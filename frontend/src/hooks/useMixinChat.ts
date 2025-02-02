import { useEffect, useState } from 'react';
import { useXAgent, useXChat, XStream } from '@ant-design/x';
import { useAsyncEffect, useSessionStorageState } from 'ahooks';

import { fetchSendMessage } from '@/api/chat';
import type { Action, History } from '@/api/chat/types';

const removeQuotes = (text: string) => {
  console.log(`text=${text}`);
  let result = text.trim();
  // 处理引号
  if (result.endsWith('"')) {
    result = result.slice(0, -1);
  }
  if (result.startsWith('"')) {
    result = result.slice(1);
  }

  console.log(`result=${result}`);

  return result;
};

const transformText = (text: string) => {
  text = text.replace(/\\([^n])/g, '$1'); // Remove backslashes except for \n
  text = text.replace(/\\n/g, '\n'); // Handle newlines
  return text;
};

const getTextAndActions = (words: string[]) => {
  const fullText = words.join('');
  let [text, actionsStr] = fullText.split('@@@');
  text = transformText(text);
  actionsStr = `${actionsStr.replace('[DONE]', '')}`;
  let actions;
  try {
    actions = JSON.parse(actionsStr);
    while (typeof actions === 'string') {
      actions = JSON.parse(actions);
    }
  } catch (e) {
    console.error(e);
    actions = {
      actionList: [],
    };
  }

  return {
    text,
    actions: actions?.actionList,
    agentAddr: actions?.agent_addr,
  };
};

function useMixinChat() {
  const [content, setContent] = useState('');
  const [actions, setActions] = useState<Action[]>([]);
  const [history, setHistory] = useSessionStorageState<History[] | undefined>('HISTORY', {
    defaultValue: [],
  });
  const [isFirstLoading, setIsFirstLoading] = useState(true);
  const [agentAddr, setAgentAddr] = useState('');

  const [agent] = useXAgent({
    request: async (_, { onSuccess, onUpdate }) => {
      const response = await fetchSendMessage({
        message_id: sessionStorage.getItem('MSG_ID')!,
        history: JSON.parse(sessionStorage.getItem('HISTORY')!),
        user_address: sessionStorage.getItem('USER_ADDRESS')!,
      });
      const words: string[] = [];

      for await (const chunk of XStream({
        readableStream: response.body!,
      })) {
        // 回话结束
        if (chunk.data.includes('[DONE]')) {
          const { text, actions, agentAddr } = getTextAndActions(words);
          if (agentAddr) {
            setAgentAddr(agentAddr);
          }
          setActions(actions);
          onSuccess(text);
          setHistory(prev => [...prev!, { role: 'bot', message: text, actionList: actions }]);
        }
        const scrollBox = document.querySelector('.chat-card-body');
        scrollBox?.scrollTo({ top: scrollBox.scrollHeight, behavior: 'smooth' });

        // 只移除首尾的引号
        words.push(removeQuotes(chunk.data));
        onUpdate(transformText(words.join('')).split('@@@')[0]);
      }
    },
  });

  const { onRequest, messages, setMessages } = useXChat({
    agent,
  });

  useAsyncEffect(async () => {
    const response = await fetchSendMessage({
      message_id: sessionStorage.getItem('MSG_ID')!,
      history: [],
      user_address: sessionStorage.getItem('USER_ADDRESS')!,
    });
    const words: string[] = [];

    for await (const chunk of XStream({
      readableStream: response.body!,
    })) {
      if (chunk.data.includes('[DONE]')) {
        const { text, actions } = getTextAndActions(words);
        setMessages([
          {
            id: Math.random(),
            message: text,
            status: 'success',
          },
        ]);
        setActions(actions);
        setHistory([{ role: 'bot', message: text, actionList: actions }]);
        setIsFirstLoading(false);
      } else {
        words.push(removeQuotes(chunk.data));
      }
    }
  }, []);

  useEffect(() => {
    sessionStorage.setItem('HISTORY', '[]');
  }, []);

  return {
    isFirstLoading,
    actions,
    agent,
    onRequest,
    messages,
    content,
    setContent,
    history,
    setHistory,
    agentAddr,
  };
}

export default useMixinChat;
