import { EventSourceMessage, fetchEventSource } from '@microsoft/fetch-event-source';

export type sseReqParams = {
  url: string;
  message?: string; // 用户输入内容
  data?: Record<string, any>; // 额外属性
  conversationId?: string; // 会话ID
  controller?: AbortController;
};

export type sseCbkOpt = {
  onopen?: (response: Response) => Promise<void>;
  onmessage?: (event: EventSourceMessage) => void;
  onclose?: () => void;
  onerror?: (err: any) => number | null | undefined | void;
};

export const sseClient = (opt: sseReqParams, cbk?: sseCbkOpt) => {
  const { data, url, controller } = opt;
  let targetUrl = url;
  // 添加前缀baseUrl
  const baseUrl = import.meta.env.VITE_API_BASE;
  if (baseUrl) {
    targetUrl = targetUrl.startsWith('/') ? `${baseUrl}${targetUrl}` : `${baseUrl}/${targetUrl}`;
  }
  const { protocol, hostname, port } = window.location;
  const fullUrl = `${protocol}//${hostname}${port ? `:${port}` : ''}`;
  fetchEventSource(targetUrl, {
    headers: {
      // address: userAddress,
      audience: fullUrl,
      'Content-Type': 'application/json',
    },
    method: 'POST',
    body: JSON.stringify(data),
    openWhenHidden: true,
    signal: controller?.signal,
    ...cbk,
  });
};
