import { useState } from 'react';

const USER_ID_KEY = 'pss_user_id';

function getOrCreateUserId(): string {
  const existing = localStorage.getItem(USER_ID_KEY);
  if (existing) return existing;
  const newId = crypto.randomUUID();
  localStorage.setItem(USER_ID_KEY, newId);
  return newId;
}

export function useUserId(): string {
  const [userId] = useState<string>(getOrCreateUserId);
  return userId;
}
