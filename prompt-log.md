# Interaction Log

## Interaction 1 - 2026-06-13T05:19:09-06:00
### User Request
please append all interactions to prompt-log.md throughout this session

### Response
I have initialized the interaction logging in [prompt-log.md](file:///Users/goodwin/Matt/SideProjects/titan/prompt-log.md). I will append all subsequent interactions to this file throughout our session.

## Interaction 2 - 2026-06-13T05:19:35-06:00
### User Request
testing

### Response
I have received the test message and appended this interaction to [prompt-log.md](file:///Users/goodwin/Matt/SideProjects/titan/prompt-log.md).

## Interaction 3 - 2026-06-13T05:23:09-06:00
### User Request
dont code - remind me how to create a uv new project and virtual enviornment

### Response
To create a new project and virtual environment using `uv`, you can use the following commands:

1. **Create a new project**:
   ```bash
   uv init my-project
   ```
   This creates a new directory `my-project` with a basic Python project structure (including a `pyproject.toml` file).

2. **Create a virtual environment**:
   ```bash
   uv venv
   ```
   This creates a virtual environment in the `.venv` directory.

3. **Activate the virtual environment**:
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows (Command Prompt):
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - On Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```

4. **Install packages and run**:
   You can add packages using:
   ```bash
   uv add package_name
   ```
   And run your scripts with:
   ```bash
   uv run python script.py
   ```
