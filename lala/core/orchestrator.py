import os
from typing import Optional, List, Dict, Any
from lala.core.config import LalaConfig, load_config
from lala.core.state import SessionState, LanguageCode
from lala.core.router import ModelRouter
from lala.personality.emotion import PersonalityManager
from lala.security.permissions import SecurityEngine
from lala.tools.registry import ToolRegistry
from lala.tools.planner import ToolPlanner
from lala.tools.executor import ToolExecutor
from lala.memory.manager import MemoryManager
from lala.workspace.scanner import WorkspaceScanner
from lala.workspace.context import format_workspace_prompt_context
from lala.agent.planner import TaskPlanner
from lala.agent.executor import AgentExecutor, MAX_AGENT_STEPS
from lala.intelligence.manager import IntelligenceManager
from lala.investigation.manager import InvestigationManager
from lala.llm.manager import LocalLLMManager
from lala.rag.manager import LocalRAGManager
from lala.automation.workflow import AutonomousWorkflowEngine
from lala.tools.web import WebSearchTool
from lala.utils.logging import logger

MAX_TOOL_ITERATIONS = 5

RESET_TOPIC_PHRASES = [
    "end of topic", "end of that topic", "new topic", 
    "reset chat", "reset topic", "start new topic", "clear chat"
]

SEARCH_KEYWORDS = ["search", "google", "find", "strength of", "who is", "what is", "latest", "news", "website", "online"]

class Orchestrator:
    """
    Central pipeline orchestrator for LALA — Uncensored ChatGPT Partner with Live Web Browsing.
    Coordinates User Goal -> Automatic Web Search -> Multi-Session Chat Memory -> Model Generation.
    """
    def __init__(self, config: Optional[LalaConfig] = None):
        self.config = config or load_config()
        self.personality = PersonalityManager()
        self.security = SecurityEngine(allow_privileged=self.config.security.allow_privileged_execution)
        self.router = ModelRouter(config=self.config.model_router)
        self.local_llm_manager = LocalLLMManager()
        self.rag_manager = LocalRAGManager()
        self.automation = AutonomousWorkflowEngine()
        self.intel_manager = IntelligenceManager(online_enabled=self.config.security.online_intelligence_enabled)
        self.investigation_manager = InvestigationManager()
        self.tools = ToolRegistry(security_engine=self.security, intel_manager=self.intel_manager)
        self.planner = ToolPlanner()
        self.executor = ToolExecutor(registry=self.tools)
        self.web_search_tool = WebSearchTool()
        self.memory = MemoryManager(db_path=self.config.storage.memory_path)
        
        default_root = "D:\\LALA" if os.path.exists("D:\\LALA") else os.path.realpath(os.getcwd())
        self.workspace_scanner = WorkspaceScanner(root_path=default_root)
        self.task_planner = TaskPlanner()
        self.agent_executor = AgentExecutor(executor=self.executor)
        
        # Session Store for Multi-Turn Chat History
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.state = SessionState(
            user_name=self.config.system.user_name,
            agent_name=self.config.system.name
        )

    def set_language(self, language_code: LanguageCode):
        self.state.language_context.primary_language = language_code

    def reset_session(self, session_id: str = "default"):
        self.sessions[session_id] = []

    def get_history(self, session_id: str = "default") -> List[Dict[str, str]]:
        return self.sessions.get(session_id, [])

    def process_user_input(self, user_input: str, session_id: str = "default") -> str:
        clean_input = user_input.strip()
        lower_input = clean_input.lower()

        # Check Topic Reset Phrases
        if any(phrase in lower_input for phrase in RESET_TOPIC_PHRASES):
            self.reset_session(session_id)
            return "Topic reset acknowledged. Fresh chat started. What shall we do next, Mandar?"

        # Initialize session history if not present
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        history = self.sessions[session_id]

        # Check if live web search should be auto-triggered
        web_context = ""
        is_search_query = any(k in lower_input for k in SEARCH_KEYWORDS) or "google" in lower_input
        if is_search_query:
            logger.info(f"Orchestrator: Auto-executing live web search for '{clean_input}'")
            search_res = self.web_search_tool.execute(query=clean_input)
            if search_res.success and search_res.output:
                web_context = f"\n[LIVE WEB SEARCH RESULTS FROM GOOGLE/DUCKDUCKGO]\n{search_res.output}\n\n"

        # Format conversation history block (last 8 messages for speed & context)
        history_block = ""
        if history:
            history_lines = []
            for item in history[-8:]:
                role = "Mandar" if item["role"] == "user" else "LALA"
                history_lines.append(f"{role}: {item['content']}")
            history_block = f"[CONVERSATION HISTORY]\n" + "\n".join(history_lines) + "\n\n"

        # Build system prompt with history and live web search context
        base_system_prompt = self.personality.get_system_prompt(self.state.language_context)
        system_prompt_with_history = f"{base_system_prompt}\n\n{web_context}{history_block}"
        
        system_prompt = self.rag_manager.build_prompt_context(system_prompt_with_history, clean_input, top_k=3)

        # Agent Execution Loop
        current_prompt = clean_input
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
                current_prompt = f"Tool '{tool_req.tool}' output: {tool_res.output}\nAnswer Mandar directly."
            else:
                current_prompt = f"Tool '{tool_req.tool}' error: {tool_res.error}\nExplain this to Mandar."

        # Update Session History
        self.sessions[session_id].append({"role": "user", "content": clean_input})
        self.sessions[session_id].append({"role": "assistant", "content": final_response})

        return final_response
