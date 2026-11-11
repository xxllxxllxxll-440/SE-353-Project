# Python Website Server

## Note

Using <https://flask.palletsprojects.com/en/stable/tutorial/> as a reference for Flask

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

Done by running the following in the root of the project:

```bash
flask --app flaskr run --debug
```

The terminal should output the link to the server' address.

Use [the Site Directory](/Doc/Site%20Directory.md) to navigate the server.

## Testing Database Connection

Running this command within the root of the project verifies if Flask can communicate to the MYSQL server.
You will need to configure your `.env` file within `database/app` first.

```bash
python -c "from database.app import database; print(database.connection_check())"
```

## Testing

This website is designed for both a mobile interface as well as a desktop interface.

### Using Responsive Design Testing

Most browsers have support for testing websites with adaptive design. Here is some details on how to do that for the popular browsers:

- [Firefox](https://firefox-source-docs.mozilla.org/devtools-user/responsive_design_mode/)
- [Chrome, Edge, Opera (most Chromium-based browsers)](https://developer.chrome.com/docs/devtools/device-mode)

### Using External Device

You can also open the site on a different device. Both devices **must** be connected to the same network.

You will need to change the arguments for the command you use to start the server. Use:

```bash
flask --app flaskr run --debug --host=0.0.0.0
```

Flask will output two addresses. You will need to use the address that is not the loopback address `127.0.0.1`

## Stopping the server

Press `Ctrl+C` in the terminal running the server.
