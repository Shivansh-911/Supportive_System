import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { MessageSquare, Sparkles } from 'lucide-react';
import Sidebar from '../../components/Sidebar/Sidebar';
import { UserBubble, AIBubble } from '../../components/MessageBubble/MessageBubble';
import MessageInput from '../../components/MessageInput/MessageInput';
import { useUserId } from '../../hooks/useUserId';
import { getSessions, getChatHistory, sendMessage } from '../../api/chat';
import type { Message } from '../../types';
import './ChatPage.scss';

export default function ChatPage() {
  const userId = useUserId();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { sessionId: sessionIdParam } = useParams<{ sessionId: string }>();
  const bottomRef = useRef<HTMLDivElement>(null);

  const activeSessionId = sessionIdParam ? parseInt(sessionIdParam, 10) : null;

  const [pendingMessage, setPendingMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { data: sessions = [], isLoading: sessionsLoading } = useQuery({
    queryKey: ['sessions', userId],
    queryFn: () => getSessions(userId),
    refetchInterval: 30000,
  });

  const { data: history = [] } = useQuery({
    queryKey: ['history', activeSessionId],
    queryFn: () => getChatHistory(activeSessionId!),
    enabled: activeSessionId !== null,
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history, pendingMessage]);

  async function handleSend(text: string) {
    setPendingMessage(text);
    setIsLoading(true);

    try {
      const res = await sendMessage({
        user_id: userId,
        question: text,
        session_id: activeSessionId,
      });

      await queryClient.invalidateQueries({ queryKey: ['sessions', userId] });
      await queryClient.invalidateQueries({ queryKey: ['history', res.session_id] });
      // Clear optimistic state BEFORE navigating so it never persists across renders
      setPendingMessage(null);
      setIsLoading(false);
      navigate(`/session/${res.session_id}`);
    } catch {
      // Keep pendingMessage visible so the user can retry; just unlock the input
      setIsLoading(false);
    }
  }

  function handleNewChat() {
    navigate('/');
  }

  const showEmpty = !activeSessionId && !pendingMessage;

  return (
    <div className="chat-page">
      <Sidebar
        sessions={sessions}
        loading={sessionsLoading}
        activeSessionId={activeSessionId}
        onSelectSession={id => navigate(`/session/${id}`)}
        onNewChat={handleNewChat}
      />

      <main className="chat-page__main">
        <div className="chat-page__messages">
          {showEmpty ? (
            <EmptyState />
          ) : (
            <>
              {(history as Message[]).map(msg => (
                <React.Fragment key={msg.request_id}>
                  <UserBubble text={msg.raw_query} time={msg.created_at} />
                  <AIBubble message={msg} />
                </React.Fragment>
              ))}

              {pendingMessage && (
                <>
                  <UserBubble text={pendingMessage} />
                  <ThinkingBubble />
                </>
              )}
            </>
          )}
          <div ref={bottomRef} />
        </div>

        <MessageInput onSend={handleSend} loading={isLoading} />
      </main>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-state__icon">
        <MessageSquare size={28} />
      </div>
      <h2 className="empty-state__title">How can I help you today?</h2>
      <p className="empty-state__sub">
        Ask anything about Publive — articles, features, workflows, or account settings.
      </p>
    </div>
  );
}

function ThinkingBubble() {
  return (
    <div className="thinking-bubble">
      <div className="thinking-bubble__avatar">
        <Sparkles size={14} />
      </div>
      <div className="thinking-bubble__card">
        <div className="thinking-bubble__dots">
          <span /><span /><span />
        </div>
      </div>
    </div>
  );
}
