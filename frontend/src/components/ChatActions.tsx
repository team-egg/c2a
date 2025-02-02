import { Fragment, useCallback } from 'react';
import { LoginOutlined, MenuOutlined, MessageFilled, SearchOutlined } from '@ant-design/icons';
import { Button, Dropdown, Flex, Skeleton, Tooltip } from 'antd';
import { createStyles } from 'antd-style';
import { useAccount } from 'wagmi';

import DownloadFileButton from './DownloadFileButton';
import LoginButton from './LoginButton';
import TransactionButtonWrapper from './TransactionButtonWrapper';
import type { Action } from '@/api/chat/types';

interface ChatActionsProps {
  onActionClick: (action: Action, params?: unknown) => void;
  isLoading: boolean;
  actions: Action[];
  setHistory: (args: any) => void;
  onRequest: (message: string) => void;
}

const useStyles = createStyles(() => ({
  chatControllerActions: {
    display: 'flex',
    flexWrap: 'wrap',
    width: '100%',
    justifyContent: 'start',
    gap: 15,
    '.ock-bg-primary': {
      background: 'none',
    },
    '.ock-bg-secondary': {
      background: 'none',
    },
    '.chat-btn': {
      borderRadius: 40,
      height: 32,
    },
    '.chat-skeleton': {
      width: '100%',
      borderRadius: 50,
      '.chat-skeleton-image': {
        width: '100%',
        height: '32px',
        borderRadius: 8,
      },
    },
  },
  loginActionButton: {
    padding: 0,
    minWidth: 'auto',
  },
  transactionActionButton: {
    padding: 0,
    minWidth: 'auto',
  },
}));

const ICON_MAP: Record<string, React.ReactNode> = {
  Explore: <SearchOutlined />,
  'Contract-to-Action': <MessageFilled />,
  "Login & Guess why I'm here": <LoginOutlined />,
  'A Group': <MenuOutlined />,
};

const ChatActions: React.FC<ChatActionsProps> = ({ onActionClick, isLoading, actions, setHistory, onRequest }) => {
  const { styles } = useStyles();
  const { address } = useAccount();

  const onLogined = useCallback(
    (action: Action, address: string) => {
      console.log(`onLogined: ${address}`);
      const message = `Login with ${address}`;
      onActionClick(
        {
          ...action,
          message,
          label: 'Login',
        },
        {
          address,
        },
      );
    },
    [onActionClick],
  );

  const onTxSuccess = useCallback(
    (action: Action, txId: string) => {
      const message = action.message.replace('<tx_id>', txId);
      onActionClick({
        ...action,
        message,
      });
    },
    [address],
  );

  const renderButton = (action: Action) => {
    switch (action.type) {
      case 'button_login':
        return (
          <LoginButton
            key={action.label}
            className={styles.loginActionButton}
            onConnect={address => onLogined(action, address)}
          />
        );
      case 'invoke_tx':
        return (
          <TransactionButtonWrapper
            className={styles.transactionActionButton}
            key={action.label}
            buttonText={action.label}
            params={action.params}
            onSuccess={tx => onTxSuccess(action, tx)}
          />
        );
      case 'download':
        return <DownloadFileButton data={action} />;
      case 'group':
        return (
          <Dropdown
            menu={{
              items: (action.children || []).map((a, idx) => ({
                label: <Tooltip title={a.desc}>{a.label}</Tooltip>,
                key: `${a.label}-${idx}`,
                onClick: () => onActionClick(a),
              })),
            }}
          >
            <Button size="small" icon={ICON_MAP[action.label]} key={action.label}>
              {action.label}
            </Button>
          </Dropdown>
        );
      default:
        return (
          <Tooltip title={action.desc}>
            <Button size="small" icon={ICON_MAP[action.label]} key={action.label} onClick={() => onActionClick(action)}>
              {action.label}
            </Button>
          </Tooltip>
        );
    }
  };

  return (
    <Flex className={styles.chatControllerActions}>
      {isLoading ? (
        <Skeleton.Node active />
      ) : (
        actions.map(a => {
          return <Fragment key={a.label}>{renderButton(a)}</Fragment>;
        })
      )}

      {/* <Button
        onClick={() => {
          const message = 'Test Tx';
          setHistory([
            { role: 'user', label: 'Login', address: '0xdd20cC951372F4a82E9Ba429F805084180C20643', message: '' },
            { role: 'user', message },
          ]);
          onRequest(message);
        }}
      >
        Test Tx
      </Button> */}
    </Flex>
  );
};

export default ChatActions;
