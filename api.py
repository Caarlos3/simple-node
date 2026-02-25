import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine import WorkflowEngine
from dotenv import load_dotenv
from session_manager import SessionManager


load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Simple-Node API",
    description="Api for executing workflows nodes",
    version="0.1.0",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_manager = SessionManager()

class WorkflowRequest(BaseModel):
    input_data: str
    workflow_config: str = "workflow_example.json"
    session_id: str | None = None


@app.get("/")
def read_root():
    return {"message": "Welcome to the Simple-Node API. Use the /execute endpoint to run your workflows."}


@app.post("/run")
def run_workflow(request: WorkflowRequest):
    try:
        logger.info(f'Received workflow execution request | session: {request.session_id}')
        engine = WorkflowEngine.load_from_json(request.workflow_config)
        stream = engine.run(request.input_data, session_id=request.session_id)

        def event_stream():
            for chunk in stream:
                yield chunk
            cost = engine.context.get('total_cost', 0)
            yield f"\n\n[COST:${engine.context.get('total_cost', 0):.6f}\n]"

        return StreamingResponse(event_stream() , media_type="text/plain")
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions", response_model=list[dict])
def list_sessions():
    sessions = session_manager.list_sessions()
    return sessions


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    if not session_id.strip():
        raise HTTPException(status_code=400)
    
    result = session_manager.delete_session(session_id)
    
    if result:
        return {"message": f"Session {session_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")



