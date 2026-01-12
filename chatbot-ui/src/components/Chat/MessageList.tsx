import { memo, useEffect, useRef } from 'react';
import { Message } from '@/types';
import { MessageBubble } from './MessageBubble';

interface MessageListProps {
    messages: Message[];
    isLoading: boolean;
}

export const MessageList = memo(function MessageList({ messages, isLoading }: MessageListProps) {
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const isFirstRender = useRef(true);

    // Only auto-scroll after first render (when new messages come in)
    useEffect(() => {
        if (isFirstRender.current) {
            isFirstRender.current = false;
            return;
        }
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    return (
        <div className="chat-messages">
            {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
            ))}

            {isLoading && (
                <div className="message bot">
                    <div className="msg-header">
                        <span className="msg-role">GadgetBot</span>
                    </div>
                    <div className="msg-bubble">
                        <div className="typing">
                            <div className="dot"></div>
                            <div className="dot"></div>
                        </div>
                    </div>
                </div>
            )}
            <div ref={messagesEndRef} />
        </div>
    );
});
