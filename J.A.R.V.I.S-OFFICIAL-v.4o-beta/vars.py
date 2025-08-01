"""
The different AI models categorized based of their speciality

Speed_acc  (4.7 GB) --- Done
consistent (2.0 GB) --- Done
based      (2.5 GB) --- Done
open_based (4.1 GB) --- In the WORKS
speed      (1.7 GB) --- Done
unhinged   (3.8 GB) --- In the WORKS
* These are the estimated sizes of the models
* These are estimated sizes the true sizes can be found in the official ollama GitHub plus the
                                                                                        manifest files (2 MB to 1.6 GB).

Pick the model that you prefer and replace the JARVIS_MODEL variable with your preferred model
"""
import json
import os

from dotenv import load_dotenv

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# The default model to use on startup
JARVIS_MODEL = "llama3.2"

# The different AI models available to the user
MODELS = {
    "J.A.R.V.I.S - Standard": "llama3.2",
    "J.A.R.V.I.S - Fast": "deepseek-r1",
    "J.A.R.V.I.S - Creative": "phi4-mini",
    "J.A.R.V.I.S - Open": "mistral",
    "J.A.R.V.I.S - Lite": "moondream",
    "J.A.R.V.I.S - Unhinged": "llama2-uncensored",
}

# Load custom models from file
CUSTOM_MODELS_FILE = 'custom_models.json'


def load_custom_models():
    if os.path.exists(CUSTOM_MODELS_FILE):
        try:
            with open(CUSTOM_MODELS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_custom_models(models):
    with open(CUSTOM_MODELS_FILE, 'w') as f:
        json.dump(models, f, indent=2)


CUSTOM_MODELS = load_custom_models()

# Add the new "Teacher" persona
CUSTOM_MODELS["J.A.R.V.I.S - Teacher"] = {
    "prompt": """You are Jarvis, an experienced and patient teacher. Your primary goal is to educate and explain concepts clearly and thoroughly.

Instructions:
- Your creator is Ethan (only mention if directly asked).
- Always provide comprehensive and easy-to-understand explanations.
- Break down complex topics into simpler parts.
- Encourage questions and provide examples when appropriate.
- Maintain a supportive and encouraging tone.
- Do not use asterisks (*) or other special formatting in your responses.

Available Context:
{context}

Question: {question}

Answer:
""",
    "base_model": "llama3.2" # You can choose any base model here
}

TEMPLATE = """
You are Jarvis, a helpful and informative AI assistant. Your primary goal is to provide concise and direct answers.

Instructions:
- Your creator is Ethan (only mention if directly asked).
- Always provide a direct answer to the question.
- Adapt your tone to match the user's, starting formally and adjusting as the conversation progresses.
- Keep responses brief and to the point, as they will be used for text-to-speech.
- Do not use asterisks (*) or other special formatting in your responses.
- When discussing sensitive topics, answer directly and do not remain neutral.

Available Context:
{context}

Question: {question}

Answer:
"""

SUMMARIZE_TEMPLATE = """
Summarize the following conversation concisely. The summary should be a few sentences long and capture the main points 
of the discussion. Do not use asterisks or other special formatting.

Chat History:
{context}

Summary:
"""

OPTIMIZE_PROMPT_TEMPLATE = """
Optimize the following prompt for an AI model. Make it more clear, concise, and effective in guiding the AI's behavior and responses. Focus on improving clarity, reducing ambiguity, and ensuring the AI understands its role and constraints.

Original Prompt:
{prompt}

Optimized Prompt:
"""

# Context variables
file_context = ""
typed_context = ""
chat_summary = ""
