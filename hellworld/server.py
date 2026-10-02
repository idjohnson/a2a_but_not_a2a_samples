from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Echo Bot API")

class EchoRequest(BaseModel):
    user_request: Optional[str] = ""

def process_request(user_request: Optional[str]) -> dict:
    if not user_request or not user_request.strip():
        return {"response": "No text input is provided!"}
    
    # Returning the exact string format requested
    return {"response": f"Hello, World! I have received your request ({user_request})"}

@app.post("/echo_bot")
async def echo_bot_post(request: EchoRequest):
    return process_request(request.user_request)

@app.get("/echo_bot")
async def echo_bot_get(user_request: Optional[str] = Query("")):
    return process_request(user_request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
