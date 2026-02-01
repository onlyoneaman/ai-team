'use client';

import { motion } from 'framer-motion';
import { Clock, Users, RotateCcw, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useChatStore } from '@/lib/stores';

export function RunSummary() {
  const { runSummary, status, resetWorkspace } = useChatStore();

  if (status !== 'complete' || !runSummary) return null;

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    const seconds = Math.floor(ms / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center justify-between gap-4 px-4 py-3 mt-4 bg-secondary/50 rounded-xl border border-border"
    >
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 text-emerald-600">
          <CheckCircle className="w-4 h-4" />
          <span className="text-sm font-medium">Complete</span>
        </div>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          {runSummary.duration_ms > 0 && (
            <div className="flex items-center gap-1.5">
              <Clock className="w-4 h-4" />
              <span>{formatDuration(runSummary.duration_ms)}</span>
            </div>
          )}
          <div className="flex items-center gap-1.5">
            <Users className="w-4 h-4" />
            <span>{runSummary.agents_involved.length} agents</span>
          </div>
        </div>
      </div>

      <Button
        variant="outline"
        size="sm"
        onClick={resetWorkspace}
        className="gap-1.5 rounded-lg"
      >
        <RotateCcw className="w-3.5 h-3.5" />
        New Task
      </Button>
    </motion.div>
  );
}
