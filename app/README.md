# Python Website Server

## Running the Server

### 1. Create a Python virtual environment

This prevents this repo from disturbing your current Python environment:

```bash
python3 -m venv .venv
```

### 2. Activate virtual environment

On Windows PowerShell:

```PowerShell
.venv\Scripts\Activate.ps1
```

On Windows Command Prompt:

```Command Prompt
.venv\Scripts\activate
```

On Linux or MacOS:

```bash
source .venv/bin/activate
```

You can verify if you are in the virtual environment if `(.venv)` is shown before the prompt.

### Disable the virtual environment

Run:

```bash
deactivate
```

### 4. Install project Python dependencies

Installs the required Python packages:

```bash
pip install -r requirements.txt
```

**NOTE**: if you need to install other dependencies when working on this project, add them to `requirements.txt`

## Starting the development server

Done by running:

```bash
python run.py
```

The terminal should output the link to the server start-page.

## Stopping the server

Press `Ctrl+C` in the terminal running the server.
