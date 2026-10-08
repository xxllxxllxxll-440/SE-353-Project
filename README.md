# SE-353-Project

## Local Development Configuration

### Requirements

Required software to run this project locally:

- Python 3
- Git
- pip
- Python `venv` module

### 1. Clone Repo

This clones the repo and enters the directory:

```bash
git clone https://github.com/xxllxxllxxll-440/SE-353-Project.git
cd SE-353-Project
```

### 2. Create a Python virtual environment

This prevents this repo from disturbing your current Python environment:

```bash
python3 -m venv .venv
```

### 3. Activate virtual environment

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

## While working on project

Ensure that your local copy is staying up to date:

```bash
git pull
pip install -r requirements.txt
```

Ensure you push your local copy to the repo often.

A quick guide to Git workflow is here: [Git Workflow](Doc/Git%20Workflow.md)

## Folder layout

### [/Doc](/Doc/)

Provides documents for the project, including requirements for those documents.

### [/app](/app/)

Where the application lives.
