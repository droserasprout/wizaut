# Wizaut

Lightweight Web UI to manage WiZ lights

## Usage

```bash
## --reload: make the server restart after code changes. Only do this for development.
uvicorn src.wizaut.api:app --reload

## Run with your host and port.
uvicorn src.wizaut.api:app --host localhost --port 8000
```