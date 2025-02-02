import { SendMessageParams } from './types';

export const fetchSendMessage = (params: SendMessageParams) => {
  return fetch(`${import.meta.env.VITE_BASE_URL}/message`, {
    method: 'POST',
    body: JSON.stringify(params),
    headers: {
      'Content-Type': 'application/json',
    },
  });
};
