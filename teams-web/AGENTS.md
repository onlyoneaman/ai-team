# Teams AI Frontend

Real-time visualization for a multi-agent AI workforce system.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Header                                 │
│  [☰] [Avatar] Teams AI          [New Task] [Workspace|Profile]  │
├──────────────────┬──────────────────────────────────────────────┤
│     Sidebar      │               Main Content                    │
│   (collapsible)  │                                               │
│                  │   ┌─────────────────────────────────────┐    │
│  ┌────────────┐  │   │         Chat / Workspace            │    │
│  │ Agent Team │  │   │                                     │    │
│  │ (idle)     │  │   │   [User Message]                    │    │
│  └────────────┘  │   │                                     │    │
│                  │   │   [Agent Team Visualization]        │    │
│  ┌────────────┐  │   │        (when running)               │    │
│  │ Activity   │  │   │                                     │    │
│  │ Feed       │  │   │   [Final Response]                  │    │
│  └────────────┘  │   │        (when complete)              │    │
│                  │   └─────────────────────────────────────┘    │
└──────────────────┴──────────────────────────────────────────────┘
```

## Task Lifecycle

### 1. Idle State
- Homepage shows welcome message with avatar
- Input field ready for user task
- Suggested prompts below input
- Agent team visible in sidebar (faded, 40% opacity)

### 2. Running State
- Agent Team moves to **center of chat** (hero visualization)
- Active agent highlighted (100% opacity, pulsing)
- Completed agents show checkmark (70% opacity)
- Sidebar shows **Activity Feed only**
- No text content in chat during execution

### 3. Complete State
- Final response appears in chat (markdown rendered)
- Copy/Download buttons on hover
- Agent Team moves back to sidebar
- "New Task" button appears in header

## State Management

Using Zustand with three stores:

```typescript
// UI Store (persisted)
useUIStore: {
  sidebarOpen: boolean
  currentView: 'workspace' | 'company-profile'
  isTyping: boolean  // For avatar animation
}

// Company Store
useCompanyStore: {
  companies: Company[]
  selectedCompanyId: string
  companyDetails: CompanyDetails
  agents: AgentHierarchy
  suggestedPrompts: SuggestedPrompt[]
}

// Chat Store
useChatStore: {
  userMessage: ChatMessage
  assistantMessage: ChatMessage
  status: 'idle' | 'running' | 'complete' | 'error'
  activeAgents: Record<string, AgentStatus>
  activityFeed: ActivityItem[]
}
```

## SSE Event Handling

Events from backend map to UI updates:

| Event | UI Action |
|-------|-----------|
| `start` | Add to activity feed |
| `agent_change` | Highlight new agent, add to activity |
| `tool_call` | Add to activity (e.g., "Transfer to Marketing Head") |
| `tool_result` | Update activity |
| `complete` | Show final response, move agent tree to sidebar |
| `error` | Show error message |

Note: `delta` events are **ignored** - we don't stream intermediate content. Final response comes from `complete` event.

## Component Hierarchy

```
app/
├── page.tsx                    # Main workspace
├── layout.tsx                  # Root layout with providers

components/
├── header.tsx                  # Logo, nav, company selector
├── sidebar/
│   └── sidebar.tsx             # Collapsible sidebar container
├── workspace/
│   ├── chat-area.tsx           # Main chat interface
│   └── chat-message.tsx        # Message bubble + markdown
├── agents/
│   ├── agent-tree.tsx          # Sidebar agent tree
│   ├── agent-tree-chat.tsx     # Chat-centered agent tree (running)
│   ├── agent-node.tsx          # Single agent with status
│   └── activity-feed.tsx       # Real-time event timeline
└── company/
    ├── company-selector.tsx    # Header company picker
    └── company-profile.tsx     # Company details view
```

## Visual Design

### Colors
- Primary: `#219ebc` (teal blue)
- Accent: `#ffb703` (warm gold)
- Light mode only

### Agent Status
- **Idle**: 40% opacity, faded
- **Active**: 100% opacity, pulsing animation, shadow
- **Complete**: 70% opacity, checkmark

### Avatars
- `/avatar.png` - Default state
- `/avatar-thinking.png` - When typing or agents working

## Key Interactions

### Avatar Animation
- Switches to thinking avatar when user types
- Debounced 250ms to switch back to normal
- Also shows thinking avatar during task execution

### Activity Feed
- Relative timestamps ("5s", "2m")
- Title case formatting ("Transfer to Marketing Head")
- Auto-scrolls to latest

### Response Actions
- Copy button (clipboard)
- Download button (markdown file)
- Appears on hover

---

## UI Principles

### 1. Show, Don't Tell
Instead of "Working on it...", show the agent visualization with live status updates. Users see which agent is active and what's happening.

### 2. Hero the Action
During task execution, the Agent Team moves to center stage. This is the most important thing - let users watch the AI workforce collaborate.

### 3. Reduce Noise
- No JSON blobs or raw tool outputs
- No intermediate streaming text
- Activity feed shows human-readable summaries
- Final response is clean markdown

### 4. Friendly Language
- "How can I help you today?" not "Welcome to Platform"
- "What would you like to work on?" not "Describe your task"
- "5s" not "21:15:35"
- "Marketing Head" not "marketing_head"

### 5. Progressive Disclosure
- Sidebar collapsible for focus
- Activity feed secondary to agent visualization
- Copy/download buttons appear on hover

### 6. Instant Feedback
- Avatar changes when typing (debounced)
- Agent pulses when active
- Relative times update live

### 7. Single-Session Model
Each task is complete in itself:
- Submit → Agents work → Deliver → Done
- "New Task" to start fresh
- No conversation continuation

---

*Keep this doc updated when modifying components or state management.*
