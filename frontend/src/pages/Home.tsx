import { UserOutlined } from '@ant-design/icons';
import { Bubble, Sender } from '@ant-design/x';
import { useBoolean } from 'ahooks';
import { Card, Flex, GetProp, message } from 'antd';

import md from '@/utils/initMd';

import 'highlight.js/styles/github.css';

import useStyle from './styles';
import type { Action } from '@/api/chat/types';
import AgentAddr from '@/components/AgentAddr';
import ChatActions from '@/components/ChatActions';
import ContractAnalysisModal from '@/components/ContractAnalysisModal';
import HeaderLoginButton from '@/components/HeaderLoginButton';
import useMixinChat from '@/hooks/useMixinChat';

const ROLES: GetProp<typeof Bubble.List, 'roles'> = {
  ai: {
    placement: 'start',
    avatar: { icon: <UserOutlined />, style: { background: '#fde3cf' } },
  },
  local: {
    placement: 'end',
    avatar: { icon: <UserOutlined />, style: { background: '#87d068' } },
  },
};

const Home: React.FC = () => {
  const { styles } = useStyle();

  const { agent, onRequest, messages, content, setContent, actions, isFirstLoading, setHistory, agentAddr } =
    useMixinChat();
  const [analysisModalOpen, { setTrue: openAnalysisModal, setFalse: closeAnalysisModal }] = useBoolean(false);

  const handleActionClick = ({ type, message, label }: Action, otherParams?: any) => {
    if (type === 'button_ask_contract') {
      // todo 这里如果用easy-modal就可以实现传参了
      openAnalysisModal();
      return;
    } else {
      console.log(`type: ${type}, message: ${message}`);
      setHistory(prev => [...prev!, { role: 'user', message, label, ...(otherParams || {}) }]);
      onRequest(message);
    }
  };

  /**
   * 提交合约分析
   * @param contractAddress 合约地址
   * @param network 网络
   */
  const submitContractAnalysis = (contractAddress: string, chainName: string) => {
    console.log(`contractAddress = ${contractAddress}, network = ${chainName}`);
    // 从action里拿到message，然后替换关键字，然后调用接口
    const action = actions.find(action => action.type === 'button_ask_contract');
    if (!action) {
      message.error('No action found');
      return;
    }
    const newMessage = action.message.replace('<contract_address>', contractAddress).replace('<network_id>', chainName);
    console.log(`newMessage = ${newMessage}`);
    setHistory(prev => [...prev!, { role: 'user', message: newMessage, label: action.label }]);
    onRequest(newMessage);
    closeAnalysisModal();
  };

  const handleUnlockWallet = () => {
    const UN_LOCK_MESSAGE = 'I want to unlock the wallet.';
    setHistory(prev => [...prev!, { role: 'user', message: UN_LOCK_MESSAGE, label: 'Unlock' }]);
    onRequest(UN_LOCK_MESSAGE);
  };

  return (
    <>
      <Flex className={styles.wrapper} vertical gap={20}>
        <Flex vertical gap={20} className="chat">
          <Flex className="chat-wallet" justify="space-between" align="center">
            <AgentAddr address={agentAddr} btnClick={handleUnlockWallet} />
            <HeaderLoginButton />
          </Flex>
          <div className="chat-container">
            {/* 临时：502 -> 450 + 32 + 20 */}
            <Card
              title="Contract2Action"
              styles={{ body: { height: actions.length > 0 || isFirstLoading ? 450 : 502 } }}
            >
              <Flex gap="middle" vertical>
                <Bubble.List
                  roles={ROLES}
                  items={messages.map(({ id, message, status }) => ({
                    key: id,
                    role: status === 'local' ? 'local' : 'ai',
                    content: (
                      <div
                        className="markdown-body"
                        dangerouslySetInnerHTML={{
                          __html: md.render(message),
                        }}
                      />
                    ),
                  }))}
                />
              </Flex>
            </Card>
            <Flex vertical align="center" className="chat-controller" gap={20}>
              <ChatActions
                onActionClick={handleActionClick}
                isLoading={isFirstLoading}
                actions={actions}
                setHistory={setHistory}
                onRequest={onRequest}
              />
              <Sender
                loading={agent.isRequesting()}
                value={content}
                onChange={setContent}
                onSubmit={nextContent => {
                  setHistory(prev => [...prev!, { role: 'user', message: nextContent }]);
                  onRequest(nextContent);
                  setContent('');
                }}
              />
            </Flex>
          </div>
          <p className="powered-by">Powered by OnchainKit @Coinbase</p>
        </Flex>
        <ContractAnalysisModal
          isOpen={analysisModalOpen}
          onClose={() => {
            closeAnalysisModal();
          }}
          onSubmit={submitContractAnalysis}
        />
      </Flex>
    </>
  );
};

export default Home;
