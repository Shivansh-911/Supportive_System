import React, { useState, useRef } from 'react';
import { Spin } from 'antd';
import { ArrowUp } from 'lucide-react';
import clsx from 'clsx';
import './MessageInput.scss';

interface Props {
  onSend: (text: string) => void;
  loading: boolean;
  disabled?: boolean;
}

export default function MessageInput({ onSend, loading, disabled }: Props) {
  const [value, setValue] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  function handleSend() {
    const trimmed = value.trim();
    if (!trimmed || loading) return;
    onSend(trimmed);
    setValue('');
    inputRef.current?.focus();
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  }

  const canSend = value.trim().length > 0 && !loading && !disabled;

  return (
    <div className="message-input">
      <div className={clsx('message-input__inner', { 'is-loading': loading })}>
        <input
          ref={inputRef}
          type="text"
          className="message-input__field"
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a creative prompt..."
          disabled={loading || disabled}
          autoComplete="off"
        />
        <button
          className={clsx('message-input__send', { 'is-active': canSend })}
          onClick={handleSend}
          disabled={!canSend}
          aria-label="Send"
        >
          {loading ? (
            <Spin size="small" />
          ) : (
            <ArrowUp size={16} />
          )}
        </button>
      </div>
    </div>
  );
}
