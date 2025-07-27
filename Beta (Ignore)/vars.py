import json
import os
from config import settings


def load_custom_models():
    if os.path.exists(settings.CUSTOM_MODELS_FILE):
        try:
            with open(settings.CUSTOM_MODELS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_custom_models(models):
    with open(settings.CUSTOM_MODELS_FILE, 'w') as f:
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

