import { memo } from 'react';
import { Message } from '@/types';
import { parseMessageContent } from '@/lib/utils';

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

            <div
                className="msg-bubble"
                dangerouslySetInnerHTML={{ __html: parseMessageContent(message.content) }}
            />
        </div>
    );
});
