import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from lala.core.orchestrator import Orchestrator
from lala.core.state import LanguageCode
from lala.core.providers.local import LocalProvider
from lala.voice.pipeline import VoicePipeline
from lala.memory.models import MemoryCategory
from lala.agent.executor import MAX_AGENT_STEPS, MAX_TOOL_ITERATIONS

console = Console()

def run_cli():
    orchestrator = Orchestrator()
    voice_pipeline = VoicePipeline(orchestrator=orchestrator)
    
    active_provider = orchestrator.router.get_active_provider()
    health = {"online": False, "model_available": False, "installed_models": []}
    
    if isinstance(active_provider, LocalProvider):
        health = active_provider.check_health()

    status_str = "[bold green]ONLINE[/bold green]" if health.get("online") else "[bold red]OFFLINE (Local Brain Unavailable)[/bold red]"
    model_name = orchestrator.config.model_router.providers.get("local", {}).model_name if orchestrator.config.model_router.providers else "qwen2.5:3b"
    online_status = "[bold green]ENABLED[/bold green]" if orchestrator.intel_manager.is_online_enabled() else "[bold yellow]DISABLED (Off by default)[/bold yellow]"

    banner = (
        f"[bold cyan]🚀 LALA Cybersecurity Investigation & Detection Platform (Phase 7)[/bold cyan]\n"
        f"──────────────────────────────────────────────────\n"
        f"[green]Local Brain:[/green] Ollama ({orchestrator.config.model_router.providers.get('local', {}).endpoint or 'http://127.0.0.1:11434'})\n"
        f"[green]Model:[/green] [bold white]{model_name}[/bold white] | [green]Status:[/green] {status_str}\n"
        f"[green]Online Intelligence Mode:[/green] {online_status}\n"
        f"[green]Network Security Engine:[/green] ENFORCED (Domain Allowlisting Active)\n"
        f"[green]Security Engine:[/green] ENFORCED (Zero Privilege Escalation)\n"
        f"──────────────────────────────────────────────────\n"
        f"[dim]Commands: '/investigate <IOC>', '/case list', '/yara scan <path>', '/yara rules', '/sigma rules', '/online', '/exit'[/dim]"
    )
    
    console.print(Panel(banner, border_style="cyan", title="LALA Cybersecurity Platform"))
    
    greeting = orchestrator.personality.format_greeting(orchestrator.state.language_context.primary_language)
    console.print(f"[bold magenta]LALA:[/bold magenta] {greeting}\n")

    while True:
        try:
            lang_str = orchestrator.state.language_context.primary_language.value
            user_input = Prompt.ask(f"[bold yellow]{orchestrator.config.system.user_name} [{lang_str}][/bold yellow]")
            
            if not user_input.strip():
                continue

            cleaned_input = user_input.strip()

            if cleaned_input.lower() in ["/exit", "exit", "quit", "/quit"]:
                console.print(f"\n[bold cyan]LALA:[/bold cyan] Goodbye {orchestrator.config.system.user_name}! Shutting down cleanly.\n")
                break

            # Command: /investigate <target>
            if cleaned_input.lower().startswith("/investigate"):
                parts = cleaned_input.split(maxsplit=1)
                target = parts[1] if len(parts) > 1 else "1.1.1.1"
                res = orchestrator.tools.execute_tool("investigate_ioc", target=target)
                out = res.output or {}
                console.print(Panel(
                    f"[bold white]Cybersecurity Investigation Summary[/bold white]\n"
                    f"Case ID: {out.get('case_id')}\nTitle: {out.get('title')}\n"
                    f"Severity: [bold red]{out.get('severity')}[/bold red]\n"
                    f"Risk Score: {out.get('risk_score', {}).get('score')} / 100\n"
                    f"Evidence Items: {out.get('evidence_count')}\n\n"
                    f"Recommendations:\n" + "\n".join(out.get('recommendations', [])),
                    title="Investigation Report", border_style="red"
                ))
                continue

            # Command: /yara scan <path> | rules
            if cleaned_input.lower().startswith("/yara"):
                parts = cleaned_input.split(maxsplit=2)
                if len(parts) >= 2 and parts[1].lower() == "scan":
                    target_path = parts[2] if len(parts) >= 3 else "D:\\LALA\\lala\\core\\config.py"
                    res = orchestrator.tools.execute_tool("yara_scan", path=target_path)
                    out = res.output or {}
                    console.print(Panel(
                        f"Target Path: {out.get('target_path')}\nTotal Matches: {out.get('total_matches')}\nMatches: {out.get('matches')}",
                        title="YARA Scan Findings", border_style="yellow"
                    ))
                else:
                    rules = orchestrator.tools.tools["yara_scan"].engine.loader.load_rules()
                    console.print(Panel(f"Loaded YARA Rules under F:\\LALA\\Rules\\Yara:\n{[r['rule_name'] for r in rules]}"))
                continue

            # Command: /sigma rules
            if cleaned_input.lower().startswith("/sigma"):
                res = orchestrator.tools.execute_tool("sigma_rules")
                out = res.output or {}
                console.print(Panel(f"Loaded Sigma Rules under F:\\LALA\\Rules\\Sigma:\n{out.get('rules')}", title="Sigma Rules Metadata"))
                continue

            # Command: /online status | enable | disable
            if cleaned_input.lower().startswith("/online"):
                parts = cleaned_input.split()
                if len(parts) == 1 or parts[1].lower() == "status":
                    st = "ENABLED" if orchestrator.intel_manager.is_online_enabled() else "DISABLED"
                    console.print(Panel(f"Online Intelligence Mode: [bold white]{st}[/bold white]\nUse '/online enable' or '/online disable' to toggle."))
                elif parts[1].lower() == "enable":
                    orchestrator.intel_manager.set_online_enabled(True)
                    console.print(Panel("[bold green]Online Intelligence Mode ENABLED. Approved provider queries authorized.[/bold green]"))
                elif parts[1].lower() == "disable":
                    orchestrator.intel_manager.set_online_enabled(False)
                    console.print(Panel("[bold yellow]Online Intelligence Mode DISABLED. All external network queries blocked.[/bold yellow]"))
                continue

            # Command: /providers
            if cleaned_input.lower().startswith("/providers"):
                table = Table(title="Cybersecurity Intelligence Providers")
                table.add_column("Provider", style="cyan")
                table.add_column("API Key Present", style="yellow")
                table.add_column("Status", style="bold green")

                sec_status = orchestrator.intel_manager.secrets.get_status()
                for p_name, prov in orchestrator.intel_manager.providers.items():
                    has_key = sec_status.get(p_name, False)
                    key_str = "YES (Loaded from ENV)" if has_key else "NO (Unauthenticated)"
                    enabled_str = "ENABLED" if prov.enabled else "DISABLED"
                    table.add_row(prov.name, key_str, enabled_str)

                console.print(table)
                continue

            # Command: /agent status or /status
            if cleaned_input.lower() in ["/agent status", "/agent", "/status"]:
                dash = (
                    f"╔══════════════════════════════════════════════════╗\n"
                    f"║          LALA AGENT STATUS (Phase 7)             ║\n"
                    f"╠══════════════════════════════════════════════════╣\n"
                    f"║ Brain       Qwen 2.5 3B (Ollama Local)           ║\n"
                    f"║ Voice       Local (piped to Orchestrator)        ║\n"
                    f"║ Online Mode {'ENABLED' if orchestrator.intel_manager.is_online_enabled() else 'DISABLED (Off by default)'}                       ║\n"
                    f"║ Memory      SQLite + FTS5 ONLINE                 ║\n"
                    f"║ Security    ENFORCED (Cloud Fallback: FALSE)     ║\n"
                    f"║ Tools       {len(orchestrator.tools.list_tools())} Registered Tools                  ║\n"
                    f"║ Workspace   D:\\LALA (Python Project)              ║\n"
                    f"║ Agent       READY                                ║\n"
                    f"╚══════════════════════════════════════════════════╝"
                )
                console.print(Panel(dash, title="Agent Dashboard", border_style="cyan"))
                continue

            # Process user request through Agent Execution Loop
            console.print(f"[bold magenta]LALA:[/bold magenta] ", end="")
            response = orchestrator.process_user_input(cleaned_input)
            console.print(f"{response}\n")

        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[bold cyan]LALA:[/bold cyan] Goodbye {orchestrator.config.system.user_name}! Exiting cleanly.\n")
            break

if __name__ == "__main__":
    run_cli()
