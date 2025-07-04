
# J.A.R.V.I.S

A customizable AI with a user-friendly GUI, powered by Ollama models.

Sign up for the next big update https://tally.so/r/mBYkjY

For an in-depth guide on how to use J.A.R.V.I.S, please check out the 

####  [How To Use J.A.R.V.I.S](https://github.com/not10gamer/J.A.R.V.I.S-OFFICIAL/blob/main/HowToUse.md)

## Features

- Customizable AI models (now with user-friendly names like "J.A.R.V.I.S - Lite")
- Load various file types (text, PDF, images) as context for the AI
- Open Source
- Cross-platform
- Intuitive Graphical User Interface (GUI)

## Installation

1.  **Install Ollama:** Download and install Ollama from [ollama.com/download](https://ollama.com/download).

2.  **Pull Models:** After installing Ollama, pull the desired models. For example, to get the default model:
    ```bash
    ollama run llama2
    ```
    You can find more models on the official Ollama GitHub [page](https://github.com/ollama/ollama).

3.  **Install Python Dependencies:** Navigate to the project directory and install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Tesseract OCR (Optional, for Image Context):** If you plan to use image files (PNG, JPG, etc.) as context, you must install the Tesseract OCR engine separately. Refer to the [How To Use J.A.R.V.I.S](https://github.com/not10gamer/J.A.R.V.I.S-OFFICIAL/blob/main/HowToUse.md) guide for detailed installation instructions for your operating system.

## Usage

1.  **Configure Models (Optional):** You can customize the AI's behavior and model mappings by editing `vars.py` and `vers.py`.

2.  **Run J.A.R.V.I.S:** Start the application by running `main.py`:
    ```bash
    python main.py
    ```
    This will open the J.A.R.V.I.S GUI in your web browser.

3.  **Load Context (Optional):** In the GUI, click the "CUSTOMIZE" button, then use the "Context File" section to load text, PDF, or image files as context for the AI.

## Deployment

Once you have installed the required models and dependencies, you can run `main.py` to start the J.A.R.V.I.S web server.

```bash
  python main.py
```

## Run Locally

Clone the project

```bash
  git clone https://github.com/not10gamer/J.A.R.V.I.S-OFFICIAL.git
```

Go to the project directory

```bash
  cd J.A.R.V.I.S-OFFICIAL
```

Install dependencies (as described in the Installation section above).

Start the AI

```bash
  python main.py
```


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

