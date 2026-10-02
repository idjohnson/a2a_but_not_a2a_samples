import uuid
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent import ReimbursementAgent

app = FastAPI(title="Expense Reimbursement API")
agent = ReimbursementAgent()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, Any]:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty")
    session_id = request.session_id or str(uuid.uuid4())
    try:
        result = agent.chat(session_id, request.message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Model call failed: {e}")
    return {"session_id": session_id, **result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
