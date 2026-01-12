'use client';

import { Message } from '@/types';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';

interface ChatAreaProps {
    messages: Message[];
    isLoading: boolean;
    inputValue: string;
    onInputChange: (value: string) => void;
    onSend: () => void;
    onToggleSidebar?: () => void;
}

export function ChatArea({
    messages,
    isLoading,
    inputValue,
    onInputChange,
    onSend,
    onToggleSidebar,
}: ChatAreaProps) {
    return (
        <main className="chat-area">
            <div className="mobile-header">
                <button
                    className="hamburger-btn"
                    onClick={onToggleSidebar}
                    aria-label="Menu"
                >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="3" y1="12" x2="21" y2="12"></line>
                        <line x1="3" y1="6" x2="21" y2="6"></line>
                        <line x1="3" y1="18" x2="21" y2="18"></line>
                    </svg>
                </button>
                <div className="mobile-title">GadgetBot</div>
            </div>

            <div className="chat-container">
                <MessageList messages={messages} isLoading={isLoading} />
            </div>

            <ChatInput
                value={inputValue}
                onChange={onInputChange}
                onSend={onSend}
                isLoading={isLoading}
            />
        </main>
    );
}
