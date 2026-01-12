import { memo, useRef } from 'react';

interface ChatInputProps {
    value: string;
    onChange: (value: string) => void;
    onSend: () => void;
    isLoading: boolean;
}

const SendIcon = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
    </svg>
);

export const ChatInput = memo(function ChatInput({ value, onChange, onSend, isLoading }: ChatInputProps) {
    const inputRef = useRef<HTMLInputElement>(null);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            onSend();
        }
    };

    return (
        <div className="input-area">
            <div className="input-wrapper">
                <input
                    ref={inputRef}
                    className="chat-input"
                    placeholder="Tanyakan tentang smartphone..."
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    onKeyDown={handleKeyDown}
                />
                <button
                    className="send-btn"
                    onClick={onSend}
                    disabled={!value.trim() || isLoading}
                    aria-label="Kirim pesan"
                >
                    <SendIcon />
                </button>
            </div>
        </div>
    );
});
