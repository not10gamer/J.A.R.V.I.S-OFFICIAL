import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

import json
from functools import wraps

import GPUtil
import PyPDF2
import psutil
import pytesseract
from PIL import Image
from elevenlabs.client import ElevenLabs
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from web_search_tool import google_custom_search

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

import vars
from config import settings

Base = declarative_base()

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True)
    sender = Column(String(50))
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "sender": self.sender,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }

class JarvisApp:
    def __init__(self, logger_obj=None):
        self.app = Flask(__name__)
        CORS(self.app)
        self.current_context = ""
        self.typed_context = ""
        self.chat_summary = ""
        self.logger = logger_obj if logger_obj else logging.getLogger(__name__)
        self.elevenlabs_client = None
        if settings.ELEVENLABS_API_KEY:
            self.elevenlabs_client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        else:
            self.logger.warning("ELEVENLABS_API_KEY not found in settings. Voice output will not work.")
        self.current_model_name = "Unknown Model"
        for name, model_info in settings.MODELS.items():
            if isinstance(model_info, str) and model_info == settings.JARVIS_MODEL:
                self.current_model_name = name
                break
        self.model = ChatOllama(model=settings.JARVIS_MODEL).bind_tools([google_custom_search])
        self.prompt_template = ChatPromptTemplate.from_template(settings.TEMPLATE)
        self.chain = self.prompt_template | self.model
        self.FILE_HANDLERS = {
            'txt': self._extract_text_from_text,
            'md': self._extract_text_from_text,
            'py': self._extract_text_from_text,
            'js': self._extract_text_from_text,
            'html': self._extract_text_from_text,
            'css': self._extract_text_from_text,
            'pdf': self._extract_text_from_pdf,
            'png': self._extract_text_from_image,
            'jpg': self._extract_text_from_image,
            'jpeg': self._extract_text_from_image,
            'gif': self._extract_text_from_image,
            'bmp': self._extract_text_from_image,
        }

        # SQLAlchemy setup
        self.engine = create_engine('sqlite:///chat_history.db')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.load_chat_history_from_db()

        self.register_routes()

    def handle_exceptions(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Error in {f.__name__}: {e}")
                return jsonify({'success': False, 'error': 'Internal server error'}), 500
        return decorated_function

    def register_routes(self):
        self.app.route('/')(self.serve_index)
        self.app.route('/img/<path:filename>')(self.serve_img)
        self.app.route('/api/current_model')(self.get_current_model)
        self.app.route('/api/models')(self.get_models)
        self.app.route('/api/set_model', methods=['POST'])(self.handle_exceptions(self.set_model))
        self.app.route('/api/save_custom_jarvis', methods=['POST'])(self.handle_exceptions(self.save_custom_jarvis))
        self.app.route('/api/delete_custom_jarvis', methods=['POST'])(self.handle_exceptions(self.delete_custom_jarvis))
        self.app.route('/api/summarize_file', methods=['POST'])(self.handle_exceptions(self.summarize_file))
        self.app.route('/api/load_context', methods=['POST'])(self.handle_exceptions(self.load_context))
        self.app.route('/api/context', methods=['GET'])(self.get_context)
        self.app.route('/api/clear_file_context', methods=['POST'])(self.clear_file_context)
        self.app.route('/api/save_typed_context', methods=['POST'])(self.handle_exceptions(self.save_typed_context))
        self.app.route('/api/clear_typed_context', methods=['POST'])(self.clear_typed_context)
        self.app.route('/api/clear_all_context', methods=['POST'])(self.clear_all_context)
        self.app.route('/api/get_chat_history')(self.get_chat_history)
        self.app.route('/api/summarize_chat', methods=['POST'])(self.handle_exceptions(self.summarize_chat))
        self.app.route('/api/chat', methods=['POST'])(self.handle_exceptions(self.chat))
        self.app.route('/api/speak', methods=['POST'])(self.handle_exceptions(self.speak_text))
        self.app.route('/api/optimize_prompt', methods=['POST'])(self.handle_exceptions(self.optimize_prompt))
        self.app.route('/api/system_stats')(self.handle_exceptions(self.system_stats))
        self.app.route('/api/shutdown', methods=['POST'])(self.shutdown)

    def run(self):
        self.logger.info("Starting J.A.R.V.I.S web server...")
        self.app.run(port=5000, debug=False)

    def load_chat_history_from_db(self):
        session = self.Session()
        try:
            messages = session.query(ChatMessage).order_by(ChatMessage.timestamp).all()
            self.chat_history_backend = [msg.to_dict() for msg in messages]
            self.logger.info("Chat history loaded from database.")
        except Exception as e:
            self.logger.error(f"Error loading chat history from DB: {e}")
        finally:
            session.close()

    def add_message_to_db(self, sender, message):
        session = self.Session()
        try:
            new_message = ChatMessage(sender=sender, message=message)
            session.add(new_message)
            session.commit()
            self.logger.info(f"Added message to DB: {sender}: {message[:50]}...")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error adding message to DB: {e}")
        finally:
            session.close()

    def update_llm_chain(self, new_model_name):
        self.current_model_name = new_model_name
        self.model = OllamaLLM(model=new_model_name)
        self.chain = ChatPromptTemplate.from_template(settings.TEMPLATE) | self.model
        self.logger.info(f"LLM chain updated to model: {new_model_name}")

    def serve_index(self):
        self.logger.info("Serving index.html")
        return send_from_directory('..', 'index.html')

    def serve_img(self, filename):
        self.logger.info(f"Serving image: {filename}")
        return send_from_directory('img', filename)

    def get_current_model(self):
        self.logger.info("Getting current model name.")
        return {'current_model': self.current_model_name}

    def get_models(self):
        self.logger.info("Getting available models.")
        all_models = {**settings.MODELS, **vars.CUSTOM_MODELS}
        return all_models

    def set_model(self, data):
        new_model_key = data.get('model_key')
        self.logger.info(f"Attempting to set model to: {new_model_key}")
        all_models = {**settings.MODELS, **vars.CUSTOM_MODELS}
        if new_model_key and new_model_key in all_models:
            self.update_llm_chain(
                all_models[new_model_key]["prompt"] if isinstance(all_models[new_model_key], dict) else all_models[
                    new_model_key])
            self.logger.info(f"Model set to {new_model_key}")
            return {'success': True, 'message': f'Model set to {new_model_key}'}, 200
        else:
            self.logger.warning(f"Invalid model key attempted: {new_model_key}")
            return {'success': False, 'error': 'Invalid model key'}, 400

    def save_custom_jarvis(self, data):
        name = data.get('name')
        prompt = data.get('prompt')
        base_model = data.get('base_model')
        self.logger.info(f"Attempting to save custom JARVIS: {name}")
        if not name or not prompt or not base_model:
            self.logger.warning("Missing required fields for saving custom JARVIS.")
            return {'success': False, 'error': 'Name, prompt, and base model are required.'}, 400

        vars.CUSTOM_MODELS[name] = {"prompt": prompt, "base_model": base_model}
        vars.save_custom_models(vars.CUSTOM_MODELS)
        self.logger.info(f"Custom JARVIS \"{name}\" saved successfully.")
        return {'success': True, 'message': f'Custom JARVIS "{name}" saved successfully.'}, 200

    def delete_custom_jarvis(self, data):
        name = data.get('name')
        self.logger.info(f"Attempting to delete custom JARVIS: {name}")
        if not name or name not in vars.CUSTOM_MODELS:
            self.logger.warning(f"Invalid custom model name for deletion: {name}")
            return {'success': False, 'error': 'Invalid custom model name.'}, 400

        del vars.CUSTOM_MODELS[name]
        vars.save_custom_models(vars.CUSTOM_MODELS)
        self.logger.info(f"Custom JARVIS \"{name}\" deleted successfully.")
        return {'success': True, 'message': f'Custom JARVIS "{name}" deleted successfully.'}, 200

    def summarize_file(self, file):
        self.logger.info(f"Attempting to summarize file: {file.filename}")
        if file.filename == '':
            self.logger.warning("No file selected for summarization.")
            return {'success': False, 'error': 'No selected file'}, 400

        file_extension = file.filename.split('.')[-1].lower()
        handler = self.FILE_HANDLERS.get(file_extension)
        if not handler:
            self.logger.warning(f"Unsupported file type for summarization: {file_extension}")
            return {'success': False, 'error': 'Unsupported file type'}, 400

        extracted_text = handler(file.file)
        summarize_prompt = ChatPromptTemplate.from_template(settings.SUMMARIZE_TEMPLATE)
        summarize_chain = summarize_prompt | self.model
        summary = summarize_chain.invoke({"context": extracted_text})
        self.logger.info(f"File {file.filename} summarized successfully.")
        return {'success': True, 'summary': summary}, 200

    def load_context(self, context_file):
        self.logger.info(f"Attempting to load context from file: {context_file.filename}")
        if context_file.filename == '':
            self.logger.warning("No file selected for context loading.")
            return {'success': False, 'error': 'No selected file'}, 400

        file_extension = context_file.filename.split('.')[-1].lower()

        if file_extension == 'json':
            try:
                chat_history_data = json.load(context_file.file)
                session = self.Session()
                try:
                    # Clear existing history
                    session.query(ChatMessage).delete()
                    self.logger.info("Cleared existing chat history from database.")
                    # Add new history
                    for item in chat_history_data:
                        new_message = ChatMessage(sender=item['sender'], message=item['message'])
                        session.add(new_message)
                    session.commit()
                    self.load_chat_history_from_db() # Reload backend list
                    self.logger.info("Chat history loaded from JSON file into database.")
                    return {'success': True, 'history': chat_history_data, 'message': 'Chat history loaded successfully'}, 200
                except Exception as e:
                    session.rollback()
                    self.logger.error(f"Error processing JSON file for context loading: {e}")
                    return {'success': False, 'error': f'Error processing JSON file: {e}'}, 500
                finally:
                    session.close()
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON format for context file: {e}")
                return {'success': False, 'error': 'Invalid JSON format'}, 400

        handler = self.FILE_HANDLERS.get(file_extension)
        if not handler:
            self.logger.warning(f"Unsupported file type for context loading: {file_extension}")
            return {'success': False, 'error': 'Unsupported file type'}, 400

        extracted_text = handler(context_file.file)
        self.current_context = extracted_text
        self.logger.info(f"Context loaded successfully from {context_file.filename}.")
        return {'success': True, 'message': 'Context loaded successfully'}, 200

    def get_context(self):
        self.logger.info("Retrieving current context.")
        return {
            'file_context': str(self.current_context),
            'typed_context': self.typed_context,
            'chat_summary': self.chat_summary
        }

    def clear_file_context(self):
        self.current_context = ""
        self.logger.info("File context cleared.")
        return {'success': True, 'message': 'File context cleared.'}, 200

    def save_typed_context(self, data):
        self.typed_context = data.get('context', '')
        self.logger.info("Typed context saved.")
        return {'success': True, 'message': 'Typed context saved.'}, 200

    def clear_typed_context(self):
        self.typed_context = ""
        self.logger.info("Typed context cleared.")
        return {'success': True, 'message': 'Typed context cleared.'}, 200

    def clear_all_context(self):
        self.current_context = ""
        self.typed_context = ""
        self.chat_summary = ""
        session = self.Session()
        try:
            session.query(ChatMessage).delete()
            session.commit()
            self.chat_history_backend = [] # Clear the in-memory list
            self.logger.info("All context and chat history cleared from database.")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error clearing all context and chat history from DB: {e}")
            return {'success': False, 'error': 'Error clearing chat history.'}, 500
        finally:
            session.close()
        return {'success': True, 'message': 'All context has been cleared.'}, 200

    def get_chat_history(self):
        self.logger.info("Retrieving chat history.")
        self.load_chat_history_from_db() # Ensure the in-memory list is up-to-date
        return self.chat_history_backend

    def summarize_chat(self, data):
        history = data.get('history', [])

        if not history:
            self.logger.warning("No chat history provided for summarization.")
            return {'success': False, 'error': 'No chat history provided.'}, 400

        context_from_history = ""
        for item in history:
            role = "User" if item.get('sender') == 'user' else "J.A.R.V.I.S"
            context_from_history += f"{role}: {item.get('message')}\n"

        summarize_prompt = ChatPromptTemplate.from_template(settings.SUMMARIZE_TEMPLATE)
        summarize_chain = summarize_prompt | self.model
        summary = summarize_chain.invoke({"context": context_from_history})

        self.chat_summary = summary
        self.logger.info("Chat summarized successfully.")
        return {'success': True, 'summary': summary}, 200

    def chat(self, data):
        question = data.get('message')
        self.logger.info(f"Received chat message: {question[:50]}...")

        if not question:
            self.logger.warning("No message provided in chat request.")
            return {'error': 'No message provided.'}, 400

        # Append user message to backend history
        self.add_message_to_db('user', question)
        self.load_chat_history_from_db() # Reload to get the latest history including the new message

        context_from_history = ""
        for item in self.chat_history_backend:
            role = "User" if item.get('sender') == 'user' else "J.A.R.V.I.S"
            context_from_history += f"{role}: {item.get('message')}\n"

        full_context = ""
        if self.current_context:
            full_context += f"Context from file: {self.current_context}\n\n"
        if self.typed_context:
            full_context += f"Typed Context: {self.typed_context}\n\n"
        full_context += context_from_history

        result = self.chain.invoke({"context": full_context, "question": question})

        # Check if the result is a tool invocation
        if isinstance(result, dict) and "tool_calls" in result:
            tool_calls = result["tool_calls"]
            tool_outputs = []
            for tool_call in tool_calls:
                if tool_call["name"] == "google_custom_search":
                    search_query = tool_call["args"].get("query")
                    if search_query:
                        search_result = google_custom_search.run(search_query)
                        tool_outputs.append(search_result)
                    else:
                        tool_outputs.append("Error: 'query' argument missing for google_custom_search tool.")
                else:
                    tool_outputs.append(f"Unknown tool: {tool_call['name']}")
            
            # Pass tool outputs back to the model
            tool_response = self.chain.invoke({"context": full_context, "question": question, "tool_outputs": tool_outputs}, tools=[google_custom_search])
            final_response = tool_response
        else:
            final_response = result

        # Append AI response to backend history
        self.add_message_to_db('ai', final_response.content)
        self.load_chat_history_from_db() # Reload to get the latest history including the new AI message
        self.logger.info(f"Generated AI response: {final_response.content[:50]}...")

        return {'response': final_response.content}, 200

    def process_search_results(self, question, search_results):
        self.logger.info("Processing search results and re-invoking AI.")
        search_context = "\n\nWeb Search Results:\n" + json.dumps(search_results, indent=2)

        full_context = ""
        if self.current_context:
            full_context += f"Context from file: {self.current_context}\n\n"
        if self.typed_context:
            full_context += f"Typed Context: {self.typed_context}\n\n"

        # Add chat history to context
        context_from_history = ""
        for item in self.chat_history_backend:
            role = "User" if item.get('sender') == 'user' else "J.A.R.V.I.S"
            context_from_history += f"{role}: {item.get('message')}\n"
        full_context += context_from_history

        full_context += search_context # Add search results to the end of the context

        ai_response = self.chain.invoke({"context": full_context, "question": question})
        self.logger.info(f"AI re-invoked with search results. Response: {ai_response.content[:50]}...")
        return {'response': ai_response.content}, 200

    def speak_text(self, data):
        text = data.get('text')
        self.logger.info(f"Attempting to synthesize speech for text: {text[:50]}...")
        if not text:
            self.logger.warning("No text provided for speech synthesis.")
            return {'error': 'No text provided for speech synthesis.'}, 400

        if self.elevenlabs_client:
            try:
                audio_stream = self.elevenlabs_client.text_to_speech.stream(text=text,
                                                                           voice_id=settings.ELEVENLABS_VOICE_ID,
                                                                           model_id="eleven_multilingual_v2")
                self.logger.info("Speech synthesis successful.")
                return Response(audio_stream, mimetype='audio/mpeg'), 200
            except Exception as e:
                self.logger.error(f"ElevenLabs API error during speech synthesis: {e}")
                return {'error': f'ElevenLabs API error: {e}'}, 500
        else:
            self.logger.error("ElevenLabs client not initialized. API key might be missing.")
            return {'error': 'ElevenLabs client not initialized. API key might be missing.'}, 500

    def optimize_prompt(self, data):
        prompt_to_optimize = data.get('prompt')
        self.logger.info(f"Attempting to optimize prompt: {prompt_to_optimize[:50]}...")

        if not prompt_to_optimize:
            self.logger.warning("No prompt provided for optimization.")
            return {'success': False, 'error': 'No prompt provided for optimization.'}, 400

        optimize_template = ChatPromptTemplate.from_template(settings.OPTIMIZE_PROMPT_TEMPLATE)
        optimize_chain = optimize_template | self.model
        optimized_prompt = optimize_chain.invoke({"prompt": prompt_to_optimize})

        self.logger.info("Prompt optimized successfully.")
        return {'success': True, 'optimized_prompt': optimized_prompt}, 200

    def system_stats(self):
        self.logger.info("Retrieving system statistics.")
        cpu_usage = psutil.cpu_percent(interval=0.1)
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        try:
            gpus = GPUtil.getGPUs()
            gpu_usage = gpus[0].load * 100 if gpus else 0
            gpu_error = None
        except Exception as e:
            gpu_usage = 0
            gpu_error = f"Could not retrieve GPU stats: {e}"
            self.logger.warning(f"GPU stats retrieval failed: {e}")

        self.logger.info("System statistics retrieved successfully.")
        return {
            'cpu': cpu_usage,
            'ram': ram_usage,
            'gpu': gpu_usage,
            'disk': disk_usage,
            'gpu_error': gpu_error
        }, 200

    def shutdown(self):
        self.logger.info("Server shutdown requested.")
        # This is a development server only feature, it will not work in production
        shutdown_server = request.environ.get('werkzeug.server.shutdown')
        if shutdown_server:
            shutdown_server()
            self.logger.info("Server shutting down.")
        return 'Server shutting down...', 200

    def feed_information(self, file):
        self.logger.info(f"Attempting to feed information from file: {file.filename}")
        if file.filename == '':
            self.logger.warning("No file selected for feeding information.")
            return {'success': False, 'error': 'No selected file'}, 400

        file_extension = file.filename.split('.')[-1].lower()
        handler = self.FILE_HANDLERS.get(file_extension)
        if not handler:
            self.logger.warning(f"Unsupported file type for feeding information: {file_extension}")
            return {'success': False, 'error': 'Unsupported file type'}, 400

        try:
            extracted_text = handler(file.file)
            # For now, append to current_context. In a real-world scenario, this might involve more sophisticated knowledge base management.
            self.current_context += "\n\n" + extracted_text
            self.logger.info(f"Information from {file.filename} fed successfully.")
            return {'success': True, 'message': f'Information from {file.filename} fed successfully.'}, 200
        except Exception as e:
            self.logger.error(f"Error feeding information from file {file.filename}: {e}")
            return {'success': False, 'error': f'Error processing file: {e}'}, 500

    def _extract_text_from_text(self, file):
        self.logger.debug("Extracting text from plain text file.")
        return file.read().decode('utf-8')

    def _extract_text_from_pdf(self, file):
        self.logger.debug("Extracting text from PDF file.")
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    def _extract_text_from_image(self, file):
        self.logger.debug("Extracting text from image file using Tesseract.")
        img = Image.open(file)
        return pytesseract.image_to_string(img)
