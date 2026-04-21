# api/main.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent.graph import run_agent
import json

app = FastAPI(
    title="AutoCoder Agent API",
    description="An autonomous coding assistant powered by LLaMA 3.3 + LangGraph",
    version="1.0.0"
)


# Request/Response Models

class TaskRequest(BaseModel):
    task: str

class AgentResponse(BaseModel):
    task: str
    code: str
    explanation: str
    success: bool
    attempts: int


# Routes 

@app.get("/")
def root():
    return {"message": "AutoCoder Agent is running 🚀"}


@app.post("/run", response_model=AgentResponse)
def run_task(request: TaskRequest):
    """
    Run the agent on a coding task.
    Returns final code + explanation.
    """
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")

    try:
        result = run_agent(request.task)
        return AgentResponse(
            task=result["task"],
            code=result["code"],
            explanation=result["explanation"],
            success=result["result"].get("success", False),
            attempts=result["attempts"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stream")
def stream_task(request: TaskRequest):
    """
    Run the agent and stream status updates as Server-Sent Events.
    """
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")

    def event_generator():
        try:
            # Send start event
            yield f"data: {json.dumps({'status': 'starting', 'message': 'Agent starting...'})}\n\n"

            result = run_agent(request.task)

            # Send code event
            yield f"data: {json.dumps({'status': 'code', 'message': result['code']})}\n\n"

            # Send explanation event
            yield f"data: {json.dumps({'status': 'explanation', 'message': result['explanation']})}\n\n"

            # Send done event
            yield f"data: {json.dumps({'status': 'done', 'message': 'Agent finished!'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/health")
def health():
    return {"status": "ok"}