import React from 'react';
import { ExternalLink } from 'lucide-react';
import './SourceLinks.scss';

interface Props {
  urls: string[];
}

function getDisplayLabel(url: string, index: number): string {
  try {
    const parsed = new URL(url);
    return parsed.hostname.replace(/^www\./, '');
  } catch {
    return `Source ${index + 1}`;
  }
}

export default function SourceLinks({ urls }: Props) {
  if (!urls.length) return null;

  return (
    <div className="source-links">
      <span className="source-links__label">Sources</span>
      <div className="source-links__list">
        {urls.map((url, i) => (
          <a
            key={url}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="source-links__tag"
          >
            <ExternalLink size={11} />
            <span>{getDisplayLabel(url, i)}</span>
          </a>
        ))}
      </div>
    </div>
  );
}
