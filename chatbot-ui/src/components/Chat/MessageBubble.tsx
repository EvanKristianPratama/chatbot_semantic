import { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Message } from '@/types';

interface MessageBubbleProps {
    message: Message;
}

export const MessageBubble = memo(function MessageBubble({ message }: MessageBubbleProps) {
    const isBot = message.role === 'bot';

    return (
        <div className={`message ${message.role}`}>
            {/* Bot Message Header */}
            {isBot && (
                <div className="msg-header">
                    <span className="msg-role">GadgetBot</span>
                </div>
            )}

            <div className="msg-bubble">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                </ReactMarkdown>
            </div>
        </div>
    );
});
