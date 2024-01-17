import Avatar from '@mui/material/Avatar';

import { type IAvatarElement } from 'client-types/';

interface Props {
  author: string;
  initial?: string;
  bgColor?: string;
  element?: IAvatarElement;
}

const AvatarElement = ({ element, author, initial, bgColor }: Props) => {
  let avatar: JSX.Element;
  const sx = {
    width: 26,
    height: 26,
    fontSize: '0.75rem',
    mt: '-2px',
    bgcolor: element?.url ? 'transparent' : bgColor
  };
  if (element?.url) {
    avatar = <Avatar sx={sx} src={element?.url} />;
  } else if (initial) {
    avatar = <Avatar sx={sx}>{initial?.toUpperCase()}</Avatar>;
  } else {
    avatar = <Avatar sx={sx}>{author[0]?.toUpperCase()}</Avatar>;
  }
  return <span className={`message-avatar`}>{avatar}</span>;
};

export { AvatarElement };
