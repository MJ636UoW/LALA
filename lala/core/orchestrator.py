from typing import Optional, List
from lala.core.config import LalaConfig, load_config
from lala.core.state import SessionState, LanguageCode
from lala.core.router import ModelRouter
from lala.personality.emotion import PersonalityManager
from lala.security.permissions import SecurityEngine
from lala.tools.registry import ToolRegistry
from lala.tools.planner import ToolPlanner
from lala.tools.executor import ToolExecutor
from lala.memory.manager import MemoryManager
from lala.utils.logging import logger

MAX_TOOL_ITERATIONS = 5

class Orchestrator:
    """
    Central pipeline orchestrator for LALA Phase 4.
    Coordinates User Input -> Persistent Memory Retrieval -> Model Router -> Tool Planner -> Security Check -> Tool Executor -> Multi-step Loop -> Final Response.
    """
    def __init__(self, config: Optional[LalaConfig] = None):
        self.config = config or load_config()
        self.personality = PersonalityManager()
        self.security = SecurityEngine(allow_privileged=self.config.security.allow_privileged_execution)
        self.router = ModelRouter(config=self.config.model_router)
        self.tools = ToolRegistry(security_engine=self.security)
        self.planner = ToolPlanner()
        self.executor = ToolExecutor(registry=self.tools)
        self.memory = MemoryManager(db_path=self.config.storage.memory_path)
        self.state = SessionState(
            user_name=self.config.system.user_name,
            agent_name=self.config.system.name
        )

    def set_language(self, language_code: LanguageCode):
        self.state.language_context.primary_language = language_code

    def process_user_input(self, user_input: str) -> str:
        # Record user message in session state
        self.state.add_message("user", user_input, language=self.state.language_context.primary_language)
        
        # 1. Retrieve relevant persistent memories
        retrieved_memories = self.memory.search_memory(user_input, limit=3)
        memory_str = "\n".join([f"- {m.content}" for m in retrieved_memories]) if retrieved_memories else "None"

        # 2. Build system prompt from PersonalityManager & inject memory context
        base_system_prompt = self.personality.get_system_prompt(self.state.language_context)
        system_prompt = (
            f"{base_system_prompt}\n\n"
            f"[RELEVANT PERSISTENT MEMORY]\n{memory_str}\n\n"
            f"[AVAILABLE TOOLS]: {', '.join(self.tools.list_tools())}\n"
            f"If you need a tool, output a JSON tool call format: ```json {{\"tool\": \"tool_name\", \"arguments\": {{...}}, \"reason\": \"...\"}} ```"
        )
        
        # 3. Agent Execution Loop
        current_prompt = user_input
        iterations = 0
        final_response = ""

        while iterations < MAX_TOOL_ITERATIONS:
            iterations += 1
            response = self.router.route_request(prompt=current_prompt, system_prompt=system_prompt)
            final_response = response.content

            # Check if model requested a tool execution
            tool_req = self.planner.parse_tool_call(final_response)
            if not tool_req:
                break

            logger.info(f"Agent Loop Iteration {iterations}: Model requested tool '{tool_req.tool}'")
            tool_res = self.executor.execute_request(tool_req)

            if tool_res.success:
                current_prompt = f"Tool '{tool_req.tool}' executed successfully. Output: {tool_res.output}\nNow provide the answer to Mandar."
            else:
                current_prompt = f"Tool '{tool_req.tool}' failed or required permission. Error: {tool_res.error}\nExplain this to Mandar."

        # Record assistant output in session state
        self.state.add_message("assistant", final_response, language=self.state.language_context.primary_language)
        return final_response
