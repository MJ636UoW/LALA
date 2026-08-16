import time
from rich.console import Console
from rich.table import Table
from lala.voice.pipeline import VoicePipeline
from lala.voice.stt import StubSpeechToText
from lala.voice.tts import NativePyttsx3TTS

console = Console()

def run_benchmark():
    console.print("[bold cyan]🧠 LALA Voice Engine Performance Benchmark[/bold cyan]\n")
    
    pipeline = VoicePipeline()
    
    # Generate dummy audio buffer (1 second 16kHz audio)
    dummy_audio = b"\x00\x00" * 16000
    
    console.print("Running end-to-end benchmark test...")
    result = pipeline.process_voice_utterance(dummy_audio)
    metrics = result.get("metrics", {})

    table = Table(title="Measured Performance Metrics")
    table.add_column("Subsystem", style="cyan")
    table.add_column("Measured Latency", style="bold green")
    table.add_column("Notes", style="dim")

    table.add_row("STT Transcription", f"{metrics.get('stt_latency', 0.0):.3f} s", "Mic audio -> Text transcript")
    table.add_row("LLM Generation", f"{metrics.get('llm_first_token_latency', 0.0):.3f} s", "Ollama qwen2.5:3b response")
    table.add_row("TTS Synthesis & Audio", f"{metrics.get('tts_latency', 0.0):.3f} s", "Text -> Local Audio Playback")
    table.add_row("Total End-to-End Latency", f"{metrics.get('total_latency', 0.0):.3f} s", "Complete voice interaction cycle")

    console.print(table)
    console.print("\n[green]Benchmark complete.[/green]")

if __name__ == "__main__":
    run_benchmark()
