import React, { useState } from 'react';
import { Tooltip } from 'antd';
import { ThumbsUp, ThumbsDown, Sparkles } from 'lucide-react';
import clsx from 'clsx';
import AnswerBlocks from '../AnswerBlocks/AnswerBlocks';
import SourceLinks from '../SourceLinks/SourceLinks';
import type { Message } from '../../types';
import { thumbsUp, thumbsDown } from '../../api/chat';
import './MessageBubble.scss';

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  });
}

interface UserBubbleProps {
  text: string;
  time?: string;
}

export function UserBubble({ text, time }: UserBubbleProps) {
  return (
    <div className="user-bubble-wrap">
      <div className="user-bubble">
        <p className="user-bubble__text">{text}</p>
        {time && <span className="user-bubble__time">Sent {formatTime(time)}</span>}
      </div>
    </div>
  );
}

interface AIBubbleProps {
  message: Message;
}

type FeedbackState = 'up' | 'down' | null;

export function AIBubble({ message }: AIBubbleProps) {
  const [feedback, setFeedback] = useState<FeedbackState>(
    message.feedback === 1 ? 'up' : message.feedback === -1 ? 'down' : null
  );

  async function handleFeedback(type: 'up' | 'down') {
    if (feedback === type) return;
    setFeedback(type);
    const fn = type === 'up' ? thumbsUp : thumbsDown;
    await fn({ request_id: message.request_id }).catch(() => setFeedback(null));
  }

  const { blocks, source_urls } = message.parsed_answer;

  return (
    <div className="ai-bubble">
      <div className="ai-bubble__avatar">
        <Sparkles size={14} />
      </div>
      <div className="ai-bubble__card">
        <AnswerBlocks blocks={blocks} />

        {source_urls?.length > 0 && (
          <SourceLinks urls={source_urls} />
        )}

        <div className="ai-bubble__footer">
          <div className="ai-bubble__feedback">
            <Tooltip title="Helpful">
              <button
                className={clsx('ai-bubble__fb-btn', { 'is-active': feedback === 'up' })}
                onClick={() => handleFeedback('up')}
                aria-label="Thumbs up"
              >
                <ThumbsUp size={13} />
              </button>
            </Tooltip>
            <Tooltip title="Not helpful">
              <button
                className={clsx('ai-bubble__fb-btn', { 'is-active is-down': feedback === 'down' })}
                onClick={() => handleFeedback('down')}
                aria-label="Thumbs down"
              >
                <ThumbsDown size={13} />
              </button>
            </Tooltip>
          </div>
          <span className="ai-bubble__time">Sent {formatTime(message.created_at)}</span>
        </div>
      </div>
    </div>
  );
}
