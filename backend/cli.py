#!/usr/bin/env python3
"""
AI Workforce Orchestrator - CLI

Usage:
    python cli.py                           # Interactive mode (default company)
    python cli.py -c promptsmint            # Interactive mode (specific company)
    python cli.py chat "Your message"       # Single query
    python cli.py companies                 # List companies
    python cli.py agents                    # Show agent hierarchy
    python cli.py runs                      # List recent runs
    python cli.py run <run_id>              # View a specific run
"""

import sys
import os
import asyncio
import argparse
import json
from datetime import datetime
from pathlib import Path

from config import load_company_data, list_companies, get_suggested_prompts
from workforce import create_workforce
from core import Session, EventType


# =============================================================================
# COLORS
# =============================================================================

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Agent colors
    FOUNDER = "\033[94m"      # Blue
    MARKETING = "\033[95m"    # Magenta
    RESEARCHER = "\033[96m"   # Cyan
    SEO = "\033[93m"          # Yellow
    CONTENT = "\033[92m"      # Green

    # Status colors
    SUCCESS = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    INFO = "\033[94m"


AGENT_COLORS = {
    "Founder": Colors.FOUNDER,
    "Marketing Head": Colors.MARKETING,
    "Market Researcher": Colors.RESEARCHER,
    "Data Analyst": Colors.INFO,
    "SEO Analyst": Colors.SEO,
    "Content Creator": Colors.CONTENT,
}

TMP_DIR = Path(__file__).parent / "tmp"


# =============================================================================
# HELPERS
# =============================================================================

def get_agent_color(agent: str) -> str:
    return AGENT_COLORS.get(agent, Colors.RESET)


def print_header(title: str, subtitle: str = ""):
    width = 50
    print(f"\n{Colors.BOLD}{'═' * width}{Colors.RESET}")
    print(f"{Colors.BOLD}  {title}{Colors.RESET}")
    if subtitle:
        print(f"{Colors.DIM}  {subtitle}{Colors.RESET}")
    print(f"{Colors.BOLD}{'═' * width}{Colors.RESET}\n")


def print_table(headers: list[str], rows: list[list[str]], colors: list[str] = None):
    """Print a simple table."""
    if not rows:
        print(f"{Colors.DIM}  (empty){Colors.RESET}")
        return

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Print header
    header_str = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(f"{Colors.BOLD}  {header_str}{Colors.RESET}")
    print(f"  {'-' * sum(widths) + '-' * (len(widths) - 1) * 2}")

    # Print rows
    for ri, row in enumerate(rows):
        color = colors[ri] if colors and ri < len(colors) else ""
        row_str = "  ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
        print(f"  {color}{row_str}{Colors.RESET}")


def print_tree(hierarchy: dict, node: str = "founder", prefix: str = "", is_last: bool = True):
    """Print agent hierarchy as a tree."""
    info = hierarchy.get(node, {})
    name = info.get("name", node)
    role = info.get("role", "")
    color = get_agent_color(name)

    connector = "└── " if is_last else "├── "
    print(f"{prefix}{connector}{color}{name}{Colors.RESET} {Colors.DIM}({role}){Colors.RESET}")

    children = info.get("children", [])
    for i, child in enumerate(children):
        new_prefix = prefix + ("    " if is_last else "│   ")
        print_tree(hierarchy, child, new_prefix, i == len(children) - 1)


