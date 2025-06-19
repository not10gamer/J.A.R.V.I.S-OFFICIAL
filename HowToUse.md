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

You can change the settings 

```bash
info.settings   # This is still heavily under development and will be improved in the future (It is still usable at the current time).
```

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