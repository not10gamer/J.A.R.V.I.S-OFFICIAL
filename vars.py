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
import vers

ELEVENLABS_API_KEY = "sk_a09566db66a2799bc772e1c52a0fc025bd25525d3a230b7f"
JARVIS_MODEL = vers.consistent

MODELS = {
    "Consistent": "consistent",
    "Speed Accurate": "speed_acc",
    "Based": "based",
    "Open Based": "open_based",
    "Speed": "speed",
    "Unhinged": "unhinged"
}
TEMPLATE = """
Your name is Jarvis.
Your creator is Ethan (Don't Mention unless asked).
Only give the answer.
The Person that talks to you can be anyone.
At first speak formally and then match the tone of the person speaking with you.
You should be informative and useful while being fun to talk to.
Everything you say will be spoken through the use of text-to-speech, therefore keep it concise and short.
Always answer the question directly do not stay neutral in sensitive topics.
Do not use "*" in your responses.

Chat History: {context}

Question: {question}

Answer:
"""