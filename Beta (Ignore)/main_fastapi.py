import json
from fastapi import FastAPI, Request, Response, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import JarvisApp, logger
from web_search_tool import google_custom_search

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

jarvis_app = JarvisApp(logger_obj=logger)

@app.on_event("startup")
async def startup_event():
    # This is where you might load models or perform other startup tasks
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # This is where you might clean up resources
    pass

app.mount("/img", StaticFiles(directory="img"), name="img")

@app.get("/")
async def read_root():
    return FileResponse("index.html")

@app.get("/api/current_model")
async def get_current_model():
    content = jarvis_app.get_current_model()
    return JSONResponse(content=content)

@app.get("/api/models")
async def get_models():
    content = jarvis_app.get_models()
    return JSONResponse(content=content)

@app.post("/api/set_model")
async def set_model(request: Request):
    data = await request.json()
    content, status_code = jarvis_app.set_model(data)
    return JSONResponse(content=content, status_code=status_code)

@app.post("/api/save_custom_jarvis")
async def save_custom_jarvis(request: Request):
    data = await request.json()
    content, status_code = jarvis_app.save_custom_jarvis(data)
    return JSONResponse(content=content, status_code=status_code)

@app.post("/api/delete_custom_jarvis")
async def delete_custom_jarvis(request: Request):
    data = await request.json()
    content, status_code = jarvis_app.delete_custom_jarvis(data)
    return JSONResponse(content=content, status_code=status_code)

@app.post("/api/summarize_file")
async def summarize_file(file: UploadFile = File(...)):
    content, status_code = jarvis_app.summarize_file(file)
    return JSONResponse(content=content, status_code=status_code)

@app.post("/api/load_context")
async def load_context(context_file: UploadFile = File(...)):
    content, status_code = jarvis_app.load_context(context_file)
    return JSONResponse(content=content, status_code=status_code)

@app.get("/api/context")
async def get_context():
    content = jarvis_app.get_context()
    return JSONResponse(content=content)

@app.post("/api/clear_file_context")
async def clear_file_context():
    content, status_code = jarvis_app.clear_file_context()
    return JSONResponse(content=content, status_code=status_code)

@app.post("/api/save_typed_context")
async def save_typed_context(request: Request):
    data = await request.json()
    content, status_code = jarvis_app.save_typed_context(data)
    return JSONResponse(content=content, status_code=status_code)

@app.post("/api/clear_typed_context")
async def clear_typed_context():
    content, status_code = jarvis_app.clear_typed_context()
    return JSONResponse(content=content, status_code=status_code)

@app.post("/api/clear_all_context")
async def clear_all_context():
    content, status_code = jarvis_app.clear_all_context()
    return JSONResponse(content=content, status_code=status_code)

@app.get("/api/get_chat_history")
async def get_chat_history():
    content = jarvis_app.get_chat_history()
    return JSONResponse(content=content)

@app.post("/api/summarize_chat")
async def summarize_chat(request: Request):
    data = await request.json()
    content, status_code = jarvis_app.summarize_chat(data)
    return JSONResponse(content=content, status_code=status_code)

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    question = data.get('message')

    # Keyword-based search trigger
    search_keywords = ["weather", "current", "latest", "today", "at the moment", "real-time"]
    force_search = any(keyword in question.lower() for keyword in search_keywords)

    final_ai_response = ""
    status_code = 200

    if force_search:
        jarvis_app.logger.info(f"Keyword-based search triggered for: {question}")
        search_query = question # Use the entire question as the search query
        try:
            search_results = google_custom_search.run(search_query)
            jarvis_app.logger.info(f"Raw search results: {search_results}")
            jarvis_app.logger.info("Web search completed successfully.")

            if "error" in search_results:
                jarvis_app.logger.error(f"Web search failed: {search_results['error']}")
                final_ai_response = f"I tried to search for \"{search_query}\" but encountered an error: {search_results['error']}"
            else:
                # Pass search results back to JarvisApp for re-invocation
                final_ai_response_data, _ = jarvis_app.process_search_results(question, search_results)
                final_ai_response = final_ai_response_data.get('response', '')

        except Exception as e:
            jarvis_app.logger.error(f"Error during web search for query '{search_query}': {e}")
            final_ai_response = f"I tried to search for \"{search_query}\" but encountered an error: {e}"
    else:
        # First, let JarvisApp generate a response (original logic)
        ai_response_data, status_code = jarvis_app.chat(data)
        ai_response_text = ai_response_data.get('response', '')

        # Check if AI wants to perform a web search (original logic)
        if "[SEARCH:" in ai_response_text and ai_response_text.endswith("]"):
            start_index = ai_response_text.find("[SEARCH:") + len("[SEARCH:")
            end_index = ai_response_text.find("]", start_index)
            if start_index != -1 and end_index != -1:
                search_query = ai_response_text[start_index:end_index].strip()
                jarvis_app.logger.info(f"AI requested web search for: {search_query}")
                try:
                    search_results = google_custom_search.run(search_query)
                    jarvis_app.logger.info(f"Raw search results: {search_results}")
                    jarvis_app.logger.info("Web search completed successfully.")

                    if "error" in search_results:
                        jarvis_app.logger.error(f"Web search failed: {search_results['error']}")
                        final_ai_response = f"I tried to search for \"{search_query}\" but encountered an error: {search_results['error']}"
                    else:
                        # Pass search results back to JarvisApp for re-invocation
                        final_ai_response_data, _ = jarvis_app.process_search_results(question, search_results)
                        final_ai_response = final_ai_response_data.get('response', '')

                except Exception as e:
                    jarvis_app.logger.error(f"Error during web search for query '{search_query}': {e}")
                    final_ai_response = f"I tried to search for \"{search_query}\" but encountered an error: {e}"
            else:
                final_ai_response = ai_response_text # If tag is malformed, treat as normal response
        else:
            final_ai_response = ai_response_text

    return JSONResponse(content={'response': final_ai_response}, status_code=status_code)

@app.post("/api/speak")
async def speak_text(request: Request):
    data = await request.json()
    content, status_code = jarvis_app.speak_text(data)
    return Response(content=content.data, media_type=content.mimetype, status_code=status_code)

@app.post("/api/optimize_prompt")
async def optimize_prompt(request: Request):
    data = await request.json()
    content, status_code = jarvis_app.optimize_prompt(data)
    return JSONResponse(content=content, status_code=status_code)

@app.post("/api/feed_info")
async def feed_info(file: UploadFile = File(...)):
    content, status_code = jarvis_app.feed_information(file)
    return JSONResponse(content=content, status_code=status_code)

@app.get("/api/system_stats")
async def system_stats():
    content, status_code = jarvis_app.system_stats()
    return JSONResponse(content=content, status_code=status_code)

@app.post("/api/shutdown")
async def shutdown():
    content, status_code = jarvis_app.shutdown()
    return Response(content=content, status_code=status_code)