import React from 'react';
import { ClickToComponent } from 'click-to-react-component';
import ReactDOM from 'react-dom/client';

import App from './App.tsx';

import './index.css';
import 'virtual:svg-icons-register';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <>
    <ClickToComponent />
    <App />
  </>,
);
