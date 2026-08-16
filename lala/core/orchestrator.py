from typing import Optional
from lala.core.config import LalaConfig, load_config
from lala.core.state import SessionState, LanguageCode, SystemMessage
from lala.core.router import ModelRouter
from lala.personality.emotion import PersonalityManager
from lala.security.permissions import SecurityEngine
from lala.tools.registry import ToolRegistry
from lala.memory.interface import InMemoryStore

class Orchestrator:
    """
    Central pipeline orchestrator for LALA.
    Coordinates configuration, identity, model routing, security evaluation, and memory context.
    """
    def __init__(self, config: Optional[LalaConfig] = None):
        self.config = config or load_config()
        self.personality = PersonalityManager()
        self.security = SecurityEngine(allow_privileged=self.config.security.allow_privileged_execution)
        self.router = ModelRouter(config=self.config.model_router)
        self.tools = ToolRegistry(security_engine=self.security)
        self.memory = InMemoryStore()
        self.state = SessionState(
            user_name=self.config.system.user_name,
            agent_name=self.config.system.name
        )

    def set_language(self, language_code: LanguageCode):
        self.state.language_context.primary_language = language_code

    def process_user_input(self, user_input: str) -> str:
        # Record user message in session state
        self.state.add_message("user", user_input, language=self.state.language_context.primary_language)
        
        # Build system prompt from PersonalityManager
        system_prompt = self.personality.get_system_prompt(self.state.language_context)
        
        # Route query through ModelRouter
        response = self.router.route_request(prompt=user_input, system_prompt=system_prompt)
        
        # Record assistant output in session state
        self.state.add_message("assistant", response.content, language=self.state.language_context.primary_language)
        
        return response.content
