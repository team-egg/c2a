import type { ReactNode } from 'react';
import { OnchainKitProvider } from '@coinbase/onchainkit';
import { baseSepolia } from 'viem/chains';

import { PUBLIC_CDP_API_KEY } from '../config';

type Props = { children: ReactNode };

function OnchainProviders({ children }: Props) {
  return (
    <OnchainKitProvider
      apiKey={PUBLIC_CDP_API_KEY}
      chain={baseSepolia}
      config={{
        appearance: {
          name: 'C-2AO',
          logo: 'https://avatars.githubusercontent.com/u/1885080?s=48&v=4',
          theme: 'light',
        },
      }}
    >
      {children}
    </OnchainKitProvider>
  );
}

export default OnchainProviders;
