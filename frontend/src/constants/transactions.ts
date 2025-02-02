import { erc20Abi } from 'viem';

import { mintABI, mintContractAddress } from '../constants';

export const TRANSACTION_CONFIGS = {
  mint: (address: string) => ({
    calls: [
      {
        address: mintContractAddress,
        abi: mintABI,
        functionName: 'mint',
        args: [address],
      },
    ],
    buttonText: 'Test Mint',
  }),

  transferNative: {
    calls: [
      {
        to: '0x9AC7421Bb573cB84709764D0D8AB1cE759416496',
        data: '0x',
        value: BigInt(1000000000000000), // 0.001 ETH in wei
      },
    ],
    buttonText: 'Test Transfer Native',
  },

  transferErc20: {
    calls: [
      {
        address: '0xdd20cC951372F4a82E9Ba429F805084180C20643',
        abi: erc20Abi,
        functionName: 'transfer',
        args: ['0xF0110D0fa36101990C12B65e292940dC4B8D2b82', BigInt(1000000000000000000)],
      },
    ],
    buttonText: 'Test Transfer ERC20',
  },
};
