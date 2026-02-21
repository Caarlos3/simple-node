import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from engine import WorkflowEngine
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Simple-Node API",
    description="Api for executing workflows nodes",
    version="0.1.0",
    )

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
        result = engine.run(request.input_data, session_id=request.session_id)

        return {
            "status": "success",
            "input": request.input_data,
            "output": result,
            "tokens_used": engine.context.get('total_tokens_used', 0),
            "context_summary": {k: (v[:50] + "..." if isinstance(v, str) and len(v) > 50 else v)
                                for k, v in engine.context.items()}
        }
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


        
         
        
