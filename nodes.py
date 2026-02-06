import os
import logging
from openai import OpenAI
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

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

class LLMNode(BaseNode):

    """
    AI Processing Node.
    Connects to Abacus RouteLLM to process text. It dynamically injects 
    context from the engine's shared memory into the system prompt.
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
        
    def execute(self, input_data: str, engine: 'WorkflowEngine') -> str:

        if engine.context.get('needs_ai') == False:
            return input_data
        
        logger.info(f'Executing node {self.name} to process input with LLM model: {self.model}, temperature: {self.temperature}.')
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
            logger.error(f'An error occurred while processing with LLM: {e}.')
            return f'An error occurred while processing with LLM: {e}'
        

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

        if any(greet in clean_input for greet in self.greetings):
            engine.context['needs_ai'] = False
            return "Hello! I'm Carlos virtual assitent ¿How can I assist you today?"
        logger.info("No greeting detected, routing to LLMNode.")
        engine.context['need_ai'] = True
        return input_data
    