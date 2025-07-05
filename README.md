# J.A.R.V.I.S

A customizable AI with a modern, user-friendly web interface, powered by Ollama models.

Sign up for the next big update https://tally.so/r/mBYkjY

For an in-depth guide on how to use J.A.R.V.I.S, please check out the 

####  [How To Use J.A.R.V.I.S](https://github.com/not10gamer/J.A.R.V.I.S-OFFICIAL/blob/main/HowToUse.md)

## Features

- **Modern Web Interface:** A sleek, responsive UI with a dark theme for an enhanced user experience.
- **Customizable AI Models:** Easily switch between different Ollama models directly from the UI.
- **Persistent Chat History:** J.A.R.V.I.S remembers your conversations across sessions.
- **Context Management:** Load various file types (text, PDF, images) as context, and manage typed context and chat summaries.
- **Real-time System Monitoring:** Monitor CPU, RAM, GPU, and Disk usage directly within the application.
- **Voice Interaction:** Toggle text-to-speech and continuous listening for hands-free operation.
- **Chat Export/Import:** Save and load your chat history.
- Open Source
- Cross-platform

## Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/not10gamer/J.A.R.V.I.S-OFFICIAL.git
    cd J.A.R.V.I.S-OFFICIAL
    ```

2.  **Install Ollama:** Download and install Ollama from [ollama.com/download](https://ollama.com/download).

3.  **Pull Models:** After installing Ollama, pull the desired models. For example, to get the default model:
    ```bash
    ollama run llama2
    ```
    You can find more models on the official Ollama GitHub [page](https://github.com/ollama/ollama).

4.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Install Tesseract OCR (Optional, for Image Context):** If you plan to use image files (PNG, JPG, etc.) as context, you must install the Tesseract OCR engine separately. Refer to the [How To Use J.A.R.V.I.S](https://github.com/not10gamer/J.A.R.V.I.S-OFFICIAL/blob/main/HowToUse.md) guide for detailed installation instructions for your operating system.

6.  **Run J.A.R.V.I.S:** Start the application:
    ```bash
    python main.py
    ```
    This will start the J.A.R.V.I.S web server. Open your web browser and go to `http://127.0.0.1:5000` to access the UI.

## Badges

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)
![Static Badge](https://img.shields.io/badge/Certification--B)
![Static Badge](https://img.shields.io/badge/Grade-A-green)


## Authors

- [@not10gamer](https://github.com/not10gamer)


## License

[MIT](https://choosealicense.com/licenses/mit/)