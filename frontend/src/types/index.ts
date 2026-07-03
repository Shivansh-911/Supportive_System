export interface Session {
  id: number;
  title: string | null;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export type BlockType = 'markdown' | 'image';

export interface Block {
  type: BlockType;
  content: string;
}

export interface ParsedAnswer {
  blocks: Block[];
  source_urls: string[];
}

export interface Message {
  request_id: string;
  raw_query: string;
  parsed_answer: ParsedAnswer;
  created_at: string;
  feedback?: number | null;
}

export interface SendMessageRequest {
  user_id: string;
  question: string;
  session_id?: number | null;
}

export interface SendMessageResponse {
  session_id: number;
  session_title: string;
  request_id: string;
  answer: ParsedAnswer;
  intent: string;
  is_follow_up: boolean;
}

export interface FeedbackRequest {
  request_id: string;
}