def print_event(event):
    """Print a session event with formatting."""
    color = get_agent_color(event.agent)
    timestamp = datetime.fromisoformat(event.timestamp).strftime("%H:%M:%S")

    if event.type == EventType.START:
        print(f"\n{Colors.DIM}[{timestamp}]{Colors.RESET} {Colors.BOLD}Starting workflow...{Colors.RESET}")

    elif event.type == EventType.AGENT_CHANGE:
        print(f"{Colors.DIM}[{timestamp}]{Colors.RESET} {color}► {event.agent}{Colors.RESET} activated")

    elif event.type == EventType.TOOL_CALL:
        tool = event.data.get("tool", "unknown")
        print(f"{Colors.DIM}[{timestamp}]{Colors.RESET} {Colors.WARNING}⚡ {event.agent} → {tool}{Colors.RESET}")

    elif event.type == EventType.TOOL_RESULT:
        print(f"{Colors.DIM}[{timestamp}]{Colors.RESET} {Colors.DIM}  ✓ Tool completed{Colors.RESET}")

    elif event.type == EventType.DELTA:
        content = event.data.get("content", "")
        print(content, end="", flush=True)

    elif event.type == EventType.COMPLETE:
        print()  # Newline after streaming
        print(f"\n{Colors.SUCCESS}{'─' * 50}{Colors.RESET}")
        agents = event.data.get("agents_involved", [])
        print(f"{Colors.DIM}Agents: {', '.join(agents)}{Colors.RESET}")

    elif event.type == EventType.ARTIFACTS_SAVED:
        path = event.data.get("path", "")
        print(f"{Colors.DIM}Artifacts: {path}{Colors.RESET}")

    elif event.type == EventType.ERROR:
        error = event.data.get("error", "Unknown error")
        print(f"\n{Colors.ERROR}✗ Error: {error}{Colors.RESET}")


# =============================================================================
# COMMANDS
# =============================================================================

def cmd_companies(args):
    """List all available companies."""
    print_header("Available Companies")

    rows = []
    colors = []
    for company_id in list_companies():
        try:
            data = load_company_data(company_id)
            company = data.get("company", {})
            rows.append([
                company_id,
                company.get("name", ""),
                company.get("mission", "")[:40] + "..." if len(company.get("mission", "")) > 40 else company.get("mission", ""),
            ])
            colors.append("")
        except Exception as e:
            rows.append([company_id, "(error)", str(e)[:40]])
            colors.append(Colors.ERROR)

    print_table(["ID", "Name", "Mission"], rows, colors)
    print()


def cmd_company(args):
    """Show company details."""
    try:
        data = load_company_data(args.company)
        company = data.get("company", {})

        print_header(company.get("name", args.company), f"ID: {args.company}")

        print(f"  {Colors.BOLD}Mission:{Colors.RESET}")
        print(f"  {company.get('mission', 'N/A')}\n")

        print(f"  {Colors.BOLD}Brand Voice:{Colors.RESET}")
        print(f"  {company.get('brand_voice', 'N/A')}\n")

        print(f"  {Colors.BOLD}Target Audience:{Colors.RESET}")
        print(f"  {company.get('target_audience', 'N/A')}\n")

        products = company.get("products", [])
        if products:
            print(f"  {Colors.BOLD}Products:{Colors.RESET}")
            for p in products:
                print(f"    • {p}")
            print()

    except FileNotFoundError:
        print(f"{Colors.ERROR}Company '{args.company}' not found.{Colors.RESET}")
        sys.exit(1)


def cmd_agents(args):
    """Show agent hierarchy."""
    try:
        data = load_company_data(args.company)
        workforce = create_workforce(data)
        hierarchy = workforce["hierarchy"]

        company_name = data.get("company", {}).get("name", args.company)
        print_header("Agent Hierarchy", company_name)

        print_tree(hierarchy)
        print()

        # Also show as table
        print(f"\n  {Colors.BOLD}Agent Details:{Colors.RESET}\n")
        rows = []
        colors = []
        for agent_id, info in hierarchy.items():
            name = info.get("name", agent_id)
            role = info.get("role", "")
            children = ", ".join(info.get("children", [])) or "-"
            rows.append([name, role, children])
            colors.append(get_agent_color(name))

        print_table(["Agent", "Role", "Can Delegate To"], rows, colors)
        print()

    except FileNotFoundError:
        print(f"{Colors.ERROR}Company '{args.company}' not found.{Colors.RESET}")
        sys.exit(1)


