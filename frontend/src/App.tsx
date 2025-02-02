import { ConfigProvider } from 'antd';

import OnchainProviders from './provider/OnchainProviders';

import '@coinbase/onchainkit/styles.css';

import { Global } from './config/theme';
import Home from './pages/Home';

const msgId = crypto.randomUUID();
console.log('msgId', msgId);
sessionStorage.setItem('MSG_ID', msgId);

function App() {
  return (
    <OnchainProviders>
      <ConfigProvider prefixCls="chat">
        <Global />
        <Home />
      </ConfigProvider>
    </OnchainProviders>
  );
}

export default App;
