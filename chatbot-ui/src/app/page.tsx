'use client';

/**
 * GadgetBot - Main Page
 * Combines Sidebar and ChatArea components
 */

import { useState } from 'react';
import { Sidebar } from '@/components/Sidebar/Sidebar';
import { ChatArea } from '@/components/Chat/ChatArea';
import { ThemeToggle } from '@/components/UI/ThemeToggle';
import { useChat } from '@/hooks/useChat';

export default function Home() {
  const { messages, isLoading, inputValue, setInputValue, sendMessage, clearMessages } = useChat();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleSend = () => {
    if (inputValue.trim()) {
      sendMessage(inputValue);
    }
  };

  return (
    <>
      <ThemeToggle />
      <div className={`main-layout ${isSidebarOpen ? 'mobile-menu-open' : ''}`}>
        <Sidebar
          onNewChat={clearMessages}
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />
        <ChatArea
          messages={messages}
          isLoading={isLoading}
          inputValue={inputValue}
          onInputChange={setInputValue}
          onSend={handleSend}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        />
      </div>
    </>
  );
}
