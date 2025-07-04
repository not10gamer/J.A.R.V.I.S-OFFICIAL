# How To Use J.A.R.V.I.S

## Installation

Once Ollama is installed run the following command

```bash
    ollama run <Your Model>
```

## Customization

Once that's done, you can set up the way the AI works by editing the following files.

```bash
vars.py
vers.py
```

**Model Naming Convention:**
Model names in the UI have been updated for clarity. For example, 'Speed' is now displayed as 'J.A.R.V.I.S - Lite'. The underlying model names in `vars.py` and `vers.py` remain the same.

You can also change other settings in:

```bash
# This is still heavily under development and will be improved in the future (It is still usable at the current time (audio and text)).
info.settings
```

## Context Loading

J.A.R.V.I.S now supports loading external files as context for the AI. This allows the AI to answer questions based on the content of your documents.

**Supported File Types:**
- **Text-based:** `.txt`, `.md`, `.py`, `.js`, `.html`, `.css`
- **Documents:** `.pdf`
- **Images (OCR):** `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`

**How to Load Context:**
1.  Open the J.A.R.V.I.S web interface.
2.  Click the "CUSTOMIZE" button in the sidebar.
3.  In the "Customization" modal, navigate to the "Context File" section.
4.  Click "Select Context File" and choose your desired file.
5.  Click "Load Context" to send the file content to the AI.

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

## Usage

To use the AI you can run the following command

```bash
python main.py
```

```
The AI will say "Hello" and after a 250 ms beep at 1500 Hz you will be able to start a conversation.

Each frequency will last 250 ms and each frequency has a corresponding meaning that can be self-evaluated in main.py.
```

The above only applies in Audio IN and OUT. (Can be changed in info.settings)