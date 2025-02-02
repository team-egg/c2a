import { useEffect, useState } from 'react';
import { Address, Avatar, EthBalance, Identity, Name } from '@coinbase/onchainkit/identity';
import {
  ConnectWallet,
  Wallet,
  WalletDropdown,
  WalletDropdownBasename,
  WalletDropdownDisconnect,
  WalletDropdownFundLink,
  WalletDropdownLink,
} from '@coinbase/onchainkit/wallet';
import { useAccount } from 'wagmi';

type WalletWrapperParams = {
  text?: string;
  className?: string;
};
export default function WalletWrapper({ className, text }: WalletWrapperParams) {
  const { address } = useAccount();

  useEffect(() => {
    if (address) {
      sessionStorage.setItem('USER_ADDRESS', address);
    } else {
      sessionStorage.removeItem('USER_ADDRESS');
    }
  }, [address]);

  return (
    <>
      <Wallet>
        <ConnectWallet text={text} className={className}>
          <Avatar className="h-6 w-6" />
          <Name />
        </ConnectWallet>
        <WalletDropdown>
          <Identity className="px-4 pt-3 pb-2" hasCopyAddressOnClick={true}>
            <Avatar />
            <Address />
            <EthBalance />
          </Identity>
          <WalletDropdownLink icon="wallet" href="https://wallet.coinbase.com">
            Go to Wallet Dashboard
          </WalletDropdownLink>
          <WalletDropdownFundLink />
          <WalletDropdownDisconnect />
        </WalletDropdown>
      </Wallet>
    </>
  );
}
