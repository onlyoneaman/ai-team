'use client';

import { useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Play,
  ArrowRight,
  Wrench,
  CheckCircle2,
  XCircle,
  Zap,
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useChatStore } from '@/lib/stores';
import { cn } from '@/lib/utils';
import type { ActivityItem, SSEEventType } from '@/lib/types';

const eventConfig: Record<SSEEventType, { icon: React.ElementType; color: string }> = {
  start: { icon: Play, color: 'bg-blue-100 text-blue-600' },
  agent_change: { icon: ArrowRight, color: 'bg-purple-100 text-purple-600' },
  tool_call: { icon: Wrench, color: 'bg-amber-100 text-amber-600' },
  tool_result: { icon: CheckCircle2, color: 'bg-emerald-100 text-emerald-600' },
  complete: { icon: Zap, color: 'bg-primary/10 text-primary' },
  error: { icon: XCircle, color: 'bg-red-100 text-red-600' },
  delta: { icon: Zap, color: 'bg-slate-100 text-slate-600' },
  artifacts_saved: { icon: CheckCircle2, color: 'bg-slate-100 text-slate-600' },
};

// Format relative time like "5s ago", "2m ago"
function formatRelativeTime(timestamp: string): string {
  const now = Date.now();
  const then = new Date(timestamp).getTime();
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);

  if (diffSec < 60) return `${diffSec}s ago`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  return `${diffHr}h ago`;
}

// Convert agent name to friendly display name
function formatAgentName(agent: string): string {
  return agent
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function ActivityItemRow({ item, isLast }: { item: ActivityItem; isLast: boolean }) {
  const config = eventConfig[item.type] || { icon: Zap, color: 'bg-slate-100 text-slate-600' };
  const Icon = config.icon;
  const [, setTick] = useState(0);

  // Update relative time every second
  useEffect(() => {
    const interval = setInterval(() => setTick(t => t + 1), 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex items-start gap-3 relative"
    >
      {/* Timeline line */}
      {!isLast && (
        <div className="absolute left-[14px] top-8 bottom-0 w-px bg-border" />
      )}

      {/* Icon */}
      <div
        className={cn(
          'flex items-center justify-center w-7 h-7 rounded-lg shrink-0 z-10',
          config.color
        )}
      >
        <Icon className="w-3.5 h-3.5" />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0 pb-4">
        <p className="text-sm text-foreground leading-snug">{item.message}</p>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-xs font-medium text-primary">{formatAgentName(item.agent)}</span>
          {/* <span className="text-xs text-muted-foreground">
            {formatRelativeTime(item.timestamp)}
          </span> */}
        </div>
      </div>
    </motion.div>
  );
}

interface ActivityFeedProps {
  className?: string;
}

export function ActivityFeed({ className }: ActivityFeedProps) {
  const { activityFeed, status } = useChatStore();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new items
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [activityFeed]);

  return (
    <div className={cn('flex flex-col', className)}>
      <h3 className="px-4 pt-4 pb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
        Activity
      </h3>
      <ScrollArea className="flex-1 px-4" ref={scrollRef}>
        {activityFeed.length === 0 ? (
          <div className="py-6 text-center">
            <p className="text-sm text-muted-foreground">
              {status === 'idle'
                ? 'Activity will show here'
                : 'Getting started...'}
            </p>
          </div>
        ) : (
          <AnimatePresence>
            {activityFeed.map((item, index) => (
              <ActivityItemRow
                key={item.id}
                item={item}
                isLast={index === activityFeed.length - 1}
              />
            ))}
          </AnimatePresence>
        )}
      </ScrollArea>
    </div>
  );
}
