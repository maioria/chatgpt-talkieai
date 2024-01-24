export interface AccountInfo {
  account_id: string;
  today_chat_count: number;
  total_chat_count: number;
  target_language_label: string;
}

export interface AccountSettings {
  auto_playing_voice:number;
  auto_text_shadow:number;
  auto_pronunciation:number;
  playing_voice_speed:string;
  speech_role_name_label:string;
  speech_role_name:string;
  target_language:string;
}

export interface Collect {
  id?: string | null;
  type: string;
  content: string;
  translation: string;
  message_id?: string | null;
  create_time?: string | null;
}
export interface Message {
  id?: string | null;
  content?: string | null;
  owner: boolean;
  file_name?: string | null;
  role: string | "USER" | "ASSISTANT";
  session_id?: string | null;
  auto_play?: boolean | null;
  auto_hint?: boolean | null;
  auto_pronunciation?: boolean | null;
  pronunciation?: Pronunciation | null | undefined;
}

export interface Phoneme {
  phoneme: string;
  accuracy_score: number;
}

export interface Word {
  word: string;
  accuracy_score: number;
  error_type: string;
  phonemes: Phoneme[];
}

export interface Pronunciation {
  accuracy_score: number;
  fluency_score: number;
  completeness_score: number;
  pronunciation_score: number;
  words: Word[];
}

export interface MessagePage {
  list: Message[];
  total: number;
}

export interface Session {
  id?: string;
  type?: string;
  messages: MessagePage;
}

export interface Prompt {
  text?: string;
  translateShow?: boolean;
}
