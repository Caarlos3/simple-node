from nodes import BaseNode

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

    def add_node(self, node: BaseNode) -> None:
        self.nodes.append(node)
    
    def run(self, input_data: str) -> str:
        self.context['user_input'] = input_data
        current_data = input_data
        for node in self.nodes:
            current_data = node.execute(current_data, self)
        return current_data