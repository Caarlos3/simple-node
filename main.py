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