def cmd_prompts(args):
    """Show suggested prompts."""
    try:
        data = load_company_data(args.company)
        prompts = get_suggested_prompts(data)

        company_name = data.get("company", {}).get("name", args.company)
        print_header("Suggested Prompts", company_name)

        for i, p in enumerate(prompts, 1):
            complexity_color = {
                "simple": Colors.SUCCESS,
                "medium": Colors.WARNING,
                "complex": Colors.ERROR,
            }.get(p.get("complexity", ""), "")

            print(f"  {Colors.BOLD}{i}. {p['label']}{Colors.RESET} {complexity_color}[{p.get('complexity', '')}]{Colors.RESET}")
            print(f"     {Colors.DIM}\"{p['prompt']}\"{Colors.RESET}")
            flow = " → ".join(p.get("expected_flow", []))
            print(f"     {Colors.DIM}Flow: {flow}{Colors.RESET}\n")

    except FileNotFoundError:
        print(f"{Colors.ERROR}Company '{args.company}' not found.{Colors.RESET}")
        sys.exit(1)


def cmd_runs(args):
    """List recent runs."""
    print_header("Recent Runs")

    if not TMP_DIR.exists():
        print(f"  {Colors.DIM}No runs yet.{Colors.RESET}\n")
        return

    runs = sorted(TMP_DIR.iterdir(), reverse=True)[:args.limit]

    if not runs:
        print(f"  {Colors.DIM}No runs yet.{Colors.RESET}\n")
        return

    rows = []
    for run_dir in runs:
        if not run_dir.is_dir():
            continue

        run_id = run_dir.name
        trace_file = run_dir / "trace.json"
        input_file = run_dir / "input.txt"

        company = "-"
        duration = "-"
        message = "-"

        if trace_file.exists():
            trace = json.loads(trace_file.read_text())
            company = trace.get("company", "-")
            duration = f"{trace.get('duration_ms', 0)}ms"

        if input_file.exists():
            msg = input_file.read_text().strip()
            message = msg[:50] + "..." if len(msg) > 50 else msg

        # Parse timestamp from run_id
        try:
            ts = datetime.strptime(run_id[:15], "%Y%m%d_%H%M%S")
            time_str = ts.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = run_id

        rows.append([run_id[:20], time_str, company, duration, message])

    print_table(["Run ID", "Time", "Company", "Duration", "Message"], rows)
    print(f"\n  {Colors.DIM}Use 'python cli.py run <run_id>' to view details{Colors.RESET}\n")


def cmd_run(args):
    """View a specific run."""
    run_dir = TMP_DIR / args.run_id

    # Try partial match
    if not run_dir.exists():
        matches = [d for d in TMP_DIR.iterdir() if d.name.startswith(args.run_id)]
        if len(matches) == 1:
            run_dir = matches[0]
        elif len(matches) > 1:
            print(f"{Colors.WARNING}Multiple matches:{Colors.RESET}")
            for m in matches:
                print(f"  {m.name}")
            sys.exit(1)
        else:
            print(f"{Colors.ERROR}Run '{args.run_id}' not found.{Colors.RESET}")
            sys.exit(1)

    print_header("Run Details", run_dir.name)

    # Trace
    trace_file = run_dir / "trace.json"
    if trace_file.exists():
        trace = json.loads(trace_file.read_text())
        print(f"  {Colors.BOLD}Company:{Colors.RESET} {trace.get('company', 'N/A')}")
        print(f"  {Colors.BOLD}Duration:{Colors.RESET} {trace.get('duration_ms', 0)}ms")
        print(f"  {Colors.BOLD}Agents:{Colors.RESET} {', '.join(trace.get('agents_involved', []))}")
        print(f"  {Colors.BOLD}Events:{Colors.RESET} {trace.get('event_count', 0)}")
        print()

    # Input
    input_file = run_dir / "input.txt"
    if input_file.exists():
        print(f"  {Colors.BOLD}Input:{Colors.RESET}")
        print(f"  {Colors.DIM}{input_file.read_text().strip()}{Colors.RESET}\n")

    # Response
    response_file = run_dir / "response.md"
    if response_file.exists():
        print(f"  {Colors.BOLD}Response:{Colors.RESET}")
        response = response_file.read_text().strip()
        for line in response.split("\n"):
            print(f"  {line}")
        print()

    # Handoffs
    if trace_file.exists():
        trace = json.loads(trace_file.read_text())
        handoffs = trace.get("handoffs", [])
        if handoffs:
            print(f"  {Colors.BOLD}Handoffs:{Colors.RESET}")
            for h in handoffs:
                color = get_agent_color(h.get("agent", ""))
                print(f"    {color}► {h.get('agent', '')}{Colors.RESET} - {h.get('details', '')}")
            print()


