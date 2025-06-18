import vars
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import pyttsx3
import speech_recognition
import winsound
import time
from decoder import return_info

o, i, ui = str(return_info())
model = OllamaLLM(model=vars.JARVIS_MODEL)
prompt = ChatPromptTemplate.from_template(vars.TEMPLATE)
chain = prompt | model
speak = pyttsx3.init()

recognizer = speech_recognition.Recognizer()


def record_speech():
    while 1:
        try:
            with speech_recognition.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("listening...", end=" ")
                winsound.Beep(frequency=2000, duration=250)
                audio = recognizer.listen(source, )
                print("Understanding...")
                winsound.Beep(frequency=1500, duration=250)
                return recognizer.recognize_google(audio)

        except speech_recognition.UnknownValueError as e:
            print("Could not understand audio: {0}".format(e))
            winsound.Beep(frequency=1000, duration=250)
        except speech_recognition.RequestError:
            print("Request Error Occurred")
            winsound.Beep(frequency=1000, duration=250)


context = ""
start_up = "JARVIS: Hello"

try:
    file = open("history.txt", "r")
    context = file.read()
    file.close()
except FileNotFoundError:
    print("No previous history found.")

context = context + start_up
print(start_up)
speak.say(start_up[8:])
speak.runAndWait()

while True:
    if i == "audio":
        user_in = record_speech()
    else:
        user_in = input("You: ")

    print(f"You: {user_in}")
    print("Thinking...")
    if str(user_in).lower() == "bye":
        result = chain.invoke({"context": context, "question": "bye"})
        print("JARVIS: " + result, end="")
        speak.say(result)
        speak.runAndWait()
        context += f"\nUser: {user_in}\nJarvis: {result}\n"

        file = open("history.txt", "a")
        file.write(context)
        file.close()
        print("Chat history saved.")
        break

    start = time.time()
    result = chain.invoke({"context": context, "question": user_in})
    end = time.time()
    print(f"Time taken: {end - start}")

    print("JARVIS: " + result)

    if o == "audio":
        if result.startswith("<think>"):
            speak.say(result.split("</think>")[1])
        else:
            speak.say(result)
        speak.runAndWait()

    context += f"\nUser: {user_in}\nJarvis: {result}\n"
