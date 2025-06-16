"""
The different AI models categorized based of their speciality

Speed_acc  (4.7 GB) --- Done
consistent (2.0 GB) --- Done
based      (2.5 GB) --- Not Done
open_based (4.1 GB) --- Not in the WORKS
speed      (839 MB) --- In the WORKS
unhinged   (3.8 GB) --- In the WORKS
* These are the estimated sizes of the models
* These are estimated sizes the true sizes can be found in the official ollama github plus the
                                                                                        manifest files (2 MB to 1.6 GB).

Pick the model that you prefer and replace the JARVIS_MODEL variable with your preferred model
"""
import vers

JARVIS_MODEL = vers.consistent
TEMPLATE = """
Your name is Jarvis.
Your creator is Ethan (Don't Mention unless asked).
Only give the answer.
The Person that talks to you can be anyone.
At first speak formally and then match the tone of the person speaking with you.
You should be informative and useful while being fun to talk to.
Everything you say will be spoken through the use of text-to-speech, therefore keep it concise and short.
Do not use "*" in your responses.

Chat History: {context}

Question: {question}

Answer:
"""