async def cmd_chat(args):
    """Send a single message."""
    try:
        data = load_company_data(args.company)
        workforce = create_workforce(data)
        entry_agent = workforce["entry_agent"]

        company_name = data.get("company", {}).get("name", args.company)
        print_header("Chat", company_name)

        print(f"  {Colors.BOLD}You:{Colors.RESET} {args.message}\n")

        session = Session(
            company_data=data,
            entry_agent=entry_agent,
            save_artifacts=True,
        )

        print(f"  {Colors.DIM}Run ID: {session.run_id}{Colors.RESET}")

        async for event in session.run_stream(args.message):
            print_event(event)

        result = session.result
        print(f"{Colors.DIM}Duration: {result.duration_ms}ms{Colors.RESET}\n")

    except FileNotFoundError:
        print(f"{Colors.ERROR}Company '{args.company}' not found.{Colors.RESET}")
        sys.exit(1)


async def cmd_interactive(args):
    """Interactive chat mode."""
    try:
        data = load_company_data(args.company)
        workforce = create_workforce(data)
        entry_agent = workforce["entry_agent"]
        company_name = data.get("company", {}).get("name", args.company)

        print_header("AI Workforce Orchestrator", f"Company: {company_name}")

        print("  Commands:")
        print(f"    {Colors.BOLD}/help{Colors.RESET}      - Show commands")
        print(f"    {Colors.BOLD}/company{Colors.RESET}   - Show current company")
        print(f"    {Colors.BOLD}/switch{Colors.RESET}    - Switch company")
        print(f"    {Colors.BOLD}/agents{Colors.RESET}    - Show agent hierarchy")
        print(f"    {Colors.BOLD}/prompts{Colors.RESET}   - Show suggested prompts")
        print(f"    {Colors.BOLD}/runs{Colors.RESET}      - Show recent runs")
        print(f"    {Colors.BOLD}/clear{Colors.RESET}     - Clear screen")
        print(f"    {Colors.BOLD}/exit{Colors.RESET}      - Exit")
        print()
        print("  Or type a message to chat with the AI workforce.\n")

        current_company = args.company

        while True:
            try:
                user_input = input(f"{Colors.BOLD}You:{Colors.RESET} ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    cmd = user_input[1:].lower().split()[0]
                    cmd_args = user_input[1:].split()[1:] if len(user_input.split()) > 1 else []

                    if cmd in ("exit", "quit", "q"):
                        print(f"\n{Colors.DIM}Goodbye!{Colors.RESET}\n")
                        break

                    elif cmd == "help":
                        print(f"\n  {Colors.BOLD}Commands:{Colors.RESET}")
                        print(f"    /help              Show this help")
                        print(f"    /company           Show current company info")
                        print(f"    /switch <id>       Switch to another company")
                        print(f"    /agents            Show agent hierarchy")
                        print(f"    /prompts           Show suggested prompts")
                        print(f"    /runs              Show recent runs")
                        print(f"    /run <id>          View a specific run")
                        print(f"    /companies         List all companies")
                        print(f"    /clear             Clear screen")
                        print(f"    /exit              Exit\n")

                    elif cmd == "company":
                        args.company = current_company
                        cmd_company(args)

                    elif cmd == "companies":
                        cmd_companies(args)

                    elif cmd == "switch":
                        if cmd_args:
                            new_company = cmd_args[0]
                            try:
                                data = load_company_data(new_company)
                                workforce = create_workforce(data)
                                entry_agent = workforce["entry_agent"]
                                current_company = new_company
                                company_name = data.get("company", {}).get("name", new_company)
                                print(f"\n  {Colors.SUCCESS}Switched to {company_name}{Colors.RESET}\n")
                            except FileNotFoundError:
                                print(f"\n  {Colors.ERROR}Company '{new_company}' not found.{Colors.RESET}")
                                print(f"  {Colors.DIM}Available: {', '.join(list_companies())}{Colors.RESET}\n")
                        else:
                            print(f"\n  {Colors.WARNING}Usage: /switch <company_id>{Colors.RESET}")
                            print(f"  {Colors.DIM}Available: {', '.join(list_companies())}{Colors.RESET}\n")

                    elif cmd == "agents":
                        args.company = current_company
                        cmd_agents(args)

                    elif cmd == "prompts":
                        args.company = current_company
                        cmd_prompts(args)

                    elif cmd == "runs":
                        args.limit = 10
                        cmd_runs(args)

                    elif cmd == "run":
                        if cmd_args:
                            args.run_id = cmd_args[0]
                            cmd_run(args)
                        else:
                            print(f"\n  {Colors.WARNING}Usage: /run <run_id>{Colors.RESET}\n")

                    elif cmd == "clear":
                        os.system("clear" if os.name != "nt" else "cls")
                        print_header("AI Workforce Orchestrator", f"Company: {company_name}")

                    else:
                        print(f"\n  {Colors.WARNING}Unknown command: /{cmd}{Colors.RESET}")
                        print(f"  {Colors.DIM}Type /help for available commands{Colors.RESET}\n")

                else:
                    # Chat message
                    session = Session(
                        company_data=data,
                        entry_agent=entry_agent,
                        save_artifacts=True,
                    )

                    print(f"\n  {Colors.DIM}Run ID: {session.run_id}{Colors.RESET}")

                    async for event in session.run_stream(user_input):
                        print_event(event)

                    result = session.result
                    print(f"\n  {Colors.DIM}Duration: {result.duration_ms}ms{Colors.RESET}\n")

            except KeyboardInterrupt:
                print(f"\n\n{Colors.DIM}Interrupted. Type /exit to quit.{Colors.RESET}\n")
            except EOFError:
                print(f"\n{Colors.DIM}Goodbye!{Colors.RESET}\n")
                break

    except FileNotFoundError:
        print(f"{Colors.ERROR}Company '{args.company}' not found.{Colors.RESET}")
        sys.exit(1)


# =============================================================================
# MAIN
# =============================================================================

def get_default_company() -> str:
    companies = list_companies()
    DEFAULT_COMPANY = os.getenv("COMPANY_ID", "solaris")
    return DEFAULT_COMPANY if DEFAULT_COMPANY in companies else companies[0]


def main():
    parser = argparse.ArgumentParser(
        description="AI Workforce Orchestrator CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-c", "--company",
        default=None,
        help="Company ID to use"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # companies
    sub = subparsers.add_parser("companies", help="List all companies")

    # company
    sub = subparsers.add_parser("company", help="Show company details")

    # agents
    sub = subparsers.add_parser("agents", help="Show agent hierarchy")

    # prompts
    sub = subparsers.add_parser("prompts", help="Show suggested prompts")

    # runs
    sub = subparsers.add_parser("runs", help="List recent runs")
    sub.add_argument("-n", "--limit", type=int, default=10, help="Number of runs to show")

    # run
    sub = subparsers.add_parser("run", help="View a specific run")
    sub.add_argument("run_id", help="Run ID (or prefix)")

    # chat
    sub = subparsers.add_parser("chat", help="Send a single message")
    sub.add_argument("message", help="Message to send")

    args = parser.parse_args()

    # Set default company if not specified
    if args.company is None:
        args.company = get_default_company()

    # Run command
    if args.command == "companies":
        cmd_companies(args)
    elif args.command == "company":
        cmd_company(args)
    elif args.command == "agents":
        cmd_agents(args)
    elif args.command == "prompts":
        cmd_prompts(args)
    elif args.command == "runs":
        cmd_runs(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "chat":
        asyncio.run(cmd_chat(args))
    else:
        # Default: interactive mode
        asyncio.run(cmd_interactive(args))


if __name__ == "__main__":
    main()
