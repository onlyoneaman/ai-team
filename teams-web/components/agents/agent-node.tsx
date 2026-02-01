'use client';

import { motion } from 'framer-motion';
import Image from 'next/image';
import {
  User,
  Users,
  Search,
  BarChart3,
  Sparkles,
  PenTool,
  CheckCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { AgentStatus, AgentRole } from '@/lib/types';

interface AgentNodeProps {
  id: string;
  name: string;
  role: AgentRole;
  status: AgentStatus;
  isLast?: boolean;
  depth?: number;
}

const agentIcons: Record<string, React.ElementType> = {
  marketing_head: Users,
  market_researcher: Search,
  data_analyst: BarChart3,
  seo_analyst: Sparkles,
  content_creator: PenTool,
  evaluator: CheckCircle,
};

const roleStyles: Record<AgentRole, { bg: string; text: string; border: string }> = {
  Orchestrator: { bg: 'bg-primary/10', text: 'text-primary', border: 'border-primary/20' },
  Lead: { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-200' },
  Worker: { bg: 'bg-slate-50', text: 'text-slate-600', border: 'border-slate-200' },
  Reviewer: { bg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-200' },
};

export function AgentNode({
  id,
  name,
  role,
  status,
  depth = 0,
}: AgentNodeProps) {
  const Icon = agentIcons[id] || User;
  const roleStyle = roleStyles[role];
  const isFounder = id === 'founder';

  return (
    <motion.div
      className={cn(
        'flex items-center gap-3 py-2 px-2 rounded-lg transition-all',
        status === 'idle' && 'opacity-40',
        status === 'active' && 'opacity-100 bg-primary/5',
        status === 'complete' && 'opacity-70'
      )}
      animate={status === 'active' ? { opacity: 1 } : {}}
    >
      {/* Indent for depth */}
      {depth > 0 && (
        <div style={{ width: depth * 16 }} className="shrink-0" />
      )}

      {/* Avatar for founder, Icon for others */}
      {isFounder ? (
        <motion.div
          className={cn(
            'relative rounded-xl overflow-hidden',
            status === 'active' && 'ring-2 ring-primary ring-offset-1'
          )}
          animate={status === 'active' ? { scale: [1, 1.05, 1] } : {}}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <Image
            src={status === 'active' ? '/avatar-thinking.png' : '/avatar.png'}
            alt="Founder"
            width={40}
            height={40}
            className={cn(
              'rounded-xl',
              status === 'idle' && 'grayscale opacity-60'
            )}
          />
        </motion.div>
      ) : (
        <motion.div
          className={cn(
            'relative flex items-center justify-center w-10 h-10 rounded-xl border-2',
            status === 'idle' && 'bg-muted/50 border-border/50',
            status === 'active' && 'bg-primary/15 border-primary shadow-md shadow-primary/20',
            status === 'complete' && 'bg-emerald-50 border-emerald-300'
          )}
          animate={status === 'active' ? { scale: [1, 1.05, 1] } : {}}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <Icon
            className={cn(
              'w-5 h-5',
              status === 'idle' && 'text-muted-foreground/60',
              status === 'active' && 'text-primary',
              status === 'complete' && 'text-emerald-600'
            )}
          />
          {status === 'active' && (
            <motion.div
              className="absolute inset-0 rounded-xl border-2 border-primary"
              initial={{ opacity: 0.8, scale: 1 }}
              animate={{ opacity: 0, scale: 1.5 }}
              transition={{ duration: 1, repeat: Infinity }}
            />
          )}
        </motion.div>
      )}

      {/* Name and Role */}
      <div className="flex-1 min-w-0">
        <p
          className={cn(
            'text-sm font-medium truncate',
            status === 'idle' && 'text-muted-foreground/70',
            status === 'active' && 'text-foreground font-semibold',
            status === 'complete' && 'text-foreground'
          )}
        >
          {name}
        </p>
        <span
          className={cn(
            'inline-block px-2 py-0.5 text-[10px] font-medium rounded-md border',
            status === 'idle' && 'opacity-60',
            roleStyle.bg,
            roleStyle.text,
            roleStyle.border
          )}
        >
          {role}
        </span>
      </div>
    </motion.div>
  );
}
