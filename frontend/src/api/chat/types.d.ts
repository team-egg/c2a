export interface SendMessageParams {
  message_id: string;
  history: History[];
  user_address: string | undefined | null;
}

export interface History {
  role: 'bot' | 'user';
  message: string;
  actionList?: Action[];
  label?: string;
  address?: string;
}

export interface Action {
  type: 'button' | 'button_ask_contract' | 'button_login' | 'invoke_tx' | 'download' | 'group';
  params: Record<string, any>;
  label: string;
  desc: string;
  message: string;
  children?: Action[];
}
