'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Separator } from '@/components/ui/separator';
import { AgentTree } from '@/components/agents/agent-tree';
import { ActivityFeed } from '@/components/agents/activity-feed';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useUIStore, useChatStore } from '@/lib/stores';

export function Sidebar() {
  const { sidebarOpen } = useUIStore();
  const { status } = useChatStore();

  const isRunning = status === 'running';

  return (
    <AnimatePresence mode="wait">
      {sidebarOpen && (
        <motion.aside
          initial={{ width: 0, opacity: 0 }}
          animate={{ width: 300, opacity: 1 }}
          exit={{ width: 0, opacity: 0 }}
          transition={{ duration: 0.2, ease: 'easeInOut' }}
          className="h-full border-r border-border bg-card flex flex-col shrink-0"
        >
          <ScrollArea className="flex-1">
            {/* When running: only Activity. When idle/complete: Agent Tree + Activity */}
            {!isRunning && (
              <>
                <AgentTree />
                <Separator />
              </>
            )}
            <ActivityFeed />
          </ScrollArea>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
