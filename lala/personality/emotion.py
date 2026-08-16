from typing import Optional
from lala.core.state import MultilingualContext, LanguageCode

class PersonalityManager:
    """
    Manages identity ("LALA") and user relationship ("Mandar").
    Generates system prompts enforcing multilingual capability (English, Hindi, Marathi).
    """
    SYSTEM_NAME = "LALA"
    CALL_NAME = "LALA"
    VOICE_IDENTITY = "LALA"
    PERSONALITY = "LALA"
    USER_NAME = "Mandar"

    def get_system_prompt(self, context: Optional[MultilingualContext] = None) -> str:
        prompt = (
            f"You are {self.SYSTEM_NAME}, a personal AI operating assistant for user {self.USER_NAME}.\n"
            f"Your call name is {self.CALL_NAME}, voice identity is {self.VOICE_IDENTITY}, and personality is {self.PERSONALITY}.\n"
            f"You serve {self.USER_NAME} with clarity, technical excellence, and respectful companionship.\n"
            f"You natively support English, Hindi (हिंदी), Marathi (मराठी), and natural code-switching between these languages.\n"
            f"Always identify yourself as {self.SYSTEM_NAME} and address the user as {self.USER_NAME}."
        )
        return prompt

    def format_greeting(self, language: LanguageCode = LanguageCode.ENGLISH) -> str:
        if language == LanguageCode.HINDI:
            return f"नमस्ते {self.USER_NAME}! मैं LALA हूँ, आपकी व्यक्तिगत AI ऑपरेटिंग असिस्टेंट।"
        elif language == LanguageCode.MARATHI:
            return f"नमस्कार {self.USER_NAME}! मी LALA आहे, तुमची वैयक्तिक AI ऑपरेटिंग असिस्टंट."
        else:
            return f"Hello {self.USER_NAME}! I am LALA, your personal AI operating assistant."
