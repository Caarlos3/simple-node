import logging
import json
import os
from nodes import BaseNode, create_node_from_dict 


logger = logging.getLogger(__name__)

"""
Workflow Engine Module.
Core logic for orchestrating sequential node execution and managing 
shared context (flow memory).
"""

class WorkflowEngine:

    """
    Orchestrates the execution of multiple nodes.
    Maintains a shared 'context' dictionary that acts as a common
    memory for all nodes in the pipeline.
    """ 

    def __init__(self):
        self.nodes: list[BaseNode] = []
        self.context: dict = {}
        self.flow_name: str = "Unnamed Workflow"

    def add_node(self, node: BaseNode) -> None:
        self.nodes.append(node)

    def _get_session_path(self, session_id: str) -> str:
        return f"memory/{session_id}.json"
       
    
    def _load_session(self, session_id: str) -> None:
        file_path = self._get_session_path(session_id)

        
        if os.path.exists(file_path):
            try:
                 with open (file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.context['conversation_history'] = data
                    logger.info(f'session loaded: {file_path} ({len(data)})')
            
            except json.JSONDecodeError:
                corrupted_path = f'{file_path}.corrupted'
                logger.error(f'Corrupted JSON in {file_path}') 

                try:
                    os.rename(file_path, corrupted_path)
                except Exception as rename_error:
                    logger.error(f'Could not rename corrupted file: {rename_error}. Renaming to {corrupted_path}')
                self.context['conversation_history'] = []
            
            except Exception as e:
                logger.error(f'Unexpected error: {e}')
                self.context['conversation_history'] = []
            
        else:
             logger.info("Session not found")
    

    
    def _save_session(self, session_id: str) -> None:
        file_path = self._get_session_path(session_id)
        os.makedirs("memory", exist_ok=True)
        history = self.context.get('conversation_history', [])
        with open (file_path, 'w') as f:
            json.dump(history, f, indent=4)
        
        logger.info(f'session saved: {file_path} ({len(history)})')
    
    def run(self, input_data: str, session_id: str = None) -> str:
        self.context['user_input'] = input_data
        
        if session_id:
            self._load_session(session_id)

        current_data = input_data
        for node in self.nodes:
            current_data = node.execute(current_data, self)
        
        if session_id:
            self._save_session(session_id)
                
        return current_data
    
    def save_to_json(self, file_path: str) -> None:
        """Serializes the current workflow configuration and context to a JSON file."""
        workflow_data = {
            'flow_name': 'Exported Workflow',
            'nodes': [node.to_dict() for node in self.nodes],
            'connections': self._generate_connections()
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=4, ensure_ascii=False)
        logger.info(f'Workflow saved to {file_path} successfully.')

    def _generate_connections(self) -> list[dict]:
        """Generates a list of connections between nodes based on their order."""
        connections = []
        node_ids = [node.to_dict()['id'] for node in self.nodes]
        for i in range(len(self.nodes) - 1):
            connections.append({
                'from': node_ids[i],
                'to': node_ids[i + 1]
            })
        return connections
    
    @classmethod
    def load_from_json(cls, file_path: str) -> 'WorkflowEngine':
        """Loads a workflow configuration from a JSON file and constructs the engine."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        engine = cls()
        engine.flow_name = data.get('flow_name', 'Unnamed Workflow')
       
        for node_data in data['nodes']:
            node = create_node_from_dict(node_data)
            engine.add_node(node)

        logger.info(f'Workflow loaded from {file_path} successfully.')
        return engine