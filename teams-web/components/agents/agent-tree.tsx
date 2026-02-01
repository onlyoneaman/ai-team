'use client';

import { AgentNode } from './agent-node';
import { Skeleton } from '@/components/ui/skeleton';
import { useCompanyStore, useChatStore } from '@/lib/stores';
import type { AgentStatus } from '@/lib/types';

interface AgentTreeProps {
  className?: string;
}

export function AgentTree({ className }: AgentTreeProps) {
  const { agents, isLoadingDetails } = useCompanyStore();
  const { activeAgents } = useChatStore();

  if (isLoadingDetails || !agents) {
    return (
      <div className={className}>
        <div className="space-y-3 p-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-center gap-3">
              <Skeleton className="w-9 h-9 rounded-xl" />
              <div className="space-y-1.5">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-3 w-14" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const { hierarchy, entry_point } = agents;

  // Recursive render function
  const renderAgent = (agentId: string, depth: number = 0): React.ReactNode => {
    const agent = hierarchy[agentId];
    if (!agent) return null;

    const status: AgentStatus = activeAgents[agentId] || 'idle';

    return (
      <div key={agentId}>
        <AgentNode
          id={agentId}
          name={agent.name}
          role={agent.role}
          status={status}
          depth={depth}
        />
        {agent.children.length > 0 && (
          <div>
            {agent.children.map((childId) =>
              renderAgent(childId, depth + 1)
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={className}>
      <div className="p-4">
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
          Agent Team
        </h3>
        <div className="space-y-0.5">
          {renderAgent(entry_point)}
        </div>
      </div>
    </div>
  );
}
