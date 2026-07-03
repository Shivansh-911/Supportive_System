import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Image } from 'antd';
import type { Block } from '../../types';
import './AnswerBlocks.scss';

interface Props {
  blocks: Block[];
}

export default function AnswerBlocks({ blocks }: Props) {
  return (
    <div className="answer-blocks">
      {blocks.map((block, i) => {
        if (block.type === 'image' && block.content) {
          return (
            <div key={i} className="answer-blocks__image-wrap">
              <Image
                src={block.content}
                alt={`Response image ${i + 1}`}
                className="answer-blocks__image"
                preview={{ maskClassName: 'answer-blocks__preview-mask' }}
              />
            </div>
          );
        }
        return (
          <div key={i} className="answer-blocks__markdown md-content">
            <ReactMarkdown>{block.content}</ReactMarkdown>
          </div>
        );
      })}
    </div>
  );
}
