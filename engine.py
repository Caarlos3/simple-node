from nodes import BaseNode

class WorkflowEngine:

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