'use client';

import { PanelLeft, Plus } from 'lucide-react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { CompanySelector } from '@/components/company/company-selector';
import { useUIStore, useChatStore } from '@/lib/stores';
import { cn } from '@/lib/utils';

import { AVATAR } from '@/lib/constants';

export function Header() {
  const { sidebarOpen, toggleSidebar, currentView, setView, isTyping } = useUIStore();
  const { status, resetWorkspace } = useChatStore();

  const isTaskComplete = status === 'complete' || status === 'error';
  const isRunning = status === 'running';

  return (
    <header className="h-14 border-b border-border bg-card/80 backdrop-blur-sm flex items-center justify-between px-4 sticky top-0 z-50">
      <div className="flex items-center gap-3">
        {/* Sidebar Toggle - always available in workspace view */}
        {currentView === 'workspace' && (
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="h-8 w-8 text-muted-foreground hover:text-primary hover:bg-primary/10"
          >
            <PanelLeft className={cn('h-4 w-4 transition-transform', sidebarOpen && 'rotate-180')} />
          </Button>
        )}

        {/* Logo with Avatar - clickable to start new chat */}
        <button
          onClick={resetWorkspace}
          className="flex items-center gap-2.5 px-2 py-1 -ml-2 rounded-lg transition-colors hover:bg-primary/10"
        >
          <Image
            src={isTyping || isRunning ? AVATAR.running : AVATAR.static}
            alt="Teams AI"
            width={32}
            height={32}
            className="rounded-lg"
          />
          <span className="font-semibold text-foreground tracking-tight hover:text-primary transition-colors">Teams AI</span>
        </button>
      </div>

      <div className="flex items-center gap-3">
        {/* New Task Button - show when task is complete */}
        {isTaskComplete && (
          <Button
            onClick={resetWorkspace}
            size="sm"
            className="gap-1.5 rounded-lg"
          >
            <Plus className="w-4 h-4" />
            New Task
          </Button>
        )}

        {/* View Toggle */}
        <div className="flex items-center bg-muted rounded-lg p-1">
          <button
            onClick={() => setView('workspace')}
            className={cn(
              'px-4 py-1.5 text-sm font-medium rounded-md transition-all',
              currentView === 'workspace'
                ? 'bg-card text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            )}
          >
            Workspace
          </button>
          <button
            onClick={() => setView('company-profile')}
            className={cn(
              'px-4 py-1.5 text-sm font-medium rounded-md transition-all',
              currentView === 'company-profile'
                ? 'bg-card text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            )}
          >
            Profile
          </button>
        </div>

        {/* Company Selector */}
        <CompanySelector />
      </div>
    </header>
  );
}
