import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import { Tooltip, IconButton } from '@mui/material';
import { Translator } from 'components/i18n';

import { useChatInteract } from '@chainlit/react-client';

import NewChatDialog from './newChatDialog';

export default function NewChatButton() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const { clear } = useChatInteract();

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleConfirm = () => {
    clear();
    navigate('/');
    handleClose();
  };

  return (
    <span>
      <Tooltip title={<Translator path="components.molecules.newChatButton.newChat" />}>
        <IconButton
          id="new-chat-button"
          // variant="outlined"
          onClick={handleClickOpen}
        >
          <RefreshIcon />
        </IconButton>
      </Tooltip>
      <NewChatDialog
        open={open}
        handleClose={handleClose}
        handleConfirm={handleConfirm}
      />
    </span>
  );
}
