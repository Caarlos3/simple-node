import logging
import os
from dotenv import load_dotenv
from engine import WorkflowEngine

load_dotenv()

if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(),
    ])
logger = logging.getLogger(__name__)


"""
Main Entry Point.
Configures and executes the AI Portfolio Assistant workflow.
"""


if __name__ == "__main__":

    # Initialize the engine and define the intelligent pipeline

    engine = WorkflowEngine.load_from_json("workflow_example.json")

    question = "Can you provide a brief summary of Carlos's professional background?"
    answer = engine.run(question)
    print("AI Response (loaded from JSON):", answer)
    engine.save_to_json("current_workflow.json")

    


