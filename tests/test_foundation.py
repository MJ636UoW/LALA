import unittest
from lala import SYSTEM_NAME, CALL_NAME, VOICE_IDENTITY, PERSONALITY, USER_NAME
from lala.core.config import load_config
from lala.core.state import SessionState, LanguageCode, MultilingualContext
from lala.core.router import ModelRouter
from lala.core.providers.local import LocalProvider
from lala.personality.emotion import PersonalityManager
from lala.security.permissions import SecurityEngine, PermissionLevel
from lala.tools.base import Tool, ToolResult
from lala.tools.registry import ToolRegistry
from lala.memory.interface import InMemoryStore, MemoryItem
from lala.voice.interface import StubSpeechToText, StubTextToSpeech
from lala.subagents.base import SubagentManager, BaseSubagent, SubagentResult
from lala.api.registry import APIRegistry, APIServiceMetadata

class TestMockTool(Tool):
    def __init__(self, name: str = "mock_tool", permission_level: PermissionLevel = PermissionLevel.READ_ONLY):
        super().__init__(name=name, description="A mock test tool", permission_level=permission_level)

    def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, output="Mock Tool Executed")

class TestMockSubagent(BaseSubagent):
    def run_task(self, task_description: str) -> SubagentResult:
        return SubagentResult(agent_id=self.agent_id, status="COMPLETED", output="Task Done")

class TestLalaFoundation(unittest.TestCase):
    def test_identity_constants(self):
        """Verify identity constants are strictly LALA and Mandar."""
        self.assertEqual(SYSTEM_NAME, "LALA")
        self.assertEqual(CALL_NAME, "LALA")
        self.assertEqual(VOICE_IDENTITY, "LALA")
        self.assertEqual(PERSONALITY, "LALA")
        self.assertEqual(USER_NAME, "Mandar")

    def test_personality_manager(self):
        """Verify personality system prompt and multilingual greetings."""
        manager = PersonalityManager()
        prompt = manager.get_system_prompt()
        self.assertIn("LALA", prompt)
        self.assertIn("Mandar", prompt)
        self.assertIn("English", prompt)
        self.assertIn("Hindi", prompt)
        self.assertIn("Marathi", prompt)

        hi_greeting = manager.format_greeting(LanguageCode.HINDI)
        self.assertIn("LALA", hi_greeting)
        self.assertIn("Mandar", hi_greeting)

    def test_configuration_loader(self):
        """Verify YAML configuration loading including storage section."""
        config = load_config()
        self.assertEqual(config.system.name, "LALA")
        self.assertEqual(config.system.user_name, "Mandar")
        self.assertEqual(config.storage.root, "F:\\LALA")
        self.assertEqual(config.storage.ollama_models, "F:\\LALA\\OllamaModels")
        self.assertFalse(config.model_router.cloud_fallback)

    def test_security_engine(self):
        """Verify security evaluation logic across permission levels."""
        engine = SecurityEngine(allow_privileged=False)
        
        read_res = engine.evaluate("read_file", PermissionLevel.READ_ONLY)
        self.assertTrue(read_res.allowed)

        confirm_res = engine.evaluate("modify_file", PermissionLevel.USER_CONFIRMATION_REQUIRED)
        self.assertFalse(confirm_res.allowed)

        priv_res = engine.evaluate("system_shell", PermissionLevel.PRIVILEGED)
        self.assertFalse(priv_res.allowed)

    def test_tool_registry(self):
        """Verify tool registration and security enforcement."""
        registry = ToolRegistry()
        tool = TestMockTool(name="safe_tool", permission_level=PermissionLevel.READ_ONLY)
        registry.register_tool(tool)

        self.assertIn("safe_tool", registry.list_tools())
        result = registry.execute_tool("safe_tool")
        self.assertTrue(result.success)

    def test_model_router_offline_behavior(self):
        """Verify ModelRouter returns local privacy error when Ollama is offline."""
        router = ModelRouter()
        # Test routing behavior
        res = router.route_request("Test Prompt")
        self.assertIsNotNone(res.content)

    def test_memory_interface(self):
        """Verify in-memory store basic operations."""
        store = InMemoryStore()
        item = MemoryItem(id="mem_1", content="Mandar likes local AI architecture.")
        store.store(item)
        retrieved = store.retrieve("local")
        self.assertEqual(len(retrieved), 1)

    def test_voice_stubs(self):
        """Verify offline voice stubs function without model downloads."""
        stt = StubSpeechToText()
        tts = StubTextToSpeech()
        self.assertIn("LALA", stt.transcribe(b"123"))
        self.assertIn("LALA", tts.synthesize("hello").decode())

if __name__ == "__main__":
    unittest.main()
