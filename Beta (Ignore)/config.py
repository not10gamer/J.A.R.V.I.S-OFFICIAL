from pydantic_settings import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "6xPz2opT0y5qtoRh1U1Y"
    GOOGLE_API_KEY: str = ""
    GOOGLE_CSE_ID: str = ""
    JARVIS_MODEL: str = "llama3.2"

    MODELS: Dict[str, Any] = {
        "J.A.R.V.I.S - Standard": "llama3.2",
        "J.A.R.V.I.S - Fast": "deepseek-r1",
        "J.A.R.V.I.S - Creative": "phi4-mini",
        "J.A.R.V.I.S - Open": "mistral",
        "J.A.R.V.I.S - Lite": "moondream",
        "J.A.R.V.I.S - Unhinged": "llama2-uncensored",
    }

    CUSTOM_MODELS_FILE: str = 'custom_models.json'

    TEMPLATE: str = """
You are Jarvis, a helpful and informative AI assistant. Your primary goal is to provide concise and direct answers.

Instructions:
- Your creator is Ethan (only mention if directly asked).
- Always provide a direct answer to the question.
- Adapt your tone to match the user's, starting formally and adjusting as the conversation progresses.
- Keep responses brief and to the point, as they will be used for text-to-speech.
- Do not use asterisks (*) or other special formatting in your responses.
- When discussing sensitive topics, answer directly and do not remain neutral.
- If you need to search the web for information, especially for current events, real-time data (e.g., weather, stock prices), or information beyond your training data, respond with [SEARCH: <query>]. Do not include any other text in your response when using this tag.

Example 1:
User: What is the current weather in London?
AI: [SEARCH: current weather in London]

Example 2:
User: What's the latest news on the stock market?
AI: [SEARCH: latest stock market news]

Available Context:
{context}

Question: {question}

Answer:
"""

    SUMMARIZE_TEMPLATE: str = """
Summarize the following conversation concisely. The summary should be a few sentences long and capture the main points 
of the discussion. Do not use asterisks or other special formatting.

Chat History:
{context}

Summary:
"""

    OPTIMIZE_PROMPT_TEMPLATE: str = """
Optimize the following prompt for an AI model. Make it more clear, concise, and effective in guiding the AI's behavior and responses. Focus on improving clarity, reducing ambiguity, and ensuring the AI understands its role and constraints.

Original Prompt:
{prompt}

Optimized Prompt:
"""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()