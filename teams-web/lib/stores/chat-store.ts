import { create } from 'zustand';
import type {
  ChatMessage,
  SSEEvent,
  ActivityItem,
  RunSummary,
  WorkflowStatus,
  AgentStatus,
} from '../types';
import { streamChat } from '../api';

interface ChatState {
  // Messages
  userMessage: ChatMessage | null;
  assistantMessage: ChatMessage | null;

  // Workflow state
  status: WorkflowStatus;
  activeAgents: Record<string, AgentStatus>;
  activityFeed: ActivityItem[];
  runSummary: RunSummary | null;

  // Error
  error: string | null;

  // Streaming controller
  abortController: AbortController | null;

  // Actions
  submitTask: (companyId: string, message: string) => void;
  cancelTask: () => void;
  resetWorkspace: () => void;
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

// Convert snake_case to Title Case
function toTitleCase(str: string): string {
  return str
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function createActivityItem(event: SSEEvent): ActivityItem {
  let message = '';
  switch (event.type) {
    case 'start':
      message = 'Starting...';
      break;
    case 'agent_change':
      // Format: "Marketing Head activated"
      message = `${toTitleCase(event.agent)} activated`;
      break;
    case 'tool_call': {
      // Format: "Transfer to Marketing Head" or "Get SEO Data"
      const toolName = toTitleCase(event.tool || 'tool');
      message = toolName;
      break;
    }
    case 'tool_result':
      message = 'Done';
      break;
    case 'complete':
      message = 'Complete';
      break;
    case 'error':
      message = event.error || 'Something went wrong';
      break;
    default:
      message = event.details || event.type;
  }

  return {
    id: generateId(),
    type: event.type,
    agent: event.agent,
    message,
    timestamp: event.timestamp,
    tool: event.tool,
  };
}

export const useChatStore = create<ChatState>()((set, get) => ({
  // Initial state
  userMessage: null,
  assistantMessage: null,
  status: 'idle',
  activeAgents: {},
  activityFeed: [],
  runSummary: null,
  error: null,
  abortController: null,

  // Submit a task to the AI workforce
  submitTask: (companyId: string, message: string) => {
    const { status } = get();
    if (status === 'running') return;

    // Reset and set user message
    const userMsg: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    const assistantMsg: ChatMessage = {
      id: generateId(),
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      isStreaming: true,
    };

    set({
      userMessage: userMsg,
      assistantMessage: assistantMsg,
      status: 'running',
      activeAgents: { founder: 'active' },
      activityFeed: [],
      runSummary: null,
      error: null,
    });

    // Start streaming
    const controller = streamChat({
      companyId,
      message,
      onEvent: (event) => {
        const state = get();

        // Update activity feed for relevant events
        if (['start', 'agent_change', 'tool_call', 'tool_result', 'complete', 'error'].includes(event.type)) {
          const activityItem = createActivityItem(event);
          set({ activityFeed: [...state.activityFeed, activityItem] });
        }

        // Handle specific event types
        switch (event.type) {
          case 'agent_change': {
            // Mark previous active agents as complete, new one as active
            const newActiveAgents = { ...state.activeAgents };
            Object.keys(newActiveAgents).forEach((key) => {
              if (newActiveAgents[key] === 'active') {
                newActiveAgents[key] = 'complete';
              }
            });
            newActiveAgents[event.agent] = 'active';
            set({ activeAgents: newActiveAgents });
            break;
          }

          case 'delta': {
            // Don't stream intermediate content during agent work
            // We'll show the full response on complete
            break;
          }

          case 'complete': {
            // Mark all agents as complete and set final response
            const finalAgents = { ...state.activeAgents };
            Object.keys(finalAgents).forEach((key) => {
              finalAgents[key] = 'complete';
            });

            set({
              activeAgents: finalAgents,
              status: 'complete',
              assistantMessage: state.assistantMessage
                ? {
                    ...state.assistantMessage,
                    content: event.response || state.assistantMessage.content,
                    isStreaming: false,
                  }
                : null,
              runSummary: {
                run_id: generateId(),
                duration_ms: 0, // Will be calculated from timestamps
                agents_involved: event.agents_involved || [],
              },
            });
            break;
          }

          case 'error': {
            set({
              status: 'error',
              error: event.error || 'An unknown error occurred',
              assistantMessage: state.assistantMessage
                ? { ...state.assistantMessage, isStreaming: false }
                : null,
            });
            break;
          }
        }
      },
      onError: (error) => {
        set({
          status: 'error',
          error: error.message,
          assistantMessage: get().assistantMessage
            ? { ...get().assistantMessage!, isStreaming: false }
            : null,
        });
      },
      onComplete: () => {
        set({ abortController: null });
      },
    });

    set({ abortController: controller });
  },

  // Cancel current task
  cancelTask: () => {
    const { abortController } = get();
    if (abortController) {
      abortController.abort();
      set({
        status: 'idle',
        abortController: null,
        assistantMessage: get().assistantMessage
          ? { ...get().assistantMessage!, isStreaming: false }
          : null,
      });
    }
  },

  // Reset workspace for new task
  resetWorkspace: () => {
    const { abortController } = get();
    if (abortController) {
      abortController.abort();
    }
    set({
      userMessage: null,
      assistantMessage: null,
      status: 'idle',
      activeAgents: {},
      activityFeed: [],
      runSummary: null,
      error: null,
      abortController: null,
    });
  },
}));
