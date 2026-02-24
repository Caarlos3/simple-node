import logging
import json
import os
import time 
from nodes import BaseNode, create_node_from_dict 
from session_manager import SessionManager


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
        self.session_manager = SessionManager()

    def add_node(self, node: BaseNode) -> None:
        self.nodes.append(node)

    
    def run(self, input_data: str, session_id: str = None):
        self.context['user_input'] = input_data
        current_data = input_data

        for i, node in enumerate(self.nodes):
            start_time = time.time()
            result = node.execute(current_data, self)

            if hasattr(result, "__iter__") and not isinstance(result, (list, str)):
                collected_text = ""
                try:
                   for chunk in result:
                       yield chunk
                       collected_text += chunk
                   current_data = collected_text
                except Exception as e:
                    logger.error(f"Error streaming from node {node.name}: {e}")
                    raise e
            else:
                current_data = result
                if i == len(self.nodes) - 1:
                    yield result
            duration = time.time() - start_time
            logger.info(f'Node {node.name} executed in {duration:.3f}s')

        if session_id:
            self.session_manager.save_history(session_id, self.context)
    
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