import React from 'react';
import { Skeleton, Tooltip } from 'antd';
import { Plus, User } from 'lucide-react';
import clsx from 'clsx';
import type { Session } from '../../types';
import './Sidebar.scss';

function relativeTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

interface Props {
  sessions: Session[];
  loading: boolean;
  activeSessionId: number | null;
  onSelectSession: (id: number) => void;
  onNewChat: () => void;
}


export default function Sidebar({
  sessions,
  loading,
  activeSessionId,
  onSelectSession,
  onNewChat,
}: Props) {
  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar__brand">
        <span className="sidebar__brand-name">Publive</span>
        <span className="sidebar__brand-sub">Supportive System</span>
      </div>

      {/* Sessions */}
      <div className="sidebar__sessions">
        <p className="sidebar__section-label">Recent Activity</p>

        {loading ? (
          <div className="sidebar__skeleton">
            {[1, 2, 3].map(i => (
              <Skeleton key={i} active title={false} paragraph={{ rows: 1, width: '80%' }} />
            ))}
          </div>
        ) : sessions.length === 0 ? (
          <p className="sidebar__empty">No sessions yet</p>
        ) : (
          <ul className="sidebar__list">
            {sessions.map(session => (
              <li key={session.id}>
                <Tooltip title={session.title || 'Untitled'} placement="right">
                  <button
                    className={clsx('sidebar__item', {
                      'is-active': session.id === activeSessionId,
                    })}
                    onClick={() => onSelectSession(session.id)}
                  >
                    <span className="sidebar__item-title">{session.title || 'Untitled'}</span>
                    <span className="sidebar__item-time">{relativeTime(session.updated_at)}</span>
                  </button>
                </Tooltip>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Footer */}
      <div className="sidebar__footer">
        <button className="sidebar__new-chat" onClick={onNewChat}>
          <Plus size={14} />
          <span>New Chat</span>
        </button>

        <div className="sidebar__account">
          <div className="sidebar__account-avatar">
            <User size={13} />
          </div>
          <span className="sidebar__account-name">Account</span>
        </div>
      </div>
    </aside>
  );
}
