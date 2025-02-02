import { Button, Flex } from 'antd';
import { createStyles } from 'antd-style';

import SvgIcon from '@/icons';
import { getEllipseText } from '@/utils/getEllipseText';

interface AgentAddrProps {
  address: string;
  btnClick: () => void;
}

const useStyles = createStyles(({ css }) => ({
  agentAddr: css`
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    color: #141414;

    .addr,
    .tit {
      font-weight: bold;
    }

    .addr {
      height: 24px;
      line-height: 24px;
      &:hover {
      }
    }

    .desc {
      font-size: 12px;
    }

    .agent {
      &-svg {
        width: 48px;
        height: 48px;
      }
      &-btn {
        font-size: 12px;
      }
    }
  `,
}));

const AgentAddr: React.FC<AgentAddrProps> = ({ address, btnClick }) => {
  const { styles } = useStyles();

  return (
    <Flex gap={10} align="center" className={styles.agentAddr}>
      <SvgIcon name="agent" className="agent-svg" />
      <Flex vertical className="right" gap={5}>
        <span className="tit">C-2AO</span>
        <span className="desc">Managing</span>
        {address ? (
          <a className="addr" href={`https://sepolia.basescan.org/address/${address}`} target="_blank">
            {getEllipseText(address)}
          </a>
        ) : (
          <Button size="small" className="agent-btn" onClick={btnClick}>
            Unlock Wallet
          </Button>
        )}
      </Flex>
    </Flex>
  );
};

export default AgentAddr;
