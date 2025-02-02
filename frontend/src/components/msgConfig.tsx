import React from 'react';
import type { MessageArgsProps, NotificationArgsProps } from 'antd';

import Icon from '@/icons';

export type MsgType = Exclude<NotificationArgsProps['type'], undefined>;

const style: React.CSSProperties = {
  width: 20,
  height: 20,
};

const ICON_MAP: Record<MsgType, React.ReactNode> = {
  info: <Icon name="m_info" style={style} />,
  warning: <Icon name="m_warn" style={style} />,
  success: <Icon name="m_success" style={style} />,
  error: <Icon name="m_error" style={style} />,
};

const getMsgConfig = (config: MessageArgsProps) => {
  const { type = '', content, ...rest } = config;

  return {
    icon: ICON_MAP[type as MsgType],
    content,
    ...rest,
  };
};

export default getMsgConfig;
