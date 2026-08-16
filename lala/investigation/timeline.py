from lala.investigation.models import TimelineEntry

class TimelineGenerator:
    """Helper for logging chronological event entries to an investigation case."""
    def log_event(self, description: str, actor: str = "LALA Agent") -> TimelineEntry:
        return TimelineEntry(event_description=description, actor=actor)
