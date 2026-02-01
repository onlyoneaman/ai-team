import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type View = 'workspace' | 'company-profile';

interface UIState {
  // Sidebar
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;

  // Current view
  currentView: View;
  setView: (view: View) => void;

  // Agent tree location: true = show in chat (during execution), false = show in sidebar
  agentTreeInChat: boolean;
  setAgentTreeInChat: (inChat: boolean) => void;

  // Typing state (for avatar animation)
  isTyping: boolean;
  setIsTyping: (typing: boolean) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      // Sidebar - default open
      sidebarOpen: true,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),

      // View
      currentView: 'workspace',
      setView: (view: View) => set({ currentView: view }),

      // Agent tree location - default in sidebar
      agentTreeInChat: false,
      setAgentTreeInChat: (inChat: boolean) => set({ agentTreeInChat: inChat }),

      // Typing state
      isTyping: false,
      setIsTyping: (typing: boolean) => set({ isTyping: typing }),
    }),
    {
      name: 'teams-ai-ui',
      partialize: (state) => ({ sidebarOpen: state.sidebarOpen }),
    }
  )
);
