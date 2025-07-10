import json
import os

import GPUtil
import PyPDF2
import psutil
import pytesseract
from PIL import Image
from elevenlabs.client import ElevenLabs
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

import vars

# import decoder # Removed as web UI handles settings

# --- Initialization ---
app = Flask(__name__)
CORS(app)

# Global variable to store context
current_context = ""

# Global variable to store chat history
CHAT_HISTORY_FILE = 'chat_history.json'
chat_history_backend = []


def load_chat_history_from_file():
    global chat_history_backend
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, 'r') as f:
                chat_history_backend = json.load(f)
        except json.JSONDecodeError:
            chat_history_backend = []
    else:
        chat_history_backend = []


def save_chat_history_to_file():
    with open(CHAT_HISTORY_FILE, 'w') as f:
        json.dump(chat_history_backend, f, indent=2)


# Load history on startup
load_chat_history_from_file()

# Set ElevenLabs API key
elevenlabs_client = None
if hasattr(vars, 'ELEVENLABS_API_KEY') and vars.ELEVENLABS_API_KEY:
    elevenlabs_client = ElevenLabs(api_key=vars.ELEVENLABS_API_KEY)
else:
    print("Warning: ELEVENLABS_API_KEY not found in vars.py. Voice output will not work.")

current_model_name = "Unknown Model"
for name, model_info in vars.MODELS.items():
    if isinstance(model_info, str) and model_info == vars.JARVIS_MODEL:
        current_model_name = name
        break

model = OllamaLLM(model=vars.JARVIS_MODEL)
prompt_template = ChatPromptTemplate.from_template(vars.TEMPLATE)
chain = prompt_template | model


def update_llm_chain(new_model_name):
    global current_model_name, model, chain
    current_model_name = new_model_name
    model = OllamaLLM(model=new_model_name)
    chain = prompt_template | model


# --- API Endpoints ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')


@app.route('/img/<path:filename>')
def serve_img(filename):
    return send_from_directory('img', filename)


@app.route('/api/current_model')
def get_current_model():
    return jsonify({'current_model': current_model_name})


@app.route('/api/models')
def get_models():
    all_models = {**vars.MODELS, **vars.CUSTOM_MODELS}
    return jsonify(all_models)


