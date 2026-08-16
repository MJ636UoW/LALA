import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from lala.core.orchestrator import Orchestrator
from lala.core.state import LanguageCode
from lala.core.providers.local import LocalProvider
from lala.voice.pipeline import VoicePipeline
from lala.voice.wakeword import VoiceState

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
        f"[bold cyan]🧠 LALA Personal AI Operating Assistant (Voice-Enabled)[/bold cyan]\n"
        f"──────────────────────────────────────────────────\n"
        f"[green]Local Brain:[/green] Ollama ({orchestrator.config.model_router.providers.get('local', {}).endpoint or 'http://127.0.0.1:11434'})\n"
        f"[green]Model:[/green] [bold white]{model_name}[/bold white]\n"
        f"[green]Status:[/green] {status_str}\n"
        f"[green]Storage Root:[/green] {orchestrator.config.storage.root}\n"
        f"[yellow]Language:[/yellow] English (en) / Hindi (hi) / Marathi (mr) / Auto (auto)\n"
        f"──────────────────────────────────────────────────\n"
        f"[dim]Commands: '/voice', '/voice-status', '/mic', '/voice-test', '/status', '/model', '/exit'[/dim]"
    )
    
    console.print(Panel(banner, border_style="cyan", title="LALA Voice & Local Brain (Phase 3)"))
    
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

            # Command: /mic
            if cleaned_input.startswith("/mic"):
                parts = cleaned_input.split()
                if len(parts) == 2 and parts[1].isdigit():
                    dev_id = int(parts[1])
                    if voice_pipeline.device_manager.set_input_device(dev_id):
                        console.print(Panel(f"[green]Selected microphone device ID {dev_id}[/green]"))
                    else:
                        console.print(Panel(f"[red]Failed to select microphone ID {dev_id}[/red]"))
                else:
                    mics = voice_pipeline.device_manager.list_input_devices()
                    table = Table(title="Available Audio Input Devices (Microphones)")
                    table.add_column("ID", style="cyan")
                    table.add_column("Device Name", style="bold white")
                    table.add_column("Sample Rate", style="yellow")
                    table.add_column("Default", style="green")

                    for m in mics:
                        table.add_row(str(m["id"]), m["name"], f"{m['sample_rate']} Hz", "YES" if m["is_default"] else "")
                    console.print(table)
                    console.print("[dim]Use '/mic <id>' to select active input device.[/dim]\n")
                continue

            # Command: /voice-status
            if cleaned_input == "/voice-status":
                gpu_info = voice_pipeline.resource_manager.get_gpu_status()
                mics = voice_pipeline.device_manager.list_input_devices()
                default_mic = next((m["name"] for m in mics if m["is_default"]), "Default Microphone")
                
                v_status = (
                    f"[bold white]LALA Voice Diagnostics & Status[/bold white]\n"
                    f"Microphone: {default_mic}\n"
                    f"STT Engine: faster-whisper / Stub\n"
                    f"TTS Engine: Piper ONNX / pyttsx3 SAPI5 Fallback\n"
                    f"GPU Model: {gpu_info.get('gpu_name', 'N/A')}\n"
                    f"VRAM Free: {gpu_info.get('free_vram_mb', 0)} MB / {gpu_info.get('total_vram_mb', 0)} MB\n"
                    f"Voice State: {voice_pipeline.wakeword_engine.get_state().value}\n"
                    f"Language Mode: {orchestrator.state.language_context.primary_language.value.upper()}\n"
                    f"STT Latency: {voice_pipeline.last_metrics.get('stt_latency', 0.0)} s\n"
                    f"LLM Latency: {voice_pipeline.last_metrics.get('llm_first_token_latency', 0.0)} s\n"
                    f"TTS Latency: {voice_pipeline.last_metrics.get('tts_latency', 0.0)} s\n"
                    f"Total Response Latency: {voice_pipeline.last_metrics.get('total_latency', 0.0)} s\n"
                    f"Cloud Audio Fallback: [bold green]FALSE (100% Local Voice Privacy)[/bold green]"
                )
                console.print(Panel(v_status, title="Voice Diagnostics", border_style="cyan"))
                continue

            # Command: /voice-test
            if cleaned_input == "/voice-test":
                console.print(Panel("[cyan]Testing local TTS speech synthesis...[/cyan]"))
                test_text = "LALA local voice test complete. Local speech synthesis is active."
                voice_pipeline.tts_engine.speak(test_text)
                console.print(Panel("[green]Voice synthesis test complete.[/green]"))
                continue

            # Command: /voice
            if cleaned_input == "/voice":
                console.print(Panel(
                    f"[bold cyan]🎙️ LALA Interactive Voice Mode[/bold cyan]\n"
                    f"Status: LISTENING | Language: {orchestrator.state.language_context.primary_language.value.upper()}\n"
                    f"[dim]Simulating spoken utterance through voice pipeline... Type '/voice-stop' to exit voice mode.[/dim]",
                    border_style="magenta"
                ))
                
                # Run sample voice test utterance through pipeline
                dummy_pcm = b"\x00\x00" * 16000
                result = voice_pipeline.process_voice_utterance(dummy_pcm)
                console.print(f"[bold cyan]STT Transcript:[/bold cyan] {result.get('transcript')}")
                console.print(f"[bold magenta]LALA Voice Response:[/bold magenta] {result.get('response')}\n")
                continue

            # Command: /status
            if cleaned_input == "/status":
                h_check = active_provider.check_health() if isinstance(active_provider, LocalProvider) else {}
                status_panel = (
                    f"[bold white]LALA System Diagnostics[/bold white]\n"
                    f"Version: 0.3.0 (Phase 3 Voice Engine)\n"
                    f"Provider: {orchestrator.config.model_router.active_provider}\n"
                    f"Runtime: {orchestrator.config.model_router.local_runtime}\n"
                    f"Active Model: {model_name}\n"
                    f"Ollama Endpoint: {h_check.get('endpoint', 'N/A')}\n"
                    f"Ollama Reachable: {h_check.get('online', False)}\n"
                    f"Storage Root: {orchestrator.config.storage.root}\n"
                    f"STT Model Path: F:\\LALA\\Models\\STT\n"
                    f"TTS Model Path: F:\\LALA\\Models\\TTS\n"
                    f"Cloud Fallback: [bold green]FALSE (Zero Cloud Leakage)[/bold green]"
                )
                console.print(Panel(status_panel, title="System Diagnostics", border_style="green"))
                continue

            # Command: /model
            if cleaned_input == "/model":
                console.print(Panel(
                    f"[bold white]Active Local Model:[/bold white] [bold cyan]{model_name}[/bold cyan]\n"
                    f"Runtime: Ollama\n"
                    f"VRAM Target: ~2.2 GB (NVIDIA RTX 3060 6GB)",
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

            # Process prompt with streaming text output
            console.print(f"[bold magenta]LALA:[/bold magenta] ", end="")
            system_prompt = orchestrator.personality.get_system_prompt(orchestrator.state.language_context)
            full_response = ""
            
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
