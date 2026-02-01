'use client';

import { useRef, useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2 } from 'lucide-react';
import Image from 'next/image';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ChatMessage } from './chat-message';
import { AgentTreeChat } from '@/components/agents/agent-tree-chat';
import { useChatStore, useCompanyStore, useUIStore } from '@/lib/stores';
import { cn } from '@/lib/utils';

export function ChatArea() {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const { userMessage, assistantMessage, status, error, submitTask } = useChatStore();
  const { companyDetails, selectedCompanyId, suggestedPrompts, isLoadingDetails } = useCompanyStore();
  const { setIsTyping, isTyping } = useUIStore();

  const isEmpty = !userMessage && !assistantMessage;
  const isRunning = status === 'running';
  const canSubmit = input.trim() && selectedCompanyId && !isRunning;

  // Handle typing state with debounce
  const handleInputChange = useCallback((value: string) => {
    setInput(value);
    setIsTyping(true);

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Set new timeout to reset typing state
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
    }, 250);
  }, [setIsTyping]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  // Auto-scroll on new content
  useEffect(() => {
    if (scrollRef.current && !isEmpty) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [userMessage, assistantMessage?.content, isEmpty]);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSubmit = () => {
    if (!canSubmit) return;
    submitTask(selectedCompanyId!, input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handlePromptClick = (prompt: string) => {
    setInput(prompt);
    textareaRef.current?.focus();
  };

  // Empty state - centered welcome with input
  if (isEmpty) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-2xl"
        >
          {/* Welcome Header */}
          <div className="text-center mb-8">
            <div className="inline-block mb-4">
              <Image
                src={isTyping ? '/avatar-thinking.png' : '/avatar.png'}
                alt="AI Assistant"
                width={100}
                height={100}
                className="rounded-2xl transition-all"
              />
            </div>
            <h1 className="text-2xl font-bold text-foreground mb-2">
              How can I help you today?
            </h1>
            <p className="text-muted-foreground max-w-md mx-auto">
              Tell me what you need and I'll get the team on it.
            </p>
          </div>

          {/* Input Area */}
          <div className="relative">
            <div className="flex items-end gap-3 p-2 bg-card rounded-2xl border border-border shadow-sm">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => handleInputChange(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  isLoadingDetails
                    ? 'Loading...'
                    : 'What would you like to work on?'
                }
                disabled={isRunning || isLoadingDetails}
                rows={1}
                className={cn(
                  'flex-1 resize-none bg-transparent px-4 py-3',
                  'text-base placeholder:text-muted-foreground',
                  'focus:outline-none',
                  'disabled:cursor-not-allowed disabled:opacity-50',
                  'min-h-[48px] max-h-[120px]'
                )}
              />
              <Button
                onClick={handleSubmit}
                disabled={!canSubmit}
                size="icon"
                className="h-12 w-12 rounded-xl shrink-0 bg-primary hover:bg-primary/90"
              >
                {isRunning ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </Button>
            </div>
          </div>

          {/* Suggested Prompts - Below Input */}
          {suggestedPrompts.length > 0 && (
            <div className="mt-4">
              <p className="text-xs font-medium text-muted-foreground mb-3 text-center">
                Try a suggested task
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {suggestedPrompts.slice(0, 4).map((prompt, index) => (
                  <Badge
                    key={index}
                    variant="outline"
                    className="cursor-pointer hover:bg-secondary hover:border-primary/30 transition-all py-2 px-4 text-sm font-normal"
                    onClick={() => handlePromptClick(prompt.prompt)}
                  >
                    {prompt.label}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      </div>
    );
  }

  // Active task - show Agent Tree when running, response when complete
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <ScrollArea className="flex-1" ref={scrollRef}>
        <div className="max-w-3xl mx-auto px-4 py-6">
          <div className="space-y-6">
            {/* User message */}
            {userMessage && <ChatMessage message={userMessage} />}

            {/* When running: show Agent Tree visualization */}
            {isRunning && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-center py-8"
              >
                <AgentTreeChat />
              </motion.div>
            )}

            {/* When complete: show assistant message */}
            {!isRunning && assistantMessage && assistantMessage.content && (
              <ChatMessage message={assistantMessage} />
            )}

            {/* Error state */}
            {status === 'error' && error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="px-4 py-3 bg-destructive/10 border border-destructive/20 rounded-xl text-sm text-destructive"
              >
                {error}
              </motion.div>
            )}
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}
