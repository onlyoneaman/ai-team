"""
Session management for agent runs.
Handles execution, logging, and artifact storage.
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import AsyncGenerator, Callable, Any

from agents import Runner
from agents.stream_events import RunItemStreamEvent, RawResponsesStreamEvent

from workforce import WorkforceContext
from utils import estimate_cost


class EventType(str, Enum):
    """Types of events during a session."""
    START = "start"
    AGENT_CHANGE = "agent_change"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    DELTA = "delta"
    COMPLETE = "complete"
    ARTIFACTS_SAVED = "artifacts_saved"
    ERROR = "error"


@dataclass
class SessionEvent:
    """A single event during a session."""
    type: EventType
    timestamp: str
    agent: str
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "timestamp": self.timestamp,
            "agent": self.agent,
            **self.data,
        }

    def to_sse(self) -> str:
        """Format as Server-Sent Event."""
        return f"event: {self.type.value}\ndata: {json.dumps(self.to_dict())}\n\n"


@dataclass
class SessionResult:
    """Final result of a session."""
    run_id: str
    response: str
    events: list[SessionEvent]
    agents_involved: list[str]
    duration_ms: int
    artifacts_path: Path | None = None

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "response": self.response,
            "agents_involved": self.agents_involved,
            "duration_ms": self.duration_ms,
            "event_count": len(self.events),
            "artifacts_path": str(self.artifacts_path) if self.artifacts_path else None,
        }


class Session:
    """
    Manages a single agent workflow run.

    Usage:
        session = Session(company_data, entry_agent)

        # Streaming
        async for event in session.run_stream("Hello"):
            print(event)
        result = session.result

        # Non-streaming
        result = await session.run("Hello")
    """

    BASE_DIR = Path(__file__).parent.parent
    TMP_DIR = BASE_DIR / "tmp"

    def __init__(
        self,
        company_data: dict,
        entry_agent: Any,
        save_artifacts: bool = True,
    ):
        self.company_data = company_data
        self.entry_agent = entry_agent
        self.save_artifacts = save_artifacts

        # Run state
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.start_time: datetime | None = None
        self.end_time: datetime | None = None
        self.events: list[SessionEvent] = []
        self.agents_involved: set[str] = set()
        self.current_agent: str = "founder"
        self.response: str = ""
        self.context: WorkforceContext | None = None
        self.artifacts_path: Path | None = None
        self._emitted_tool_calls: set[str] = set()  # Dedupe tool calls
        self.usage: dict | None = None  # Token usage

        # Set up artifacts directory
        if self.save_artifacts:
            self.artifacts_path = self.TMP_DIR / self.run_id
            self.artifacts_path.mkdir(parents=True, exist_ok=True)

    @property
    def result(self) -> SessionResult:
        """Get the session result after run completes."""
        duration = 0
        if self.start_time and self.end_time:
            duration = int((self.end_time - self.start_time).total_seconds() * 1000)

        return SessionResult(
            run_id=self.run_id,
            response=self.response,
            events=self.events,
            agents_involved=list(self.agents_involved),
            duration_ms=duration,
            artifacts_path=self.artifacts_path,
        )

    def _emit(self, event_type: EventType, **data) -> SessionEvent:
        """Create and store an event."""
        return self._emit_with_agent(event_type, self.current_agent, **data)

    def _emit_with_agent(self, event_type: EventType, agent: str, **data) -> SessionEvent:
        """Create and store an event with explicit agent."""
        event = SessionEvent(
            type=event_type,
            timestamp=datetime.now().isoformat(),
            agent=agent,
            data=data,
        )
        self.events.append(event)
        self._log_event(event)
        return event

    def _log_event(self, event: SessionEvent):
        """Append event to JSONL log file."""
        if not self.artifacts_path:
            return
        log_file = self.artifacts_path / "events.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

    def _save_artifacts(self):
        """Save final artifacts after run completes."""
        if not self.artifacts_path:
            return

        # Save response
        (self.artifacts_path / "response.md").write_text(self.response)

        # Collect agents from handoff trace (more reliable than event tracking)
        if self.context and self.context.trace_steps:
            for step in self.context.trace_steps:
                if step.get("agent"):
                    self.agents_involved.add(step["agent"])

        # Save trace summary
        trace = {
            "run_id": self.run_id,
            "company": self.company_data.get("company", {}).get("name"),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.result.duration_ms,
            "agents_involved": list(self.agents_involved),
            "event_count": len(self.events),
            "usage": self.usage,
            "handoffs": self.context.trace_steps if self.context else [],
            "task_state": {
                "goal": self.context.task.goal,
                "status": self.context.task.status,
                "iteration": self.context.task.iteration,
                "artifacts": self.context.task.artifacts,
            } if self.context else None,
        }
        (self.artifacts_path / "trace.json").write_text(
            json.dumps(trace, indent=2)
        )

        # Save conversation (cleaner than events.jsonl)
        conversation = {
            "input": (self.artifacts_path / "input.txt").read_text() if (self.artifacts_path / "input.txt").exists() else "",
            "output": self.response,
            "agents": list(self.agents_involved),
            "handoffs": self.context.trace_steps if self.context else [],
            "tool_calls": [
                {"agent": e.agent, "tool": e.data.get("tool")}
                for e in self.events if e.type == EventType.TOOL_CALL
            ],
        }
        (self.artifacts_path / "conversation.json").write_text(
            json.dumps(conversation, indent=2)
        )

    async def run(self, message: str) -> SessionResult:
        """Run the workflow and return the final result (non-streaming)."""
        async for _ in self.run_stream(message):
            pass  # Consume all events
        return self.result

    async def run_stream(self, message: str) -> AsyncGenerator[SessionEvent, None]:
        """
        Run the workflow and yield events as they occur.
        After completion, access `session.result` for the final result.
        """
        self.start_time = datetime.now()
        self.context = WorkforceContext(company_data=self.company_data)

        # Save input
        if self.artifacts_path:
            (self.artifacts_path / "input.txt").write_text(message)

        # Add initial agent
        self.agents_involved.add(self.current_agent)
        yield self._emit(EventType.START, message="Starting agent workflow...")

        try:
            result = Runner.run_streamed(
                self.entry_agent,
                message,
                context=self.context,
                max_turns=30
            )

            response_chunks: list[str] = []

            async for event in result.stream_events():
                # Sync with context.current_agent (set by handoff callbacks - source of truth)
                if self.context and self.context.current_agent != self.current_agent:
                    self.current_agent = self.context.current_agent
                    self.agents_involved.add(self.current_agent)
                    yield self._emit(
                        EventType.AGENT_CHANGE,
                        details=f"{self.current_agent} is now handling the request",
                    )

                # Handle stream events
                if isinstance(event, RunItemStreamEvent):
                    item = event.item
                    if hasattr(item, "raw_item") and hasattr(item.raw_item, "type"):
                        if item.raw_item.type == "function_call":
                            tool_name = getattr(item.raw_item, "name", "unknown")
                            call_id = getattr(item.raw_item, "call_id", None) or id(item.raw_item)
                            # Dedupe: only emit once per call_id
                            if call_id not in self._emitted_tool_calls:
                                self._emitted_tool_calls.add(call_id)
                                # Use context.current_agent (set by handoff callbacks) as source of truth
                                agent_for_call = self.context.current_agent if self.context else self.current_agent
                                self.agents_involved.add(agent_for_call)
                                yield self._emit_with_agent(
                                    EventType.TOOL_CALL,
                                    agent_for_call,
                                    tool=tool_name,
                                    details=f"Using tool: {tool_name}",
                                )
                        elif item.raw_item.type == "function_call_output":
                            agent_for_result = self.context.current_agent if self.context else self.current_agent
                            yield self._emit_with_agent(
                                EventType.TOOL_RESULT,
                                agent_for_result,
                                details="Tool execution completed",
                            )

                elif isinstance(event, RawResponsesStreamEvent):
                    if hasattr(event.data, "delta") and event.data.delta:
                        response_chunks.append(event.data.delta)
                        yield self._emit(
                            EventType.DELTA,
                            content=event.data.delta,
                        )

            # Get final result (final_output is available after stream completes)
            self.response = result.final_output or "".join(response_chunks) or "No response generated."
            self.end_time = datetime.now()

            # Capture usage and estimate cost
            if hasattr(result, "context_wrapper") and hasattr(result.context_wrapper, "usage"):
                usage = result.context_wrapper.usage
                cost = estimate_cost(usage.input_tokens, usage.output_tokens)
                self.usage = {
                    "requests": usage.requests,
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                    "total_tokens": usage.total_tokens,
                    **cost,
                }

            yield self._emit(
                EventType.COMPLETE,
                response=self.response,
                agents_involved=list(self.agents_involved),
            )

            # Save artifacts and emit event
            self._save_artifacts()
            if self.artifacts_path:
                yield self._emit(
                    EventType.ARTIFACTS_SAVED,
                    path=str(self.artifacts_path),
                )

        except Exception as e:
            self.end_time = datetime.now()
            self.response = f"Error: {str(e)}"
            yield self._emit(EventType.ERROR, error=str(e))
            # Still save artifacts on error
            self._save_artifacts()
            if self.artifacts_path:
                yield self._emit(
                    EventType.ARTIFACTS_SAVED,
                    path=str(self.artifacts_path),
                )
