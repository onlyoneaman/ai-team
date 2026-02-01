// Company types
export interface Company {
  id: string;
  name: string;
}

export interface CompanyDetails {
  id: string;
  name: string;
  mission?: string;
  brand_voice?: string;
  philosophy?: string;
  target_audience?: string;
  products?: string[];
}

// Agent types
export type AgentRole = 'Orchestrator' | 'Lead' | 'Worker' | 'Reviewer';

export interface AgentNode {
  id: string;
  name: string;
  role: AgentRole;
  children: string[];
}

export interface AgentHierarchy {
  company_id: string;
  hierarchy: Record<string, AgentNode>;
  entry_point: string;
}

export type AgentStatus = 'idle' | 'active' | 'complete';

// Suggested prompts
export interface SuggestedPrompt {
  label: string;
  prompt: string;
  complexity: 'simple' | 'medium' | 'complex';
  expected_flow: string[];
}

// SSE Event types
export type SSEEventType =
  | 'start'
  | 'agent_change'
  | 'tool_call'
  | 'tool_result'
  | 'delta'
  | 'complete'
  | 'artifacts_saved'
  | 'error';

export interface SSEEvent {
  type: SSEEventType;
  timestamp: string;
  agent: string;
  // Event-specific fields
  message?: string;
  details?: string;
  tool?: string;
  content?: string;
  response?: string;
  agents_involved?: string[];
  path?: string;
  error?: string;
}

// Chat types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  isStreaming?: boolean;
}

// Run summary
export interface RunSummary {
  run_id: string;
  duration_ms: number;
  agents_involved: string[];
}

// Activity feed item
export interface ActivityItem {
  id: string;
  type: SSEEventType;
  agent: string;
  message: string;
  timestamp: string;
  tool?: string;
}

// Workflow state
export type WorkflowStatus = 'idle' | 'running' | 'complete' | 'error';
