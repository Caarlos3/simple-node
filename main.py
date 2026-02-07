import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from engine import WorkflowEngine
from nodes import LLMNode, FileReadNode, RouterNode
load_dotenv()

if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ])
logger = logging.getLogger(__name__)


"""
Main Entry Point.
Configures and executes the AI Portfolio Assistant workflow.
"""


if __name__ == "__main__":

    # Initialize the engine and define the intelligent pipeline

    with open("my_info.txt", "r", encoding="utf-8") as f:
        context = f.read()

    engine = WorkflowEngine()

    router = RouterNode(name="Input Router")

    reader = FileReadNode(name="File Reader", file_path="my_info.txt")
    
    ai_node = LLMNode(
        name="LLM Processor",
        model="abacusai/dreamina",
        system_prompt= "You are the professional AI assistant for Carlos, a Full Stack Developer."
    )
    engine.add_node(router)
    engine.add_node(reader)
    engine.add_node(ai_node)


    question = "Can you provide a brief summary of Carlos's professional background?"
    engine.save_to_json("current_workflow.json")

    


