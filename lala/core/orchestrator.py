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
from lala.workspace.scanner import WorkspaceScanner
from lala.workspace.context import format_workspace_prompt_context
from lala.agent.planner import TaskPlanner
from lala.agent.executor import AgentExecutor, MAX_AGENT_STEPS
from lala.intelligence.manager import IntelligenceManager
from lala.investigation.manager import InvestigationManager
from lala.llm.manager import LocalLLMManager
from lala.rag.manager import LocalRAGManager
from lala.automation.workflow import AutonomousWorkflowEngine
from lala.utils.logging import logger

MAX_TOOL_ITERATIONS = 5

class Orchestrator:
    """
    Central pipeline orchestrator for LALA Phase 10.
    Coordinates User Goal -> Memory -> Workspace -> Offline Local RAG -> Autonomous Security Automation -> Local LLM -> Security Engine -> Response.
    Enforces 100% Local Inference, Safe Autonomous Automation Policy, and Privacy.
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
        self.memory = MemoryManager(db_path=self.config.storage.memory_path)
        self.workspace_scanner = WorkspaceScanner(root_path="D:\\LALA")
        self.task_planner = TaskPlanner()
        self.agent_executor = AgentExecutor(executor=self.executor)
        self.state = SessionState(
            user_name=self.config.system.user_name,
            agent_name=self.config.system.name
        )

    def set_language(self, language_code: LanguageCode):
        self.state.language_context.primary_language = language_code

    def process_user_input(self, user_input: str) -> str:
        # Record user message in session state
        self.state.add_message("user", user_input, language=self.state.language_context.primary_language)
        
        # 1. Retrieve workspace context & persistent memories & local RAG evidence
        ws_ctx = self.workspace_scanner.scan("D:\\LALA")
        ws_prompt_block = format_workspace_prompt_context(ws_ctx)

        retrieved_memories = self.memory.search_memory(user_input, limit=3)
        memory_str = "\n".join([f"- {m.content}" for m in retrieved_memories]) if retrieved_memories else "None"

        # 2. Build system prompt & inject RAG context
        base_system_prompt = self.personality.get_system_prompt(self.state.language_context)
        system_prompt_with_context = (
            f"{base_system_prompt}\n\n"
            f"{ws_prompt_block}\n\n"
            f"[RELEVANT PERSISTENT MEMORY]\n{memory_str}\n\n"
            f"[AVAILABLE TOOLS]: {', '.join(self.tools.list_tools())}\n"
            f"If you need a tool, output a JSON tool call format: ```json {{\"tool\": \"tool_name\", \"arguments\": {{...}}, \"reason\": \"...\"}} ```"
        )
        
        system_prompt = self.rag_manager.build_prompt_context(system_prompt_with_context, user_input, top_k=8)

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
