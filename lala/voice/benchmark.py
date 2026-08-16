import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from lala.voice.pipeline import VoicePipeline

console = Console()

def run_benchmark():
    console.print("[bold cyan]🧠 LALA Voice Engine Performance Audit & Benchmark[/bold cyan]\n")
    
    pipeline = VoicePipeline()
    tts_info = pipeline.tts_engine.get_info()

    # Display Active TTS Engine & Voice Discovery Info
    info_panel = (
        f"[bold white]TTS Engine Audit[/bold white]\n"
        f"Active TTS Engine: [bold cyan]{tts_info.get('active_engine')}[/bold cyan]\n"
        f"Piper Available: {tts_info.get('piper_available', False)}\n"
        f"Piper Voices Found in F:\\LALA\\Models\\TTS: {tts_info.get('piper_voices_found', 0)}\n"
        f"Model Path: {tts_info.get('model_path', 'N/A')}\n"
        f"Sample Rate: {tts_info.get('sample_rate', 22050)} Hz"
    )
    console.print(Panel(info_panel, title="Engine Status", border_style="cyan"))

    # Generate test audio buffer (1 second 16kHz audio)
    dummy_audio = b"\x00\x00" * 16000
    
    console.print("Running streaming voice pipeline benchmark...")
    result = pipeline.process_voice_utterance(dummy_audio)
    metrics = result.get("metrics", {})

    table = Table(title="Audited Voice Engine Performance Metrics")
    table.add_column("Subsystem / Metric", style="cyan")
    table.add_column("Measured Time", style="bold green")
    table.add_column("Description", style="dim")

    table.add_row("STT Transcription", f"{metrics.get('stt_latency', 0.0):.3f} s", "Mic audio -> Text transcript")
    table.add_row("LLM First Token", f"{metrics.get('llm_first_token_latency', 0.0):.3f} s", "Ollama qwen2.5:3b first token")
    table.add_row("Time To First Audio (TTFA)", f"{metrics.get('tts_ttfa', 0.0):.3f} s", "Time until sound output begins")
    table.add_row("TTS Synthesis Overhead", f"{metrics.get('tts_synthesis_overhead', 0.0):.3f} s", "Pure text-to-audio synthesis time")
    table.add_row("Spoken Playback Duration", f"{metrics.get('audio_playback_duration', 0.0):.3f} s", "Natural soundcard playback time")
    table.add_row("Total End-to-End Latency", f"{metrics.get('total_latency', 0.0):.3f} s", "Complete voice interaction cycle")

    console.print(table)
    console.print("\n[green]Audit and benchmark complete.[/green]")

if __name__ == "__main__":
    run_benchmark()
