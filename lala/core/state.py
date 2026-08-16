from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class LanguageCode(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    MARATHI = "mr"
    MIXED = "mixed"

class MultilingualContext(BaseModel):
    primary_language: LanguageCode = LanguageCode.ENGLISH
    code_switching_enabled: bool = True
    detected_languages: List[LanguageCode] = Field(default_factory=lambda: [LanguageCode.ENGLISH])

class SystemMessage(BaseModel):
    role: str # "user", "assistant", "system"
    content: str
    language: Optional[LanguageCode] = None

class SessionState(BaseModel):
    session_id: str = "default_session"
    user_name: str = "Mandar"
    agent_name: str = "LALA"
    language_context: MultilingualContext = Field(default_factory=MultilingualContext)
    history: List[SystemMessage] = Field(default_factory=list)

    def add_message(self, role: str, content: str, language: Optional[LanguageCode] = None):
        self.history.append(SystemMessage(role=role, content=content, language=language))
