# 🤖 Simple Node AI Engine

A modular workflow engine built with Python to understand how node-based automation systems work. The goal is to create an AI-first automation platform where tasks can be chained through customizable nodes.

## ✨ Current Features

The engine can already create workflows and process data through multiple node types:

- FileReadNode: Reads local files with robust error handling (useful for providing CV/context to the engine)
- ReplaceNode: Replaces specific text patterns with configurable parameters
- UppercaseNode: Converts text to uppercase
- TrimNode: Removes leading and trailing whitespace
- ReverseNode: Reverses the input string

## 🛠️ Tech Stack

- Python 3.12
- Pytest (unit + integration tests)
- Type hints
- Error handling (try/except to avoid crashes on missing files and unexpected errors)

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Virtual environment (venv)

### Setup

1) Clone the repository and enter the project folder:

git clone https://github.com/Caarlos3/simple-node.git
cd simple-node

2) Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate

3) Install dependencies:

pip install -r requirements.txt

## Running Tests

Activate the venv and run:

source venv/bin/activate
python3 -m pytest -v

## 📂 Project Structure

simple-node/
  main.py              # Core engine and node classes
  test/
    test_workflow.py   # Unit and integration tests
  my_info.txt          # Sample context file for testing
  requirements.txt     # Python dependencies
  README.md

## 🎯 Next Steps

- Integrate OpenAI API nodes
- Add environment variable management (.env)
- Build a simple CLI interface
- Create data transformation nodes (JSON, CSV)

## 📝 License

This project is open source and available for learning purposes.

Built by Carlos Ramírez Torres 
