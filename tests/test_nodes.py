import os
import sys
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pytest
from nodes import UppercaseNode, ReverseNode, TrimNode, ReplaceNode, FileReadNode, RouterNode, LLMNode
from engine import WorkflowEngine


@pytest.fixture
def mock_engine():

    class MockEngine:
        def __init__(self):
            self.context = {}
    return MockEngine()

@pytest.fixture
def workflow_engine():
    return WorkflowEngine()


def test_workflow_engine(workflow_engine):
    workflow_engine.add_node(TrimNode("Trim Node"))
    workflow_engine.add_node(UppercaseNode("Uppercase Node"))
    workflow_engine.add_node(ReverseNode("Reverse Node"))

    input_data = "   Hello World   "
    result = workflow_engine.run(input_data)

    assert result == "DLROW OLLEH"

def test_trim_node(mock_engine):
    trim_node = TrimNode("Trim Node")
    input_data = "   Hello World   "
    result = trim_node.execute(input_data, mock_engine)
    assert result == "Hello World"

def test_uppercase_node():
    uppercase_node = UppercaseNode("Uppercase Node")
    input_data = "Hello World"
    result = uppercase_node.execute(input_data, mock_engine)
    assert result == "HELLO WORLD"

def test_reverse_node():
    reverse_node = ReverseNode("Reverse Node")
    input_data = "Hello World"
    result = reverse_node.execute(input_data, mock_engine)
    assert result == "dlroW olleH"


def test_replace_node():
    replace_node = ReplaceNode("Replace Node", "World", "Boss")
    input_data = "Hello World"
    result = replace_node.execute(input_data, mock_engine)
    assert result == "Hello Boss"

def test_file_read_node_success(mock_engine, tmp_path):
    file_path = tmp_path / "my_info.txt"
    file_path.write_text("Carlos is a software developer.", encoding="utf-8")
    file_node = FileReadNode("File Node", str(file_path))
    result = file_node.execute("", mock_engine)
    assert "Carlos" in mock_engine.context.get('file_content', '')
    assert result == ""

def test_file_read_node_error(mock_engine):
    file_node = FileReadNode("File Node", "non_existent_file.txt")
    result = file_node.execute("", mock_engine)
    assert result == "File not found: non_existent_file.txt."
    assert 'file_content' not in mock_engine.context

def test_file_read_node_empty(mock_engine, tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("", encoding="utf-8")
    file_node = FileReadNode("Empty File Node", str(file_path))
    result = file_node.execute("", mock_engine)
    assert mock_engine.context.get('file_content', '') == ""
    assert result == ""

def test_router_node_greeting(mock_engine):
    router = RouterNode("Router")
    result = router.execute("Hello", mock_engine)

    assert mock_engine.context.get('needs_ai') is False
    assert "carlos" in result.lower()

def test_router_node_query(mock_engine):
    router = RouterNode("Router")
    query = "Can you provide a brief summary of Carlos's professional background?"
    result = router.execute(query, mock_engine)

    assert mock_engine.context.get('needs_ai') is True
    assert result == query


def test_llm_node_with_mock(mock_engine, monkeypatch):
    monkeypatch.setenv("ROUTELLM_API_KEY", "test_api_key")
    node = LLMNode("AI Node", "gpt-4o", "You are a helpful assistant.")
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Mocked AI response."

    with patch.object(node.client.chat.completions, 'create', return_value=mock_response) as mock_create:
        result = node.execute("¿Quien es Carlos?", mock_engine)
        mock_create.assert_called_once()

    assert result == "Mocked AI response."

def test_llm_node_skip_ai(mock_engine, monkeypatch):
    monkeypatch.setenv("ROUTELLM_API_KEY", "test_api_key")
    node = LLMNode("AI Node", "gpt-4o", "System prompt.")
    mock_engine.context['needs_ai'] = False

    result = node.execute("Input", mock_engine)

    assert result == "Input"

def test_llm_node_handle_api_error(mock_engine, monkeypatch):
    monkeypatch.setenv("ROUTELLM_API_KEY", "test_api_key")
    node = LLMNode("AI Node", "gpt-4o", "System prompt.")
    
    with patch.object(node.client.chat.completions, 'create', side_effect=Exception("API error")):
        result = node.execute("Test query", mock_engine)

    assert "API error" in result

        





