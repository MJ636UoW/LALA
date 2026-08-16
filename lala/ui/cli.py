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
    
    # Startup Health Check
    active_provider = orchestrator.router.get_active_provider()
    health = {"online": False, "model_available": False, "installed_models": []}
    
    if isinstance(active_provider, LocalProvider):
        health = active_provider.check_health()

    status_str = "[bold green]ONLINE[/bold green]" if health.get("online") else "[bold red]OFFLINE (Local Brain Unavailable)[/bold red]"
    model_name = orchestrator.config.model_router.providers.get("local", {}).model_name if orchestrator.config.model_router.providers else "qwen2.5:3b"

    banner = (
        f"[bold cyan]🧠 LALA Controlled Autonomous Agent (Phase 5)[/bold cyan]\n"
        f"──────────────────────────────────────────────────\n"
        f"[green]Local Brain:[/green] Ollama ({orchestrator.config.model_router.providers.get('local', {}).endpoint or 'http://127.0.0.1:11434'})\n"
        f"[green]Model:[/green] [bold white]{model_name}[/bold white] | [green]Status:[/green] {status_str}\n"
        f"[green]Workspace Intelligence:[/green] [bold green]ONLINE[/bold green] (D:\\LALA)\n"
        f"[green]Task Execution Limits:[/green] Max Agent Steps = [bold white]{MAX_AGENT_STEPS}[/bold white] | Sub-step Tool Cap = [bold white]{MAX_TOOL_ITERATIONS}[/bold white]\n"
        f"[green]Defensive Cybersecurity Scanner:[/green] ACTIVE\n"
        f"[green]Security Engine:[/green] ENFORCED (Zero Cloud Fallback)\n"
        f"──────────────────────────────────────────────────\n"
        f"[dim]Commands: '/agent status', '/workspace scan', '/task <goal>', '/security scan', '/tools', '/memory', '/exit'[/dim]"
    )
    
    console.print(Panel(banner, border_style="cyan", title="LALA Controlled Autonomous Agent"))
    
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

            # Command: /agent status or /status
            if cleaned_input.lower() in ["/agent status", "/agent", "/status"]:
                mem_stats = orchestrator.memory.get_status()
                dash = (
                    f"╔══════════════════════════════════════════════════╗\n"
                    f"║            LALA AGENT STATUS (Phase 5)           ║\n"
                    f"╠══════════════════════════════════════════════════╣\n"
                    f"║ Brain       Qwen 2.5 3B (Ollama Local)           ║\n"
                    f"║ Voice       Local (piped to Orchestrator)        ║\n"
                    f"║ Memory      SQLite + FTS5 ONLINE                 ║\n"
                    f"║ Security    ENFORCED (Cloud Fallback: FALSE)     ║\n"
                    f"║ Tools       {len(orchestrator.tools.list_tools())} Registered Tools                   ║\n"
                    f"║ Workspace   D:\\LALA (Python Project)              ║\n"
                    f"║ Agent       READY                                ║\n"
                    f"║ Max Steps   {MAX_AGENT_STEPS}                                    ║\n"
                    f"║ Tool Limit  {MAX_TOOL_ITERATIONS}                                    ║\n"
                    f"╚══════════════════════════════════════════════════╝"
                )
                console.print(Panel(dash, title="Agent Dashboard", border_style="cyan"))
                continue

            # Command: /workspace scan or /workspace info
            if cleaned_input.lower().startswith("/workspace"):
                parts = cleaned_input.split()
                target = "D:\\LALA"
                if len(parts) >= 3:
                    target = parts[2]
                ctx = orchestrator.workspace_scanner.scan(target)
                ws_table = Table(title=f"Workspace Intelligence Summary for '{target}'")
                ws_table.add_column("Property", style="cyan")
                ws_table.add_column("Detected Value", style="bold white")

                ws_table.add_row("Root Path", ctx.root_path)
                ws_table.add_row("Project Type", ctx.project_type.value)
                ws_table.add_row("Languages", ", ".join(ctx.languages_detected))
                ws_table.add_row("Git Repository", "YES" if ctx.git_detected else "NO")
                ws_table.add_row("Total Files", str(ctx.total_files))
                ws_table.add_row("Python Files", str(ctx.python_files_count))
                ws_table.add_row("Test Suite Files", str(ctx.tests_count))
                ws_table.add_row("Config Files", ", ".join(ctx.config_files[:5]))
                console.print(ws_table)
                continue

            # Command: /security scan or /security findings
            if cleaned_input.lower().startswith("/security"):
                res = orchestrator.tools.execute_tool("security_scan", path="D:\\LALA")
                out = res.output or {}
                console.print(Panel(
                    f"[bold white]Defensive Static Cybersecurity Audit[/bold white]\n"
                    f"Total Findings: {out.get('total_findings', 0)}\n"
                    f"High Severity: {out.get('high_count', 0)}\n"
                    f"Medium Severity: {out.get('medium_count', 0)}\n\n"
                    f"Top Findings: {out.get('findings', [])[:3]}",
                    title="Security Report", border_style="yellow"
                ))
                continue

            # Command: /task <goal>
            if cleaned_input.lower().startswith("/task "):
                goal = cleaned_input[6:].strip()
                plan = orchestrator.task_planner.create_plan_for_goal(goal)
                
                table = Table(title=f"Structured Task Plan for: '{goal}'")
                table.add_column("Step #", style="cyan")
                table.add_column("Action", style="bold white")
                table.add_column("Tool", style="yellow")
                table.add_column("Risk Level", style="bold green")

                for step in plan.steps:
                    table.add_row(str(step.step_number), step.action, step.tool or "N/A", step.risk.value)

                console.print(table)
                console.print("\n[bold cyan]Executing planned task steps...[/bold cyan]\n")
                result = orchestrator.agent_executor.execute_plan(plan)
                
                status_color = "green" if result.success else "red"
                console.print(Panel(
                    f"Success: {result.success}\nSteps Executed: {result.steps_executed}\nVerification Passed: {result.verification_passed}\nOutput:\n{result.final_output}",
                    title="Task Execution Result", border_style=status_color
                ))
                orchestrator.memory.record_task_history(plan.plan_id[:8], goal, "COMPLETED" if result.success else "FAILED", result.final_output)
                continue

            # Standard tools and commands
            if cleaned_input.lower() in ["/tools", "/tool-status"]:
                table = Table(title="Registered Safe Agent Tools")
                table.add_column("Tool Name", style="cyan")
                table.add_column("Category", style="yellow")
                table.add_column("Permission Tier", style="bold green")
                table.add_column("Risk Description", style="dim")

                for t_name in orchestrator.tools.list_tools():
                    tool = orchestrator.tools.get_tool(t_name)
                    if tool:
                        table.add_row(tool.name, tool.category, tool.permission_level.value, tool.risk_description)
                console.print(table)
                continue

            if cleaned_input.lower().startswith("/memory"):
                mem_stats = orchestrator.memory.get_status()
                console.print(Panel(f"SQLite Memory Store: {mem_stats['total_memories']} items saved, {mem_stats['tasks_recorded']} tasks recorded."))
                continue

            # Language switching
            if cleaned_input.lower() == "/lang en":
                orchestrator.set_language(LanguageCode.ENGLISH)
                console.print(Panel("[green]Language context switched to English.[/green]"))
                continue
            elif cleaned_input.lower() == "/lang hi":
                orchestrator.set_language(LanguageCode.HINDI)
                console.print(Panel("[green]भाषा संदर्भ बदलकर हिंदी (Hindi) किया गया।[/green]"))
                continue
            elif cleaned_input.lower() == "/lang mr":
                orchestrator.set_language(LanguageCode.MARATHI)
                console.print(Panel("[green]भाषा संदर्भ बदलून मराठी (Marathi) केले.[/green]"))
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
