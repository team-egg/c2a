import { useCallback, useMemo, useRef } from 'react';
import { SendOutlined } from '@ant-design/icons';
import { TransactionButton as OnchainKitTransactionButton, Transaction } from '@coinbase/onchainkit/transaction';
import type { TransactionError, TransactionResponse } from '@coinbase/onchainkit/transaction';
import { Button, message } from 'antd';
import { ContractFunctionParameters } from 'viem';

import { BASE_SEPOLIA_CHAIN_ID } from '@/constants';

interface TransactionButtonProps {
  buttonText: string;
  className?: string;
  params?: {
    address?: `0x${string}`; // 目标地址
    abi?: readonly any[]; // 合约ABI
    functionName?: string; // 合约方法名
    args?: readonly any[]; // 合约方法参数
    value?: bigint; // 交易金额
    chainId?: number;
  };
  onSuccess?: (txId: string) => void;
}

const TransactionButtonWrapper = ({ buttonText, params, className, onSuccess }: TransactionButtonProps) => {
  const hasProcessedRef = useRef(false);

  const handleError = useCallback((err: TransactionError) => {
    console.error('Transaction error:', err);
    message.error('Transaction failed');
    hasProcessedRef.current = false;
  }, []);

  const handleSuccess = useCallback((response: TransactionResponse) => {
    if (hasProcessedRef.current) return;
    console.log('Transaction successful', response);
    onSuccess?.(response.transactionReceipts[0].transactionHash);
    hasProcessedRef.current = true;
  }, []);

  const calls = useMemo(() => {
    if (!params?.address || !params?.abi || !params?.functionName || !params?.args) {
      return [];
    }
    return [
      {
        address: params?.address,
        abi: params?.abi,
        functionName: params?.functionName,
        args: params?.args,
        value: params?.value,
        chainId: params?.chainId || BASE_SEPOLIA_CHAIN_ID,
      },
    ] as unknown as ContractFunctionParameters[];
  }, [params]);

  return (
    <div className={`flex`}>
      <Transaction calls={calls} onError={handleError} onSuccess={handleSuccess}>
        {/* <Button icon={<SendOutlined />}>{buttonText}</Button> */}
        <OnchainKitTransactionButton
          className={className}
          text={<Button icon={<SendOutlined />}>{buttonText}</Button>}
          successOverride={{
            text: (
              <Button icon={<SendOutlined />} disabled>
                Success
              </Button>
            ),
          }}
          errorOverride={{
            text: <Button icon={<SendOutlined />}>Try Again</Button>,
          }}
          pendingOverride={{
            text: (
              <Button icon={<SendOutlined />} disabled>
                Pending
              </Button>
            ),
          }}
        />
      </Transaction>
    </div>
  );
};

export default TransactionButtonWrapper;
