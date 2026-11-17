# mindspeak-foxy

A small child-safe AI toy demo project. This folder currently contains only the Phase 1 setup.

## Windows setup (beginner steps)

Open PowerShell in this folder, then run these commands one at a time:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

When activation works, PowerShell usually shows `(.venv)` at the start of the prompt. If PowerShell says script execution is disabled, open Command Prompt instead and use:

```bat
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

To leave the virtual environment, run:

```powershell
deactivate
```

Keep any real API key in a local `.env` file. Do not put a real key in `.env.example` or commit `.env` to Git.
