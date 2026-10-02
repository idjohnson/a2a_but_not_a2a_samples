# Expense Reimbursement (FastAPI + LiteLLM)

Non-A2A version of `adk_expense_reimbursement`. A FastAPI server runs a LiteLLM tool-calling loop (`create_request_form`, `return_form`, `reimburse`) and keeps per-session history in memory.

## Setup

```bash
pip install -r requirements.txt
```

Configuration (environment variables):

- `LITELLM_MODEL` – any LiteLLM model string (default `vertex_ai/gemini-2.5-flash`).
- For Vertex AI: `VERTEXAI_PROJECT`, `VERTEXAI_LOCATION`, and credentials via `gcloud auth application-default login` or `GOOGLE_APPLICATION_CREDENTIALS`.
- `REIMBURSE_URL` – CLI target (default `http://127.0.0.1:8000/chat`).

## Run

```bash
python server.py     # terminal 1
python cli.py        # terminal 2
```

## API

`POST /chat` with `{"message": "...", "session_id": "optional"}`.

Response always includes `session_id`, plus either:

- `{"type": "text", "response": "..."}` – final answer.
- `{"type": "form", "form": {...}, "form_data": {...}, "instructions": "..."}` – send the completed form back as the next `message` (JSON string) with the same `session_id`.

```bash
curl -X POST localhost:8000/chat -H 'Content-Type: application/json' \
  -d '{"message": "Reimburse $20 for lunch on 2026-01-02 with a client"}'
```
