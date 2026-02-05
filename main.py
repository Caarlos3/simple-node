import os
from dotenv import load_dotenv
from openai import OpenAI
from engine import WorkflowEngine
from nodes import LLMNode

load_dotenv()


if __name__ == "__main__":

    with open("my_info.txt", "r", encoding="utf-8") as f:
        context = f.read()

    engine = WorkflowEngine()
    
    ai_node = LLMNode(
        name="LLM Processor",
        model="abacusai/dreamina",
        system_prompt= (
            f"You are the professional AI assistant for Carlos, a Full Stack Developer. "
            f"Your mission is to assist recruiters and collaborators by providing accurate information about Carlos's career. "
            f"Use the following context as your only source of truth:\n\n"
            f"{context}\n\n"
            f"GUIDELINES:\n"
            f"1. Answer questions based ONLY on the provided context.\n"
            f"2. If the information is not available, politely state that you don't have that specific detail and suggest contacting Carlos.\n"
            f"3. Maintain a professional, helpful, and proactive tone.\n"
            f"4. You can answer in the same language as the user's question (Spanish or English)."
    )
    )
    engine.add_node(ai_node)

    question = "Can you provide a brief summary of Carlos's professional background?"
    answer = engine.run(question)
    print("AI Response:")
    print(answer)

    


