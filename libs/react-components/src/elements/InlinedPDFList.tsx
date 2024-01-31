import Stack from '@mui/material/Stack';

import type { IPdfElement } from 'client-types/';

import { PDFElement } from './PDF';
import { Collapse } from 'src/Collapse';
import { HorizontalRule } from '@mui/icons-material';

interface Props {
  items: IPdfElement[];
}

const InlinedPDFList = ({ items }: Props) => (
  <Collapse defaultExpandAll={false} collapsedSize={0} expandLabel='📖'>
    <Stack spacing={1} sx={{ mt: 2 }}>
      {items.map((pdf, i) => {
        return (
          <div className="inline-pdf-container" key={i}>
            <HorizontalRule sx={{ mt: 1, mb: 1 }} />
            <div className="inline-pdf-name">{pdf.name}</div>
            <PDFElement element={pdf} />
          </div>
        );
      })}
    </Stack>
  </Collapse>
);

export { InlinedPDFList };
