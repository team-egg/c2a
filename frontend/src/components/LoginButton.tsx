import { useEffect, useState } from 'react';
import { LoginOutlined } from '@ant-design/icons';
import { ConnectWallet, ConnectWalletText, Wallet } from '@coinbase/onchainkit/wallet';
import { Button } from 'antd';
import { useAccount } from 'wagmi';

type LoginButtonWrapper = {
  text?: string;
  className?: string;
  onConnect?: (address: string) => void;
};
export default function LoginButtonWrapper({ className, text, onConnect }: LoginButtonWrapper) {
  const { address } = useAccount();

  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (address && isConnected && onConnect) {
      sessionStorage.setItem('USER_ADDRESS', address);
      onConnect(address);
    }
  }, [address, isConnected]);

  const onWalletConnect = () => {
    // 这里可以保留为空，或者添加其他连接时需要的逻辑
    setIsConnected(true);
  };

  return (
    <>
      <Wallet>
        <ConnectWallet className={className} onConnect={onWalletConnect}>
          <ConnectWalletText>
            <Button icon={<LoginOutlined />}>{text || 'Login'}</Button>
          </ConnectWalletText>
          <Button icon={<LoginOutlined />} disabled>
            Logined
          </Button>
        </ConnectWallet>
      </Wallet>
    </>
  );
}
