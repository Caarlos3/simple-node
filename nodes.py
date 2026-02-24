import os
import logging
import requests
from openai import OpenAI
from typing import TYPE_CHECKING
import tiktoken 

if TYPE_CHECKING:
    from engine import WorkflowEngine

logger = logging.getLogger(__name__)

"""
Workflow Nodes Module.
Contains the base interface and concrete implementations of processing nodes.
Each node performs a specific task and can interact with the global engine context.
"""


class BaseNode:

    """
    Abstract base class for all workflow nodes.
    Defines the contract that every node must follow.
    """

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

        if engine.context.get('skip_reader'):
           logger.info(f'Skipping FileReadNode, context already loaded')
           return input_data

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
    
class MemoryNode(BaseNode):
    """
    Manages conversation history by storing and retrieving past interactions.
    Limits the history to the most recent 'max_turns' exchanges to optimize token usage.
    Does not modify input_data; acts as a memory layer for downstream nodes (e.g., LLMNode).
    """

    def __init__(self, name: str, max_turns: int = 5):
        super().__init__(name)
        self.max_turns = max_turns

    def execute(self, input_data: str, engine: 'WorkflowEngine') -> str:
        logger.info(f'Executing node {self.name} for keep the information in conversation memory')
        history = engine.context.get('conversation_history', [])
        num_msg = self.max_turns * 2
        if len(history) > num_msg:
         engine.context['conversation_history'] = history[-num_msg:]
         logger.info(f'Memory trimmed to last {self.max_turns} turns ({num_msg} messages)')
        return input_data
   
    def to_dict(self) -> dict:
        return {
            'id': self.name,
            'type': 'MemoryNode',
            'params': {
                'max_turns': self.max_turns
            }
        }

        
        


class LLMNode(BaseNode):

    """
    AI Processing Node.
    Connects to Abacus RouteLLM to process text. It dynamically injects 
    context from the engine's shared memory into the system prompt.
    """

    def __init__(self, name: str, model: str, system_prompt: str, temperature: float = 0.4):
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
        
    def execute(self, input_data: str, engine: 'WorkflowEngine'):
        if engine.context.get('needs_ai') == False:
            return input_data
        
        context_info = engine.context.get('file_content', 'No hay información adicional disponible.')
        web_context = engine.context.get('Web Search', 'No encontrada busqueda' )
        
        logger.info(f'Executing node {self.name} with multi-source context (file + web).')

        acumulate_text = ""
        messages = [
                    {"role": "system", "content": f"{self.system_prompt}\n\n--- CONTEXTO DESDE ARCHIVO ---\n{context_info}\n\n---CONTEXTO DESDE WEB---\n{web_context}"},
                    *engine.context.get('conversation_history', []),
                    {"role": "user", "content": f"Pregunta: {input_data}"},
                ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                stream= True,
                messages= messages,
                temperature=self.temperature
            )
            for chunck in response:
                content = chunck.choices[0].delta.content
                if content:
                    yield content
                    acumulate_text += content

            enc = tiktoken.encoding_for_model(self.model)
            full_input = " ".join([m["content"] for m in messages])
            input_tokens = len(enc.encode(full_input))
            output_tokens = len(enc.encode(acumulate_text))
            total_tokens = input_tokens + output_tokens
            cost = (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.60 / 1_000_000)
            logger.info(f'Node {self.name} used {total_tokens} tokens (In: {input_tokens}, Out: {output_tokens} ) | Cost: ${cost:.6f}')
            previous_tokens = engine.context.get('total_tokens_used', 0)
            engine.context['total_tokens_used'] = previous_tokens + total_tokens
            previous_cost = engine.context.get('total_cost', 0)
            engine.context['total_cost'] = previous_cost + cost
            history = engine.context.get('conversation_history', [])
            history.append({"role": "user", "content": input_data})
            history.append({"role": "assistant", "content": acumulate_text})
            engine.context['conversation_history'] = history
            return 
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
    

class WebSearchNode(BaseNode):

    def __init__(self, name:str, query_prefix: str = "", max_results: int = 5):
        super().__init__(name)
        self.query_prefix = query_prefix
        self.max_results = max_results
        
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables. Please set it in the .env file.")
        
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"

    def execute(self, input_data: str, engine: 'WorkflowEngine') -> str:
        query = f"{self.query_prefix} {input_data}".strip()
        logger.info(f'Executing node {self.name} to perform web search with query: {query}')
        payload = {
            "query": query,
            "max_results": self.max_results,
            "search_depth": "basic",
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(self.base_url,json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            answer = data.get("answer", "")

            snippets = []

            if answer:
                snippets.append(f"Resume Tavily: {answer}")
            
            for idx, result in enumerate(results):
                title = result.get("title", "No Title")
                url = result.get("url", "No URL")
                snippet = result.get("snippet", "No Snippet")
                snippets.append(f"Result {idx + 1}:\nTitle: {title}\nURL: {url}\nSnippet: {snippet}\n")

            formatted_results = "\n".join(snippets) if snippets else "No results found."

            engine.context['Web Search'] = formatted_results

            return input_data
        except requests.exceptions.RequestException as e:
            logger.error(f'Error during web search: {e}.')
            if e.response is not None:
                 logger.error(f'Response status: {e.response.status_code}, body: {e.response.text}')
            engine.context["Web Search"] = f"Error during web search: {e}"
            return input_data
        
    def to_dict(self) -> dict:
        data = super().to_dict()
        data['params'] = {
            'query_prefix': self.query_prefix,
            'max_results': self.max_results
        }
        return data


            
          

class RouterNode(BaseNode):

    """
    Decision-making node.
    Analyzes user input to determine if it needs AI processing or 
    if it can be resolved with a static response, optimizing API credit usage.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.greetings = ["hello", "hi", "hey", "greetings", "quien eres", "who are you"]

    def execute(self, input_data: str, engine: 'WorkflowEngine') -> str:
        logger.info(f'Executing node {self.name} to route based on input.')
        clean_input = input_data.lower().strip()
        history = engine.context.get('conversation_history', [])


        if any(greet in clean_input for greet in self.greetings):
            engine.context['needs_ai'] = False
            return f"Hello! I'm Carlos virtual assistant. ¿How can I assist you today?"
        
        elif len(history) > 0:
            logger.info(f"Existing session detected, routing directly to LlMNode")
            engine.context['needs_ai'] = True
            engine.context['skip_reader'] = True
            return input_data
        
        else:
            logger.info(f"New session detected, routing to ReaderNode")
            engine.context['needs_ai'] = True
            engine.context['skip_reader'] = False
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
        'RouterNode': RouterNode,
        'WebSearchNode': WebSearchNode,
        'MemoryNode': MemoryNode,
    }

    if node_type not in node_classes:
        raise ValueError(f"Unknown node type: {node_type}")
    
    readable_name = node_id.replace("_", " ").title()
    
    if node_type in ['ReplaceNode', 'LLMNode', 'FileReadNode', 'WebSearchNode']:
        return node_classes[node_type](name=readable_name, **params)
    elif node_type == 'MemoryNode':
        return MemoryNode(
            name=node_id,
            max_turns=params.get('max_turns', 5)
        )
    else:
        return node_classes[node_type](name=readable_name)
    




   