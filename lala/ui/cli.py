import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from lala.core.orchestrator import Orchestrator
from lala.core.state import LanguageCode
from lala.core.providers.local import LocalProvider

console = Console()

def run_cli():
    orchestrator = Orchestrator()
    
    # Startup Health Check
    active_provider = orchestrator.router.get_active_provider()
    health = {"online": False, "model_available": False, "installed_models": []}
    
    if isinstance(active_provider, LocalProvider):
        health = active_provider.check_health()

    status_str = "[bold green]ONLINE[/bold green]" if health.get("online") else "[bold red]OFFLINE (Local Brain Unavailable)[/bold red]"
    model_name = orchestrator.config.model_router.providers.get("local", {}).model_name if orchestrator.config.model_router.providers else "qwen2.5:3b"

    banner = (
        f"[bold cyan]🧠 LALA Personal AI Operating Assistant[/bold cyan]\n"
        f"──────────────────────────────────────────────────\n"
        f"[green]Local Brain:[/green] Ollama ({orchestrator.config.model_router.providers.get('local', {}).endpoint or 'http://127.0.0.1:11434'})\n"
        f"[green]Model:[/green] [bold white]{model_name}[/bold white]\n"
        f"[green]Status:[/green] {status_str}\n"
        f"[green]Storage Root:[/green] {orchestrator.config.storage.root}\n"
        f"[yellow]Language:[/yellow] English (en) / Hindi (hi) / Marathi (mr)\n"
        f"──────────────────────────────────────────────────\n"
        f"[dim]Commands: '/status', '/model', '/lang en|hi|mr', '/exit'[/dim]"
    )
    
    console.print(Panel(banner, border_style="cyan", title="LALA Local Brain (Phase 2)"))
    
    greeting = orchestrator.personality.format_greeting(orchestrator.state.language_context.primary_language)
    console.print(f"[bold magenta]LALA:[/bold magenta] {greeting}\n")

    while True:
        try:
            lang_str = orchestrator.state.language_context.primary_language.value
            user_input = Prompt.ask(f"[bold yellow]{orchestrator.config.system.user_name} [{lang_str}][/bold yellow]")
            
            if not user_input.strip():
                continue

            cleaned_input = user_input.strip().lower()

            if cleaned_input in ["/exit", "exit", "quit", "/quit"]:
                console.print(f"\n[bold cyan]LALA:[/bold cyan] Goodbye {orchestrator.config.system.user_name}! Shutting down cleanly.\n")
                break

            # Diagnostic Command: /status
            if cleaned_input == "/status":
                h_check = active_provider.check_health() if isinstance(active_provider, LocalProvider) else {}
                status_panel = (
                    f"[bold white]LALA System Diagnostics[/bold white]\n"
                    f"Version: 0.2.0 (Phase 2 Local Brain)\n"
                    f"Provider: {orchestrator.config.model_router.active_provider}\n"
                    f"Runtime: {orchestrator.config.model_router.local_runtime}\n"
                    f"Active Model: {model_name}\n"
                    f"Ollama Endpoint: {h_check.get('endpoint', 'N/A')}\n"
                    f"Ollama Reachable: {h_check.get('online', False)}\n"
                    f"Model Loaded: {h_check.get('model_available', False)}\n"
                    f"Storage Root: {orchestrator.config.storage.root}\n"
                    f"Ollama Models Dir: {orchestrator.config.storage.ollama_models}\n"
                    f"Cloud Fallback: [bold green]FALSE (Zero Cloud Leakage)[/bold green]\n"
                    f"Languages Configured: English, Hindi, Marathi"
                )
                console.print(Panel(status_panel, title="System Diagnostics", border_style="green"))
                continue

            # Diagnostic Command: /model
            if cleaned_input == "/model":
                console.print(Panel(
                    f"[bold white]Active Local Model:[/bold white] [bold cyan]{model_name}[/bold cyan]\n"
                    f"Runtime: Ollama\n"
                    f"VRAM Footprint Target: ~2.2 GB (NVIDIA RTX 3060 6GB)",
                    title="Model Info", border_style="cyan"
                ))
                continue

            # Language switching commands
            if cleaned_input == "/lang en":
                orchestrator.set_language(LanguageCode.ENGLISH)
                console.print(Panel("[green]Language context switched to English.[/green]"))
                continue
            elif cleaned_input == "/lang hi":
                orchestrator.set_language(LanguageCode.HINDI)
                console.print(Panel("[green]भाषा संदर्भ बदलकर हिंदी (Hindi) किया गया।[/green]"))
                continue
            elif cleaned_input == "/lang mr":
                orchestrator.set_language(LanguageCode.MARATHI)
                console.print(Panel("[green]भाषा संदर्भ बदलून मराठी (Marathi) केले.[/green]"))
                continue

            # Process prompt with streaming
            console.print(f"[bold magenta]LALA:[/bold magenta] ", end="")
            
            system_prompt = orchestrator.personality.get_system_prompt(orchestrator.state.language_context)
            full_response = ""
            
            # Stream tokens from ModelRouter
            for token in orchestrator.router.route_stream(prompt=user_input, system_prompt=system_prompt):
                console.print(token, end="")
                full_response += token
                sys.stdout.flush()
            
            console.print("\n")
            orchestrator.state.add_message("user", user_input, language=orchestrator.state.language_context.primary_language)
            orchestrator.state.add_message("assistant", full_response, language=orchestrator.state.language_context.primary_language)

        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[bold cyan]LALA:[/bold cyan] Goodbye {orchestrator.config.system.user_name}! Exiting cleanly.\n")
            break

if __name__ == "__main__":
    run_cli()
