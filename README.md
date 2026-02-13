 # 🤖 Simple Node AI Engine

![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square&logo=github)
![Python Version](https://img.shields.io/badge/python-3.12-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat-square&logo=fastapi)
![Tests](https://img.shields.io/badge/tests-8%20passed-success?style=flat-square&logo=pytest)

A modular workflow engine built with Python to understand how node-based automation systems work. The goal is to create an AI-first automation platform where tasks can be chained through customizable nodes with persistent memory and dynamic routing.

## ✨ Current Features

The engine can create workflows and process data through multiple specialized node types:

### 🔗 Core Nodes
- **FileReadNode**: Reads local files with robust error handling (useful for providing CV/context to the engine)
- **ReplaceNode**: Replaces specific text patterns with configurable parameters
- **UppercaseNode**: Converts text to uppercase
- **TrimNode**: Removes leading and trailing whitespace
- **ReverseNode**: Reverses the input string

### 🤖 AI-Powered Nodes
- **LLMNode**: Integrates with Abacus RouteLLM API for intelligent text processing with context injection
- **RouterNode**: Decision-making node that optimizes API usage by routing simple queries to static responses
- **WebSearchNode**: Performs web searches via Tavily API and injects results into the workflow context
- **MemoryNode**: Manages conversation history with configurable turn limits for token optimization

### 🔄 Workflow Management
- **JSON-based workflow persistence**: Save and load complete workflow configurations
- **Dynamic node factory**: Create nodes from JSON definitions at runtime
- **Shared context system**: All nodes can read/write to a global memory space
- **Sequential execution**: Nodes execute in order with data passing between them

### 🌐 REST API
- FastAPI-based HTTP interface
- Swagger UI documentation at `/docs`
- Dynamic workflow loading from JSON files
- Context summary in responses for debugging

## 🛠️ Tech Stack

- **Python 3.12**
- **FastAPI** - Modern web framework for building APIs
- **OpenAI SDK** - For LLM integration via RouteLLM
- **Requests** - HTTP client for web search integration
- **Pytest** - Unit and integration testing
- **Pydantic** - Data validation
- **python-dotenv** - Environment variable management

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Virtual environment (venv)
- API Keys:
  - `ROUTELLM_API_KEY` (Abacus RouteLLM)
  - `TAVILY_API_KEY` (optional, for web search)

### Setup

1) Clone the repository and enter the project folder:

git clone https://github.com/Caarlos3/simple-node.git
cd simple-node

2) Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate

3) Install dependencies:

pip install -r requirements.txt

4) Create a `.env` file in the root directory:

ROUTELLM_API_KEY=your_routellm_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

5) Run the API server:

uvicorn api:app --reload

6) Open your browser and go to `http://localhost:8000/docs` to see the interactive API documentation.

## 🧪 Running Tests

Activate the venv and run:

source venv/bin/activate
python3 -m pytest -v

## 📂 Project Structure

simple-node/
├── api.py                    # FastAPI REST endpoints
├── engine.py                 # Workflow orchestration engine
├── nodes.py                  # Node implementations and factory
├── test/
│   └── test_workflow.py      # Unit and integration tests
├── workflows/
│   ├── workflow_example.json # Basic workflow example
│   └── workflow_memory.json  # Conversational AI with memory
├── my_info.txt               # Sample context file for testing
├── requirements.txt          # Python dependencies
├── .env                      # API keys (not in repo)
└── README.md

## 📋 Example Workflow

Here's a simple conversational AI workflow with memory (`workflow_memory.json`):

{
    "flow_name": "Chat memory",
    "nodes": [
        {
            "id": "memory_manager",
            "type": "MemoryNode",
            "params": {"max_turns": 5}
        },
        {
            "id": "llm",
            "type": "LLMNode",
            "params": {
                "model": "gpt-4o-mini",
                "system_prompt": "You are a friendly assistant who remembers what we talked about.",
                "temperature": 0.4
            }
        }
    ],
    "connections": [
        {"from": "memory_manager", "to": "llm"}
    ]
}

## 🗺️ Development Roadmap

### ✅ Completed
- [x] Core workflow engine with sequential execution
- [x] Basic text transformation nodes
- [x] LLM integration with context injection
- [x] Web search capabilities
- [x] Conversation memory management
- [x] JSON-based workflow persistence
- [x] REST API with FastAPI
- [x] Dynamic node factory pattern

### 🚧 In Progress (Feature Branch: `feature/memory-node`)
- [ ] **Session-based memory persistence** (file-based storage by `session_id`)
- [ ] Multi-turn conversations that survive server restarts

### 🔮 Planned
- [ ] Database integration for scalable memory storage
- [ ] Parallel node execution (DAG support)
- [ ] Visual workflow editor (web UI)
- [ ] More node types (CSV, JSON transformations, email, etc.)
- [ ] Webhook triggers
- [ ] Scheduled workflow execution

## 🤝 Contributing

This is a learning project, but suggestions and improvements are welcome! Feel free to open an issue or submit a pull request.

## 📝 License

This project is open source and available for learning purposes.

---

**Built by Carlos Ramírez Torres** | Learning AI Development Day by Day 🚀
