'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Image from 'next/image';
import {
  Users,
  Search,
  BarChart3,
  Sparkles,
  PenTool,
  CheckCircle,
  User,
} from 'lucide-react';
import { AVATAR } from '@/lib/constants';
import { cn } from '@/lib/utils';
import { useCompanyStore, useChatStore } from '@/lib/stores';
import type { AgentStatus, AgentRole } from '@/lib/types';

const agentIcons: Record<string, React.ElementType> = {
  marketing_head: Users,
  market_researcher: Search,
  data_analyst: BarChart3,
  seo_analyst: Sparkles,
  content_creator: PenTool,
  evaluator: CheckCircle,
};

const roleColors: Record<AgentRole, string> = {
  Orchestrator: 'bg-primary',
  Lead: 'bg-blue-500',
  Worker: 'bg-slate-400',
  Reviewer: 'bg-amber-500',
};

interface AgentNodeChatProps {
  id: string;
  name: string;
  role: AgentRole;
  status: AgentStatus;
  depth?: number;
}

function AgentNodeChat({ id, name, role, status, depth = 0 }: AgentNodeChatProps) {
  const Icon = agentIcons[id] || User;
  const roleColor = roleColors[role];
  const isFounder = id === 'founder';

  return (
    <motion.div
      className={cn(
        'flex items-center gap-3 py-2.5 px-3 rounded-xl transition-all',
        status === 'idle' && 'opacity-35',
        status === 'active' && 'opacity-100 bg-primary/10',
        status === 'complete' && 'opacity-70'
      )}
      animate={status === 'active' ? { scale: [1, 1.01, 1] } : {}}
      transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
      style={{ marginLeft: depth * 20 }}
    >
      {/* Avatar/Icon */}
      <div className="relative">
        {isFounder ? (
          <motion.div
            className={cn(
              'relative rounded-xl overflow-hidden',
              status === 'active' && 'ring-2 ring-primary ring-offset-2'
            )}
            animate={status === 'active' ? { scale: [1, 1.05, 1] } : {}}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <Image
              src={status === 'active' ? AVATAR.running : AVATAR.static}
              alt="Founder"
              width={44}
              height={44}
              className={cn(
                'rounded-xl',
                status === 'idle' && 'grayscale opacity-50'
              )}
            />
          </motion.div>
        ) : (
          <motion.div
            className={cn(
              'flex items-center justify-center w-11 h-11 rounded-xl border-2',
              status === 'idle' && 'bg-muted/20 border-border/30',
              status === 'active' && 'bg-primary/15 border-primary',
              status === 'complete' && 'bg-emerald-50 border-emerald-300'
            )}
          >
            <Icon
              className={cn(
                'w-5 h-5',
                status === 'idle' && 'text-muted-foreground/30',
                status === 'active' && 'text-primary',
                status === 'complete' && 'text-emerald-600'
              )}
            />
          </motion.div>
        )}
        {status === 'active' && !isFounder && (
          <motion.div
            className="absolute inset-0 rounded-xl border-2 border-primary"
            initial={{ opacity: 0.6, scale: 1 }}
            animate={{ opacity: 0, scale: 1.3 }}
            transition={{ duration: 1.2, repeat: Infinity }}
          />
        )}
      </div>

      {/* Name and role */}
      <div className="flex-1 min-w-0">
        <p
          className={cn(
            'text-sm font-medium truncate',
            status === 'idle' && 'text-muted-foreground/40',
            status === 'active' && 'text-foreground font-semibold',
            status === 'complete' && 'text-foreground'
          )}
        >
          {name}
        </p>
        <div className="flex items-center gap-1.5 mt-0.5">
          <div className={cn('w-1.5 h-1.5 rounded-full', roleColor, status === 'idle' && 'opacity-85')} />
          <span
            className={cn(
              'text-[11px]',
              status === 'idle' && 'text-muted-foreground/30',
              status !== 'idle' && 'text-muted-foreground'
            )}
          >
            {role}
          </span>
        </div>
      </div>

      {/* Status indicator */}
      {status === 'active' && (
        <motion.div
          className="w-2 h-2 rounded-full bg-primary shrink-0"
          animate={{ opacity: [1, 0.4, 1] }}
          transition={{ duration: 0.8, repeat: Infinity }}
        />
      )}
      {status === 'complete' && (
        <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0" />
      )}
    </motion.div>
  );
}

const workingMessages = [
  "Team is collaborating...",
  "Putting heads together...",
  "Making magic happen..."
];

export function AgentTreeChat() {
  const { agents } = useCompanyStore();
  const { activeAgents } = useChatStore();
  const [messageIndex, setMessageIndex] = useState(0);

  // Rotate messages every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % workingMessages.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  if (!agents) return null;

  const { hierarchy, entry_point } = agents;

  // Recursive render
  const renderAgent = (agentId: string, depth: number = 0): React.ReactNode => {
    const agent = hierarchy[agentId];
    if (!agent) return null;

    const status: AgentStatus = activeAgents[agentId] || 'idle';

    return (
      <div key={agentId}>
        <AgentNodeChat
          id={agentId}
          name={agent.name}
          role={agent.role}
          status={status}
          depth={depth}
        />
        {agent.children.length > 0 && (
          <div className="mt-1">
            {agent.children.map((childId) => renderAgent(childId, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card border border-border rounded-2xl p-5 shadow-xl min-w-[340px] max-w-[380px]"
    >
      <div className="flex items-center gap-3 mb-4 pb-3 border-b border-border">
        <Image
          src={AVATAR.running}
          alt="Working"
          width={36}
          height={36}
          className="rounded-lg"
        />
        <div>
          <h3 className="text-sm font-semibold text-foreground">Working on it</h3>
          <div className="h-4 overflow-hidden">
            <AnimatePresence mode="wait">
              <motion.p
                key={messageIndex}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
                className="text-xs text-muted-foreground"
              >
                {workingMessages[messageIndex]}
              </motion.p>
            </AnimatePresence>
          </div>
        </div>
      </div>
      <div className="space-y-0.5">
        {renderAgent(entry_point)}
      </div>
    </motion.div>
  );
}
