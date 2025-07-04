import json
import webbrowser

import GPUtil
import PyPDF2
import psutil
import pytesseract
from PIL import Image
from elevenlabs import ElevenLabs
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

import vars
import vers

# --- Initialization ---
app = Flask(__name__)
CORS(app)

# Global variable to store context
current_context = ""

# Set ElevenLabs API key
elevenlabs_client = None
if hasattr(vars, 'ELEVENLABS_API_KEY') and vars.ELEVENLABS_API_KEY:
    elevenlabs_client = ElevenLabs(api_key=vars.ELEVENLABS_API_KEY)
else:
    print("Warning: ELEVENLABS_API_KEY not found in vars.py. Voice output will not work.")

current_model_name = vars.JARVIS_MODEL
model = OllamaLLM(model=current_model_name)
prompt_template = ChatPromptTemplate.from_template(vars.TEMPLATE)
chain = prompt_template | model


def update_llm_chain(new_model_name):
    global current_model_name, model, chain
    current_model_name = new_model_name
    model = OllamaLLM(model=getattr(vers, new_model_name))
    chain = prompt_template | model


# --- API Endpoints ---
@app.route('/')
def serve_gui():
    return send_from_directory('.', 'index.html')


@app.route('/img/<path:filename>')
def serve_img(filename):
    return send_from_directory('img', filename)


@app.route('/api/models')
def get_models():
    return jsonify(vars.MODELS)


@app.route('/api/set_model', methods=['POST'])
def set_model():
    try:
        data = request.json
        new_model_key = data.get('model_key')
        if new_model_key and new_model_key in vars.MODELS:
            update_llm_chain(vars.MODELS[new_model_key])
            return jsonify({'success': True, 'message': f'Model set to {new_model_key}'})
        else:
            return jsonify({'success': False, 'error': 'Invalid model key'}), 400
    except Exception as e:
        print(f"Error setting model: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/load_context', methods=['POST'])
def load_context():
    global current_context
    if 'context_file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    file = request.files['context_file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    file_extension = file.filename.split('.')[-1].lower()
    extracted_text = ""

    try:
        if file_extension == 'json':
            chat_history_data = json.load(file)
            # We don't set current_context here, instead we return the history
            return jsonify(
                {'success': True, 'history': chat_history_data, 'message': 'Chat history loaded successfully'})
        elif file_extension in ['txt', 'md', 'py', 'js', 'html', 'css']:
            extracted_text = file.read().decode('utf-8')
        elif file_extension == 'pdf':
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                extracted_text += reader.pages[page_num].extract_text() + "\n"
        elif file_extension in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
            img = Image.open(file)
            extracted_text = pytesseract.image_to_string(img)
        else:
            return jsonify({'success': False, 'error': 'Unsupported file type'}), 400

        current_context = extracted_text
        return jsonify({'success': True, 'message': 'Context loaded successfully'})
    except Exception as e:
        print(f"Error loading context: {e}")
        return jsonify({'success': False, 'error': f'Error processing file: {e}'}), 500


@app.route('/api/context', methods=['GET'])
def get_context():
    return jsonify({
        'file_context': current_context,
        'typed_context': vars.typed_context,
        'chat_summary': vars.chat_summary
    })


@app.route('/api/clear_file_context', methods=['POST'])
def clear_file_context():
    global current_context
    current_context = ""
    return jsonify({'success': True, 'message': 'File context cleared.'})


@app.route('/api/save_typed_context', methods=['POST'])
def save_typed_context():
    try:
        data = request.json
        vars.typed_context = data.get('context', '')
        return jsonify({'success': True, 'message': 'Typed context saved.'})
    except Exception as e:
        print(f"Error saving typed context: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/clear_typed_context', methods=['POST'])
def clear_typed_context():
    vars.typed_context = ""
    return jsonify({'success': True, 'message': 'Typed context cleared.'})


@app.route('/api/clear_all_context', methods=['POST'])
def clear_all_context():
    global current_context
    current_context = ""
    vars.typed_context = ""
    vars.chat_summary = ""  # Assuming you might want to clear this too
    return jsonify({'success': True, 'message': 'All context has been cleared.'})


@app.route('/api/summarize_chat', methods=['POST'])
def summarize_chat():
    try:
        data = request.json
        history = data.get('history', [])

        if not history:
            return jsonify({'success': False, 'error': 'No chat history provided.'}), 400

        context_from_history = ""
        for item in history:
            role = "User" if item.get('sender') == 'user' else "J.A.R.V.I.S"
            context_from_history += f"{role}: {item.get('message')}\n"

        summarize_prompt = ChatPromptTemplate.from_template(vars.SUMMARIZE_TEMPLATE)
        summarize_chain = summarize_prompt | model
        summary = summarize_chain.invoke({"context": context_from_history})

        vars.chat_summary = summary
        return jsonify({'success': True, 'summary': summary})

    except Exception as e:
        print(f"Error in /api/summarize_chat: {e}")
        return jsonify({'success': False, 'error': 'An internal server error occurred.'}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        question = data.get('message')
        history = data.get('history', [])

        if not question:
            return jsonify({'error': 'No message provided.'}), 400

        context_from_history = ""
        for item in history:
            role = "User" if item.get('sender') == 'user' else "J.A.R.V.I.S"
            context_from_history += f"{role}: {item.get('message')}\n"

        full_context = ""
        if current_context:
            full_context += f"Context from file: {current_context}\n\n"
        if vars.typed_context:
            full_context += f"Typed Context: {vars.typed_context}\n\n"
        full_context += context_from_history

        result = chain.invoke({"context": full_context, "question": question})
        return jsonify({'response': result})

    except Exception as e:
        print(f"Error in /api/chat: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500


@app.route('/api/speak', methods=['POST'])
def speak_text():
    try:
        text = request.json.get('text')
        if not text:
            return jsonify({'error': 'No text provided for speech synthesis.'}), 400

        if elevenlabs_client:
            audio_stream = elevenlabs_client.text_to_speech.stream(text=text, voice_id="pNInz6obpgDQGXGNn6iq",
                                                                   model_id="eleven_multilingual_v2")
        else:
            return jsonify({'error': 'ElevenLabs client not initialized. API key might be missing.'}), 500

        return Response(audio_stream, mimetype='audio/mpeg')

    except Exception as e:
        print(f"Error in /api/speak: {e}")
        return jsonify({'error': f'ElevenLabs API error: {e}'}), 500


@app.route('/api/system_stats')
def system_stats():
    try:
        cpu_usage = psutil.cpu_percent(interval=None)
        ram_usage = psutil.virtual_memory().percent

        try:
            gpus = GPUtil.getGPUs()
            gpu_usage = gpus[0].load * 100 if gpus else 0
            gpu_error = None
        except Exception as e:
            gpu_usage = 0
            gpu_error = f"Could not retrieve GPU stats: {e}"

        return jsonify({
            'cpu': cpu_usage,
            'ram': ram_usage,
            'gpu': gpu_usage,
            'gpu_error': gpu_error
        })
    except Exception as e:
        print(f"Error in /api/system_stats: {e}")
        return jsonify({
            'cpu': 0,
            'ram': 0,
            'gpu': 0,
            'error': 'Could not retrieve system stats.'
        })


# --- Main Execution ---
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")


if __name__ == '__main__':
    print("Starting J.A.R.V.I.S web server...")
    from threading import Timer

    Timer(1, open_browser).start()
    app.run(port=5000, debug=False)
