import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class BaseNode:

    def __init__(self, name: str):
        self.name = name
    
    def execute(self, input_data: str):
        raise NotImplementedError('Each node must implement the execute method.')


class UppercaseNode(BaseNode):

    def execute(self, input_data: str):
        print(f'Executing node {self.name} to convert to uppercase.')
        return input_data.upper()  
    
class ReverseNode(BaseNode):

    def execute(self, input_data: str):
        print(f'Executing node {self.name} to reverse the string.')
        return input_data[::-1]

class TrimNode(BaseNode):

    def execute(self, input_data: str):
        print(f'Executing node {self.name} to trim whitespace.')
        return input_data.strip()

class ReplaceNode(BaseNode):
    
    def __init__(self, name: str, old: str, new: str):
        super().__init__(name)
        self.old = old
        self.new = new

    def execute(self, input_data: str) -> str:
        print(f'Executing node {self.name} to replace "{self.old}" with "{self.new}".')
        return input_data.replace(self.old, self.new)

class FileReadNode(BaseNode):

    def __init__(self, name: str, file_path: str):
        super().__init__(name)
        self.file_path = file_path
    
    def execute(self, input_data: str) -> str:
        print(f'Executing node {self.name} to read from file: {self.file_path}.')
        try:
            with open(self.file_path, 'r', encoding= "utf-8") as file:
                content = file.read()
            return content
        except FileNotFoundError:
            return(f'File not found: {self.file_path}.')
        except Exception as e:
            return(f'An error occurred while reading the file: {e}')

class LLMNode(BaseNode):

    """
    Node that processes input text using Abacus AI RouteLLM models.
    It requires a valid ROUTELLM_API_KEY in the .env file.
    """

    def __init__(self, name: str, model: str, system_prompt: str, temperature: float = 0.7):
        super().__init__(name)
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature

        api_key = os.getenv("ROUTELLM_API_KEY")
        if not api_key:
            raise ValueError("ROUTELLM_API_KEY not found in environment variables. Please set it in the .env file.")
        

        self.client = OpenAI(
            base_url="https://routellm.abacus.ai/v1",
            api_key=api_key
            )
        
    def execute(self, input_data: str) -> str:
        print(f'Executing node {self.name} to process input with LLM model: {self.model}, temperature: {self.temperature}.')
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Based on the information provided, please answer the following question: {input_data}"}
                ],
                temperature=self.temperature

            )
            return response.choices[0].message.content
        except Exception as e:
            return f'An error occurred while processing with LLM: {e}'

      


class WorkflowEngine:

    def __init__(self):
        self.nodes: list[BaseNode] = []

    def add_node(self, node: BaseNode) -> None:
        self.nodes.append(node)
    
    def run(self, input_data: str) -> str:
        current_data = input_data
        for node in self.nodes:
            current_data = node.execute(current_data)
        return current_data
    

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

    


