from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from chainlit.context import context_var
from chainlit.element import Text
from chainlit.step import Step, StepType
from literalai import ChatGeneration, CompletionGeneration, GenerationMessage
from llama_index.callbacks import TokenCountingHandler
from llama_index.callbacks.schema import CBEventType, EventPayload
from llama_index.llms.base import ChatMessage, ChatResponse, CompletionResponse

DEFAULT_IGNORE = [
    CBEventType.CHUNKING,
    CBEventType.SYNTHESIZE,
    CBEventType.EMBEDDING,
    CBEventType.NODE_PARSING,
    CBEventType.QUERY,
    CBEventType.TREE,
]


class LlamaIndexCallbackHandler(TokenCountingHandler):
    """Base callback handler that can be used to track event starts and ends."""

    steps: Dict[str, Step]

    def __init__(
        self,
        event_starts_to_ignore: List[CBEventType] = DEFAULT_IGNORE,
        event_ends_to_ignore: List[CBEventType] = DEFAULT_IGNORE,
    ) -> None:
        """Initialize the base callback handler."""
        super().__init__(
            event_starts_to_ignore=event_starts_to_ignore,
            event_ends_to_ignore=event_ends_to_ignore,
        )
        self.context = context_var.get()

        self.steps = {}

    def _get_parent_id(self, event_parent_id: Optional[str] = None) -> Optional[str]:
        if event_parent_id and event_parent_id in self.steps:
            return event_parent_id
        elif self.context.current_step:
            return self.context.current_step.id
        elif self.context.session.root_message:
            return self.context.session.root_message.id
        else:
            return None

    def _restore_context(self) -> None:
        """Restore Chainlit context in the current thread

        Chainlit context is local to the main thread, and LlamaIndex
        runs the callbacks in its own threads, so they don't have a
        Chainlit context by default.

        This method restores the context in which the callback handler
        has been created (it's always created in the main thread), so
        that we can actually send messages.
        """
        context_var.set(self.context)

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        """Run when an event starts and return id of event."""
        self._restore_context()
        step_type: StepType = "undefined"
        if event_type == CBEventType.RETRIEVE:
            step_type = "retrieval"
        elif event_type == CBEventType.LLM:
            step_type = "llm"
        else:
            return event_id

        step = Step(
            name=event_type.value,
            type=step_type,
            parent_id=self._get_parent_id(parent_id),
            id=event_id,
            disable_feedback=False,
        )
        self.steps[event_id] = step
        step.start = datetime.utcnow().isoformat()
        step.input = payload or {}
        self.context.loop.create_task(step.send())
        return event_id

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        """Run when an event ends."""
        step = self.steps.get(event_id, None)

        if payload is None or step is None:
            return

        self._restore_context()

        step.end = datetime.utcnow().isoformat()

        if event_type == CBEventType.RETRIEVE:
            sources = payload.get(EventPayload.NODES)
            if sources:

                def truncate(s, m):
                    return s if len(s) <= m else s[:m].rsplit(" ", 1)[0] + "..."

                def fix_markdown(s):
                    return s.replace("|", "&#124;").replace("\n", "<br>")

                source_refs = (
                    "|مصدر|اسم الملف|صفحة|النقاط المحرزة|معاينة المحتوى|\n|---|---|---|---|---|\n"
                    + "\n".join(
                        (
                            f"| مصدر {i} |"
                            f" {source.node.metadata.get('file_name')} |"
                            f" {source.node.metadata.get('page_label', '')} |"
                            f" {source.score:.4f} |"
                            f" {fix_markdown(truncate(source.node.get_text(), 150))} |"
                        )
                        for i, source in enumerate(sources)
                    )
                )
                step.elements = [
                    Text(
                        name=f"مصدر {i}",
                        content=source.node.get_text() or ":warning: فارغ",
                    )
                    for i, source in enumerate(sources)
                ]

                def histogram(data, bins=10, char="┼", header="") -> str:
                    counts, bin_edges = np.histogram(data, bins=bins)
                    max_count = max(counts)
                    # Normalize counts to scale with the character count
                    normalized_counts = [
                        int((count / max_count) * len(data)) for count in counts
                    ]
                    # Build histogram string
                    histogram_str = header
                    for i, count in enumerate(normalized_counts):
                        bin_label = f"{bin_edges[i]:.4f} - {bin_edges[i+1]:.4f}"
                        line = f"{bin_label}: {char * count}\n"
                        histogram_str += line
                    return histogram_str

                text_histogram = histogram(
                    [s.score for s in sources], header="### توزيع النقاط المحرزة\n"
                )
                step.output = f"### المصادر\n{source_refs}\n\n" + text_histogram
            self.context.loop.create_task(step.update())

        if event_type == CBEventType.LLM:
            formatted_messages = payload.get(
                EventPayload.MESSAGES
            )  # type: Optional[List[ChatMessage]]
            formatted_prompt = payload.get(EventPayload.PROMPT)
            response = payload.get(EventPayload.RESPONSE)

            if formatted_messages:
                messages = [
                    GenerationMessage(
                        role=m.role.value, content=m.content or ""  # type: ignore
                    )
                    for m in formatted_messages
                ]
            else:
                messages = None

            if isinstance(response, ChatResponse):
                content = response.message.content or ""
            elif isinstance(response, CompletionResponse):
                content = response.text
            else:
                content = ""

            step.output = content

            token_count = self.total_llm_token_count or None

            if messages and isinstance(response, ChatResponse):
                msg: ChatMessage = response.message
                step.generation = ChatGeneration(
                    messages=messages,
                    message_completion=GenerationMessage(
                        role=msg.role.value,  # type: ignore
                        content=content,
                    ),
                    token_count=token_count,
                )
            elif formatted_prompt:
                step.generation = CompletionGeneration(
                    prompt=formatted_prompt,
                    completion=content,
                    token_count=token_count,
                )

            self.context.loop.create_task(step.update())

        self.steps.pop(event_id, None)

    def _noop(self, *args, **kwargs):
        pass

    start_trace = _noop
    end_trace = _noop
