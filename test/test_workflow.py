import pytest
from main import WorkflowEngine, UppercaseNode, ReverseNode, TrimNode, ReplaceNode, FileReadNode


def test_workflow_engine():
    engine = WorkflowEngine()
    engine.add_node(TrimNode("Trim Node"))
    engine.add_node(UppercaseNode("Uppercase Node"))
    engine.add_node(ReverseNode("Reverse Node"))

    input_data = "   Hello World   "
    result = engine.run(input_data)

    assert result == "DLROW OLLEH"

def test_trim_node():
    trim_node = TrimNode("Trim Node")
    input_data = "   Hello World   "
    result = trim_node.execute(input_data)
    assert result == "Hello World"

def test_uppercase_node():
    uppercase_node = UppercaseNode("Uppercase Node")
    input_data = "Hello World"
    result = uppercase_node.execute(input_data)
    assert result == "HELLO WORLD"

def test_reverse_node():
    reverse_node = ReverseNode("Reverse Node")
    input_data = "Hello World"
    result = reverse_node.execute(input_data)
    assert result == "dlroW olleH"


def test_replace_node():
    replace_node = ReplaceNode("Replace Node", "World", "Boss")
    input_data = "Hello World"
    result = replace_node.execute(input_data)
    assert result == "Hello Boss"

def test_file_read_node_success():
    file_node = FileReadNode("File Node", "my_info.txt")
    result = file_node.execute("")
    assert "Carlos" in result

def test_file_read_node_error():
    file_node = FileReadNode("File Node", "non_existent_file.txt")
    result = file_node.execute("")
    assert result == "File not found: non_existent_file.txt."

def test_file_read_node_empty():
    node = FileReadNode("Empty File Node", "empty.txt")
    assert node.execute("") == ""






