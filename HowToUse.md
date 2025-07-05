# How To Use J.A.R.V.I.S

## Installation

1.  **Install Ollama:** Ensure Ollama is installed and running.
2.  **Run J.A.R.V.I.S:** Navigate to the project directory in your terminal and run:
    ```bash
    python main.py
    ```
3.  **Access the Web UI:** Open your web browser and go to `http://127.0.0.1:5000`.

## Customization

You can customize J.A.R.V.I.S through the web interface:

1.  **Theme and LLM Model:**
    *   Click the "CUSTOMIZE" button in the sidebar.
    *   In the "Customization" modal, you can:
        *   Select different themes (Dark, Light, Blue, Green) to change the UI's appearance.
        *   Choose a different LLM model for J.A.R.V.I.S to use.

2.  **Model Naming Convention:**
    Model names in the UI have been updated for clarity (e.g., 'J.A.R.V.I.S - Lite'). The underlying model names in `vars.py` and `vers.py` remain the same.

## Context Management

J.A.R.V.I.S now supports loading external files as context for the AI, and managing typed context and chat summaries.

**How to Manage Context:**
1.  Click the "CONTEXT" button in the sidebar.
2.  In the "Context Management" modal, you can:
    *   **Loaded File Context:** View the content of a previously loaded file.
    *   **Typed Context:** Add or edit custom text context for the AI.
    *   **Chat Summary:** View a summary of the current conversation.

**Actions within Context Management:**
*   **Add Context File:** Click the "+" button next to "CONTEXT" to upload a file.
    *   **Supported File Types:** `.txt`, `.md`, `.py`, `.js`, `.html`, `.css`, `.pdf`, image files (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`).
*   **Clear File Context:** Clears the loaded file context.
*   **Save Typed Context:** Saves the text entered in the "Typed Context" area.
*   **Clear Typed Context:** Clears the typed context.
*   **Summarize Chat:** Generates a summary of the current chat history.
*   **Clear All Context:** Clears all loaded file context, typed context, and chat summary.

**Important: Tesseract OCR for Image Files**
For J.A.R.V.I.S to read text from image files (PNG, JPG, etc.), you **must** have the Tesseract OCR engine installed on your system. This is a separate application and not a Python library.

**Tesseract Installation Guide:**
-   **Windows:**
    1.  Download the installer from the [Tesseract-OCR GitHub page](https://github.com/UB-Mannheim/tesseract/wiki).
    2.  Run the installer. Ensure "Add Tesseract to your system PATH" is selected during installation.
    3.  Restart your computer or command prompt after installation.
-   **macOS:**
    ```bash
    brew install tesseract
    ```
-   **Linux (Debian/Ubuntu):**
    ```bash
    sudo apt update
    sudo apt install tesseract-ocr
    sudo apt install libtesseract-dev
    ```
After installing Tesseract, restart J.A.R.V.I.S for changes to take effect.

## Conversation Features

*   **Persistent Chat History:** J.A.R.V.I.S now remembers your conversations even after you refresh the browser or restart the application. The chat history is automatically saved and loaded.
*   **Time Taken for Responses:** Each AI response will display the time taken to generate the response, providing insight into performance.
*   **Speak/Conversation Mode:**
    *   **SPEAK:** Toggles text-to-speech for AI responses.
    *   **CONVERSATION MODE:** Enables continuous listening for voice input.
*   **Save/Load Chat:**
    *   **Save Chat:** Exports your current chat history as a JSON file.
    *   **Load Chat:** Imports a chat history from a JSON file.
*   **Delete Chat:** Clears the current chat history.

## System Monitoring

The web interface now includes real-time monitoring of your system's resources:
*   **CPU Usage**
*   **RAM Usage**
*   **GPU Usage**
*   **Disk Usage**

These metrics are displayed as live graphs at the top of the conversation area.

## Exiting J.A.R.V.I.S

To exit the J.A.R.V.I.S application, click the "EXIT" button in the sidebar. This will attempt to gracefully shut down the backend server.
