class BaseNode:

    def __init__(self, name: str):
        self.name = name
    
    def execute(self, input_data: str):
        raise NotImplementedError('Each node must implement the execution method.')


class UppercaseNode(BaseNode):

    def execute(self, input_data: str):
        print(f'Executing node {self.name} to convert to uppercase.')
        return input_data.upper()  

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