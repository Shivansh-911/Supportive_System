import client from './client';
import type {
  Session,
  Message,
  SendMessageRequest,
  SendMessageResponse,
  FeedbackRequest,
} from '../types';

export async function sendMessage(data: SendMessageRequest): Promise<SendMessageResponse> {
  const response = await client.post<SendMessageResponse>('/api/message/', data);
  return response.data;
}

export async function getSessions(userId: string): Promise<Session[]> {
  const response = await client.get<Session[]>('/api/all_sessions/', {
    params: { user_id: userId },
  });
  return response.data;
}

export async function getChatHistory(sessionId: number): Promise<Message[]> {
  const response = await client.get<Message[]>('/api/chat_history/', {
    params: { session_id: sessionId },
  });
  return response.data;
}

export async function thumbsUp(data: FeedbackRequest): Promise<void> {
  await client.post('/api/thumbs_up/', data);
}

export async function thumbsDown(data: FeedbackRequest): Promise<void> {
  await client.post('/api/thumbs_down/', data);
}
