# 🤖 GenAgent Pro - Agentic AI Workflow Engine

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.16-green.svg)](https://github.com/langchain-ai/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini-2.5-orange.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**GenAgent Pro** is an enterprise-grade, multi-agent AI system that autonomously plans, executes, validates, and completes real-world workflows end-to-end.

Unlike simple chatbots, GenAgent Pro features true **agentic collaboration** with specialized agents that reason, plan, act, and learn from their actions.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://genagent-pro-agentic-ai-workflow-hxjfvucfnkubzabfj32pnn.streamlit.app/)

---

## 🌟 Key Features

✅ **True Multi-Agent System** - Not a single chatbot; multiple specialized agents collaborate  
✅ **LangGraph Orchestration** - State machine-based workflow with conditional routing  
✅ **Google Gemini Powered** - Uses Gemini 1.5 Flash/Pro (free tier friendly)  
✅ **Tool Calling** - File reading, Python execution, calculations, memory search  
✅ **Vector Memory** - FAISS-based semantic memory with context retrieval  
✅ **Production-Ready** - Clean architecture, error handling, logging  
✅ **Multiple Interfaces** - CLI, Interactive CLI, and Streamlit web UI  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                            │
│          (CLI / Interactive / Streamlit Web UI)              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              LANGGRAPH ORCHESTRATION LAYER                   │
│                                                              │
│    START → PLANNER → EXECUTOR → VALIDATOR → MEMORY → END    │
│              ↑          ↓           ↓                        │
│              └──────────┴───────────┘ (retry loop)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     TOOLS LAYER                              │
│    [File Reader] [Python Exec] [Calculator] [Memory]        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                MEMORY LAYER (FAISS)                          │
│          [Vector Store] [Conversation History]               │
└─────────────────────────────────────────────────────────────┘
```

### 🤖 Agent Roles

| Agent | Role | Responsibility |
|-------|------|----------------|
| **Planner** | Strategic Planner | Breaks goals into executable tasks |
| **Executor** | Task Executor | Executes tasks using tools |
| **Validator** | Quality Checker | Verifies outputs, requests retries |
| **Memory** | Context Manager | Stores/retrieves conversation context |

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/yourusername/genagent-pro.git
cd genagent-pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup API Key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

**Get your free Gemini API key**: [https://ai.google.dev/](https://ai.google.dev/)

### 3. Run the Application

**Option A: CLI (Single Query)**
```bash
python main.py "Calculate the average of 10, 20, 30, 40, 50"
```

**Option B: Interactive CLI**
```bash
python main.py
# Then type your queries interactively
```

**Option C: Streamlit Web UI**
```bash
streamlit run app.py
# Opens browser at http://localhost:8501
```

---

## 📖 Usage Examples

### Example 1: Simple Calculation

```
User: Calculate 15% of 890

Workflow:
1. Planner creates task: "Use calculator to compute 890 * 0.15"
2. Executor calls calculator tool
3. Validator checks result
4. Output: "133.5"
```

### Example 2: Python Code Execution

```
User: Generate first 10 Fibonacci numbers using Python

Workflow:
1. Planner: "Write Python code for Fibonacci sequence"
2. Executor: Runs python_executor tool
3. Validator: Checks output format
4. Output: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### Example 3: Multi-Step Task

```
User: Read data.csv, calculate average of column 'sales', 
      then multiply by 1.15 for tax

Workflow:
1. Planner creates 3 tasks:
   - Task 1: Read CSV file
   - Task 2: Calculate average
   - Task 3: Apply tax multiplier
2. Executor executes sequentially with dependencies
3. Validator verifies final result
```

### Example 4: Memory Recall

```
User: What did we discuss yesterday about the project?

Workflow:
1. Planner: "Search memory for past conversation"
2. Executor: Uses memory_search tool
3. Memory: Retrieves relevant context from vector store
4. Output: Context from past conversations
```

---

## 🛠️ Tools

| Tool | Description | Example Use |
|------|-------------|-------------|
| **file_reader** | Read PDF, TXT, CSV, DOCX files | "Read report.pdf" |
| **python_executor** | Safe Python code execution | "Run this code: print(2**10)" |
| **calculator** | Math expression evaluation | "Calculate sqrt(144) + 5" |
| **memory_search** | Vector similarity search | "Find past conversations about X" |

---

## ⚙️ Configuration

Edit `config.yaml` to customize behavior:

```yaml
llm:
  model: "gemini-1.5-flash"
  temperature: 0.7
  max_tokens: 8192

agents:
  planner:
    temperature: 0.3  # More deterministic
  executor:
    temperature: 0.5
  validator:
    temperature: 0.2  # Very deterministic

workflow:
  max_iterations: 10
  retry_on_failure: true
  max_retries: 2
```

---

## 📁 Project Structure

```
genagent_pro/
├── main.py                  # CLI entry point
├── app.py                   # Streamlit web UI
├── requirements.txt         # Dependencies
├── config.yaml              # Configuration
├── .env.example             # Environment template
│
├── core/
│   ├── state.py            # Workflow state schema
│   ├── orchestrator.py     # LangGraph workflow
│   └── llm_factory.py      # LLM initialization
│
├── agents/
│   ├── base_agent.py       # Agent base class
│   ├── planner_agent.py    # Planning agent
│   ├── executor_agent.py   # Execution agent
│   ├── validator_agent.py  # Validation agent
│   └── memory_agent.py     # Memory agent
│
├── tools/
│   ├── base_tool.py        # Tool interface
│   ├── file_reader.py      # Document reader
│   ├── python_executor.py  # Code executor
│   ├── calculator.py       # Math tool
│   └── memory_search.py    # Memory search
│
├── memory/
│   ├── vector_store.py     # FAISS vector store
│   └── conversation_memory.py
│
└── utils/
    ├── logger.py           # Logging setup
    └── helpers.py          # Utilities
```

---

## 🧪 Testing

Run tests:

```bash
pytest tests/
```

Test specific component:

```bash
pytest tests/test_workflow.py -v
```

---

## 🔒 Security

- **Sandboxed Python Execution**: Uses `RestrictedPython` to prevent dangerous operations
- **File Access Control**: Limits file sizes and formats
- **Input Validation**: Validates all tool inputs
- **No Direct Shell Access**: Agents cannot execute arbitrary shell commands

---

## 📊 Logging

Logs are stored in `./data/logs/genagent.log`

View logs:

```bash
tail -f ./data/logs/genagent.log
```

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`

Change log level in `.env`:

```env
LOG_LEVEL=DEBUG
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [Google Gemini](https://ai.google.dev/)
- Vector search by [FAISS](https://github.com/facebookresearch/faiss)
- Embeddings by [Sentence Transformers](https://www.sbert.net/)

---

## 📧 Contact

For questions or support:
- LinkedIn: [Create an issue](https://www.linkedin.com/in/vignesh246v-ai-engineer/)
- Email: vignesh246v@gmail.com

---

**⭐ Star this repo if you find it useful!**

Made with ❤️ using AI-powered automation
