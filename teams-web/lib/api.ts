import type {
  Company,
  CompanyDetails,
  AgentHierarchy,
  SuggestedPrompt,
  SSEEvent,
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8023';

// Fetch utilities
async function fetchJSON<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

// Company endpoints
export async function getCompanies(): Promise<Company[]> {
  const data = await fetchJSON<{ companies: Company[] }>('/api/companies');
  return data.companies;
}

export async function getCompany(companyId: string): Promise<CompanyDetails> {
  return fetchJSON<CompanyDetails>(`/api/companies/${companyId}`);
}

// Agent endpoints
export async function getAgents(companyId: string): Promise<AgentHierarchy> {
  return fetchJSON<AgentHierarchy>(`/api/companies/${companyId}/agents`);
}

// Suggested prompts
export async function getSuggestedPrompts(
  companyId: string
): Promise<SuggestedPrompt[]> {
  const data = await fetchJSON<{ prompts: SuggestedPrompt[] }>(
    `/api/companies/${companyId}/suggested-prompts`
  );
  return data.prompts;
}

// SSE streaming chat
export interface StreamChatOptions {
  companyId: string;
  message: string;
  onEvent: (event: SSEEvent) => void;
  onError: (error: Error) => void;
  onComplete: () => void;
}

export function streamChat({
  companyId,
  message,
  onEvent,
  onError,
  onComplete,
}: StreamChatOptions): AbortController {
  const controller = new AbortController();

  const runStream = async () => {
    try {
      const response = await fetch(`${API_URL}/api/companies/${companyId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          stream: true,
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Parse SSE events from buffer
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        let currentEvent: string | null = null;

        for (const line of lines) {
          if (line.startsWith('event:')) {
            currentEvent = line.slice(6).trim();
          } else if (line.startsWith('data:') && currentEvent) {
            try {
              const data = JSON.parse(line.slice(5).trim());
              onEvent(data as SSEEvent);
            } catch {
              // Skip malformed JSON
            }
            currentEvent = null;
          }
        }
      }

      onComplete();
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        onError(error as Error);
      }
    }
  };

  runStream();
  return controller;
}
