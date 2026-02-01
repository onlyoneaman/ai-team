'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import { motion } from 'framer-motion';
import { User, Sparkles, Loader2, Copy, Download, Check } from 'lucide-react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { ChatMessage as ChatMessageType } from '@/lib/types';

// Dynamic import for markdown preview (client-side only)
const MarkdownPreview = dynamic(
  () => import('@uiw/react-markdown-preview').then((mod) => mod.default),
  { ssr: false }
);

interface ChatMessageProps {
  message: ChatMessageType;
  isThinking?: boolean;
}

export function ChatMessage({ message, isThinking = false }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([message.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'response.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn('flex gap-3 items-start', isUser && 'flex-row-reverse')}
    >
      {/* Avatar - fixed at top */}
      {isUser ? (
        <div className="flex items-center justify-center w-9 h-9 rounded-xl shrink-0 bg-primary">
          <User className="w-4 h-4 text-primary-foreground" />
        </div>
      ) : (
        <Image
          src="/avatar.png"
          alt="AI"
          width={36}
          height={36}
          className="rounded-xl shrink-0 mt-1"
        />
      )}

      {/* Message content */}
      <div className={cn('flex-1 min-w-0', isUser && 'flex justify-end')}>
        <div
          className={cn(
            'inline-block max-w-[85%] px-4 py-3 rounded-2xl overflow-hidden',
            isUser
              ? 'bg-primary text-primary-foreground rounded-br-lg'
              : 'bg-card border border-border rounded-bl-lg shadow-sm'
          )}
        >
          {isUser ? (
            <p className="m-0 whitespace-pre-wrap break-words text-sm">{message.content}</p>
          ) : (
            <div className="min-w-0">
              {/* Thinking indicator */}
              {isThinking && !message.content && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="w-4 h-4 animate-spin text-primary" />
                  <span className="text-sm">Agents are working...</span>
                </div>
              )}

              {/* Streaming content */}
              {message.content && message.isStreaming && (
                <div className="text-sm whitespace-pre-wrap break-words">
                  {message.content}
                  <motion.span
                    className="inline-block w-2 h-4 ml-1 bg-primary rounded-sm align-middle"
                    animate={{ opacity: [1, 0.3] }}
                    transition={{ duration: 0.6, repeat: Infinity }}
                  />
                </div>
              )}

              {/* Final content with markdown */}
              {message.content && !message.isStreaming && (
                <div className="relative">
                  {/* Copy/Download buttons - always visible at top right */}
                  <div className="flex items-center gap-1 mb-3 justify-end">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 text-muted-foreground hover:text-primary hover:bg-primary/10"
                      onClick={handleCopy}
                    >
                      {copied ? (
                        <Check className="w-3.5 h-3.5 text-emerald-500" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 text-muted-foreground hover:text-primary hover:bg-primary/10"
                      onClick={handleDownload}
                    >
                      <Download className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                  <div
                    className="markdown-body"
                    data-color-mode="light"
                  >
                    <MarkdownPreview
                      source={message.content}
                      style={{
                        backgroundColor: 'transparent',
                        fontSize: '14px',
                        lineHeight: '1.6',
                      }}
                      wrapperElement={{
                        'data-color-mode': 'light',
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
