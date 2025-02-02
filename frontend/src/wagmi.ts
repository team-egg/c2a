import { useMemo } from 'react';
import { createConfig, http } from 'wagmi';
import { base, baseSepolia } from 'wagmi/chains';

export function useWagmiConfig() {
  return useMemo(() => {
    const wagmiConfig = createConfig({
      chains: [base, baseSepolia],
      multiInjectedProviderDiscovery: false,
      transports: {
        [base.id]: http(),
        [baseSepolia.id]: http(),
      },
    });
    return wagmiConfig;
  }, []);
}