@app.route('/api/set_model', methods=['POST'])
def set_model():
    try:
        data = request.json
        new_model_key = data.get('model_key')
        all_models = {**vars.MODELS, **vars.CUSTOM_MODELS}
        if new_model_key and new_model_key in all_models:
            update_llm_chain(
                all_models[new_model_key]["prompt"] if isinstance(all_models[new_model_key], dict) else all_models[
                    new_model_key])
            return jsonify({'success': True, 'message': f'Model set to {new_model_key}'})
        else:
            return jsonify({'success': False, 'error': 'Invalid model key'}), 400
    except Exception as e:
        print(f"Error setting model: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/save_custom_jarvis', methods=['POST'])
def save_custom_jarvis():
    try:
        data = request.json
        name = data.get('name')
        prompt = data.get('prompt')
        base_model = data.get('base_model')
        if not name or not prompt or not base_model:
            return jsonify({'success': False, 'error': 'Name, prompt, and base model are required.'}), 400

        vars.CUSTOM_MODELS[name] = {"prompt": prompt, "base_model": base_model}
        vars.save_custom_models(vars.CUSTOM_MODELS)
        return jsonify({'success': True, 'message': f'Custom JARVIS "{name}" saved successfully.'})
    except Exception as e:
        print(f"Error saving custom JARVIS: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/delete_custom_jarvis', methods=['POST'])
def delete_custom_jarvis():
    try:
        data = request.json
        name = data.get('name')
        if not name or name not in vars.CUSTOM_MODELS:
            return jsonify({'success': False, 'error': 'Invalid custom model name.'}), 400

        del vars.CUSTOM_MODELS[name]
        vars.save_custom_models(vars.CUSTOM_MODELS)
        return jsonify({'success': True, 'message': f'Custom JARVIS "{name}" deleted successfully.'})
    except Exception as e:
        print(f"Error deleting custom JARVIS: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/summarize_file', methods=['POST'])
def summarize_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    file_extension = file.filename.split('.')[-1].lower()
    handler = FILE_HANDLERS.get(file_extension)
    if not handler:
        return jsonify({'success': False, 'error': 'Unsupported file type'}), 400

    try:
        extracted_text = handler(file)
        summarize_prompt = ChatPromptTemplate.from_template(vars.SUMMARIZE_TEMPLATE)
        summarize_chain = summarize_prompt | model
        summary = summarize_chain.invoke({"context": extracted_text})
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        print(f"Error summarizing file: {e}")
        return jsonify({'success': False, 'error': f'Error processing file: {e}'}), 500


def _extract_text_from_text(file):
    return file.read().decode('utf-8')


def _extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def _extract_text_from_image(file):
    img = Image.open(file)
    return pytesseract.image_to_string(img)


FILE_HANDLERS = {
    'txt': _extract_text_from_text,
    'md': _extract_text_from_text,
    'py': _extract_text_from_text,
    'js': _extract_text_from_text,
    'html': _extract_text_from_text,
    'css': _extract_text_from_text,
    'pdf': _extract_text_from_pdf,
    'png': _extract_text_from_image,
    'jpg': _extract_text_from_image,
    'jpeg': _extract_text_from_image,
    'gif': _extract_text_from_image,
    'bmp': _extract_text_from_image,
}


@app.route('/api/load_context', methods=['POST'])
def load_context():
    global current_context
    if 'context_file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    file = request.files['context_file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    file_extension = file.filename.split('.')[-1].lower()

    if file_extension == 'json':
        try:
            chat_history_data = json.load(file)
            chat_history_backend.clear()
            chat_history_backend.extend(chat_history_data)
            save_chat_history_to_file()
            return jsonify(
                {'success': True, 'history': chat_history_data, 'message': 'Chat history loaded successfully'})
        except Exception as e:
            print(f"Error loading chat history: {e}")
            return jsonify({'success': False, 'error': f'Error processing JSON file: {e}'}), 500

    handler = FILE_HANDLERS.get(file_extension)
    if not handler:
        return jsonify({'success': False, 'error': 'Unsupported file type'}), 400

    try:
        extracted_text = handler(file)
        current_context = extracted_text
        return jsonify({'success': True, 'message': 'Context loaded successfully'})
    except Exception as e:
        print(f"Error loading context: {e}")
        return jsonify({'success': False, 'error': f'Error processing file: {e}'}), 500


@app.route('/api/context', methods=['GET'])
def get_context():
    return jsonify({
        'file_context': str(current_context),
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
    vars.chat_summary = ""
    chat_history_backend.clear()
    if os.path.exists(CHAT_HISTORY_FILE):
        os.remove(CHAT_HISTORY_FILE)
    return jsonify({'success': True, 'message': 'All context has been cleared.'})


@app.route('/api/get_chat_history')
def get_chat_history():
    return jsonify(chat_history_backend)


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

        # Append user message to backend history
        chat_history_backend.append({'sender': 'user', 'message': question})
        save_chat_history_to_file()

        context_from_history = ""
        for item in chat_history_backend:
            role = "User" if item.get('sender') == 'user' else "J.A.R.V.I.S"
            context_from_history += f"{role}: {item.get('message')}\n"

        full_context = ""
        if current_context:
            full_context += f"Context from file: {current_context}\n\n"
        if vars.typed_context:
            full_context += f"Typed Context: {vars.typed_context}\n\n"
        full_context += context_from_history

        result = chain.invoke({"context": full_context, "question": question})

        # Append AI response to backend history
        chat_history_backend.append({'sender': 'ai', 'message': result})
        save_chat_history_to_file()

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
            audio_stream = elevenlabs_client.text_to_speech.stream(text=text,
                                                                   voice_id="6xPz2opT0y5qtoRh1U1Y",
                                                                   model_id="eleven_multilingual_v2")
        else:
            return jsonify({'error': 'ElevenLabs client not initialized. API key might be missing.'}), 500

        return Response(audio_stream, mimetype='audio/mpeg')

    except Exception as e:
        print(f"Error in /api/speak: {e}")
        return jsonify({'error': f'ElevenLabs API error: {e}'}), 500


@app.route('/api/optimize_prompt', methods=['POST'])
def optimize_prompt():
    try:
        data = request.json
        prompt_to_optimize = data.get('prompt')

        if not prompt_to_optimize:
            return jsonify({'success': False, 'error': 'No prompt provided for optimization.'}), 400

        optimize_template = ChatPromptTemplate.from_template(vars.OPTIMIZE_PROMPT_TEMPLATE)
        optimize_chain = optimize_template | model
        optimized_prompt = optimize_chain.invoke({"prompt": prompt_to_optimize})

        return jsonify({'success': True, 'optimized_prompt': optimized_prompt})

    except Exception as e:
        print(f"Error optimizing prompt: {e}")
        return jsonify({'success': False, 'error': 'Internal server error during prompt optimization.'}), 500


@app.route('/api/system_stats')
def system_stats():
    try:
        cpu_usage = psutil.cpu_percent(interval=None)
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('C:\\').percent

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
            'disk': disk_usage,
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


@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    shutdown_server = request.environ.get('werkzeug.server.shutdown')
    if shutdown_server:
        shutdown_server()
    return 'Server shutting down...'


# --- Main Execution ---
if __name__ == '__main__':
    print("Starting J.A.R.V.I.S web server...")
    app.run(port=5000, debug=False)
