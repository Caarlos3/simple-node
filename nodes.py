import os
import logging
from openai import OpenAI
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import WorkflowEngine

logger = logging.getLogger(__name__)


class BaseNode:

    def __init__(self, name: str):
        self.name = name
    
    def execute(self, input_data: str, engine: 'WorkflowEngine'):
        raise NotImplementedError('Each node must implement the execute method.')
    
    def to_dict(self):
        return {
            'id': self.name.lower().replace(" ", "_"),
            'type': self.__class__.__name__,
            'params': {}
        }


class UppercaseNode(BaseNode):

    def execute(self, input_data: str, engine: 'WorkflowEngine'):
        logger.info(f'Executing node {self.name} to convert to uppercase.')
        return input_data.upper()  
    
class ReverseNode(BaseNode):

    def execute(self, input_data: str, engine: 'WorkflowEngine'):
        logger.info(f'Executing node {self.name} to reverse the string.')
        return input_data[::-1]

class TrimNode(BaseNode):

    def execute(self, input_data: str, engine: 'WorkflowEngine'):
        logger.info(f'Executing node {self.name} to trim whitespace.')
        return input_data.strip()

class ReplaceNode(BaseNode):
    
    def __init__(self, name: str, old: str, new: str):
        super().__init__(name)
        self.old = old
        self.new = new

    def execute(self, input_data: str, engine: 'WorkflowEngine') -> str:
        logger.info(f'Executing node {self.name} to replace "{self.old}" with "{self.new}".')
        return input_data.replace(self.old, self.new)
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data['params'] = {
            'old': self.old,
            'new': self.new
        }
        return data

class FileReadNode(BaseNode):

    def __init__(self, name: str, file_path: str):
        super().__init__(name)
        self.file_path = file_path
    
    def execute(self, input_data: str, engine: 'WorkflowEngine') -> str:
        logger.info(f'Executing node {self.name} to read from file: {self.file_path}.')
        try:
            with open(self.file_path, 'r', encoding= "utf-8") as file:
                content = file.read()
                engine.context['file_content'] = content
            return input_data
        except FileNotFoundError:
            logger.error(f'File not found: {self.file_path}.')
            return(f'File not found: {self.file_path}.')
        except Exception as e:
            logger.error(f'An error occurred while reading the file: {e}.')
            return(f'An error occurred while reading the file: {e}')
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data['params'] = {
            'file_path': self.file_path
        }
        return data

class LLMNode(BaseNode):

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
        
    def execute(self, input_data: str, engine: 'WorkflowEngine') -> str:
        if engine.context.get('needs_ai') == False:
            return input_data
        
        context_info = engine.context.get('file_content', 'No hay información adicional disponible.')
        
        logger.info(f'Executing node {self.name} with context injection from file.')
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"{self.system_prompt}\n\n--- CONTEXTO RELEVANTE ---\n{context_info}"},
                    {"role": "user", "content": f"Pregunta: {input_data}"}
                ],
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f'An error occurred while processing with LLM: {e}.')
            return f'An error occurred while processing with LLM: {e}'
    
    def to_dict(self) -> dict:
       data = super().to_dict()
       data['params'] = {
           'model': self.model,
           'system_prompt': self.system_prompt,
           'temperature': self.temperature
       }
       return data
        

class RouterNode(BaseNode):

    def __init__(self, name: str):
        super().__init__(name)
        self.greetings = ["hello", "hi", "hey", "greetings", "quien eres", "who are you"]

    def execute(self, input_data: str, engine: 'WorkflowEngine') -> str:
        logger.info(f'Executing node {self.name} to route based on input.')
        clean_input = input_data.lower().strip()

        if any(greet in clean_input for greet in self.greetings):
            engine.context['needs_ai'] = False
            return "Hello! I'm Carlos virtual assistant. ¿How can I assist you today?"
        
        logger.info("No greeting detected, routing to LLMNode.")
        engine.context['needs_ai'] = True
        return input_data
    

def create_node_from_dict(data: dict) -> BaseNode:
    node_type = data['type']
    node_id = data['id']
    params = data.get('params', {})

    node_classes = {
        'UppercaseNode': UppercaseNode,
        'ReverseNode': ReverseNode,
        'TrimNode': TrimNode,
        'ReplaceNode': ReplaceNode,
        'FileReadNode': FileReadNode,
        'LLMNode': LLMNode,
        'RouterNode': RouterNode
    }

    if node_type not in node_classes:
        raise ValueError(f"Unknown node type: {node_type}")
    
    readable_name = node_id.replace("_", " ").title()
    
    if node_type in ['ReplaceNode', 'LLMNode', 'FileReadNode']:
        return node_classes[node_type](name=readable_name, **params)
    else:
        return node_classes[node_type](name=readable_name)