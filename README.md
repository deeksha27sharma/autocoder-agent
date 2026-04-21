# 🤖 AutoCoder Agent

An autonomous AI coding assistant that writes, executes, debugs, and explains Python code — all on its own.

Built as a Final Year Project using LangGraph, Groq (LLaMA 3.3 70B), ChromaDB, FastAPI, and Streamlit.



## 🎯 What It Does

Give it a coding task in plain English. The agent will:
1. **Plan** — decide whether to write fresh code or debug existing code
2. **Write** — generate clean, working Python code
3. **Execute** — run the code in a safe sandbox
4. **Debug** — if code fails, analyze the error and fix it automatically
5. **Remember** — save successful solutions to memory for future reuse
6. **Explain** — describe what the code does in plain English



## 🏗️ Architecture
```
User Input
↓
Planner Node (LLaMA 3.3 70B via Groq)
↓
Writer Node ──→ Code Executor (subprocess sandbox)
↓                  ↓ error?
Debugger Node ←────────┘
↓ success
Explainer Node
↓
ChromaDB Memory (save solution)
↓
Final Response
```


## 🛠️ Tech Stack

| Component        | Technology                  |
|------------------|-----------------------------|
| LLM              | LLaMA 3.3 70B (Groq API)    |
| Agent Framework  | LangGraph                   |
| Code Execution   | Python subprocess + tempfile|
| Vector Memory    | ChromaDB + MiniLM embeddings|
| Backend API      | FastAPI + Uvicorn           |
| Frontend UI      | Streamlit                   |



## 📁 Project Structure
```
autocoder-agent/
├── agent/
│   ├── graph.py          # LangGraph state machine
│   ├── tools.py          # write, debug, explain tools
│   ├── prompts.py        # all LLM prompts
│   └── memory.py         # ChromaDB vector memory
├── api/
│   └── main.py           # FastAPI backend
├── ui/
│   └── app.py            # Streamlit frontend
├── sandbox/
│   └── executor.py       # safe code execution
├── evaluation/
│   ├── benchmark.py      # benchmark runner
│   ├── benchmark_results.json
│   └── benchmark_chart.png
├── memory/
│   └── chroma_store/     # persisted vector memory
├── .env
├── requirements.txt
└── README.md
```


## ⚡ Installation

##  Quick Start

Try the live demo instantly — no installation needed:
```
 [https://autocoder-diksha.streamlit.app](https://autocoder-diksha.streamlit.app)
```
Or run locally by following the installation steps below.


### 1. Clone the repo
```bash
git clone https://github.com/deeksha27sharma/autocoder-agent.git
cd autocoder-agent
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root:
```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
```
Get a free Groq API key at: https://console.groq.com



## 🚀 Running the Project

### Option 1: Streamlit UI (recommended for demo)
```bash
streamlit run ui/app.py
```
Open http://localhost:8501

### Option 2: FastAPI Backend
```bash
uvicorn api.main:app --reload
```
Open http://127.0.0.1:8000/docs

### Option 3: Run agent directly
```python
from agent.graph import run_agent
result = run_agent("Write a function to find all prime numbers up to n")
```



## 📊 Benchmark Results

Evaluated on 10 standard Python coding tasks:

| Metric         | Score        |
|----------------|--------------|
| Pass Rate      | 100%         |
| Tasks Passed   | 10/10        |
| Avg Attempts   | 1.0          |
| Model Used     | LLaMA 3.3 70B|



## 🔑 Key Features

- **Autonomous ReAct Loop** — agent reasons and acts without human input
- **Self-Healing** — automatically detects and fixes code errors (up to 3 retries)
- **Persistent Memory** — ChromaDB stores past solutions, retrieved via semantic search
- **REST API** — FastAPI backend with Swagger UI for easy testing
- **Chat Interface** — Streamlit UI for interactive demo
- **Benchmarking** — evaluated on 10 tasks with pass rate metrics


##  Live Demo
```
| Link |
|---|---|
|  Streamlit UI | [autocoder-diksha.streamlit.app](https://autocoder-diksha.streamlit.app) |
|  API Docs | [autocoder-agent.onrender.com/docs](https://autocoder-agent.onrender.com/docs) |
|  GitHub | [deeksha27sharma/autocoder-agent](https://github.com/deeksha27sharma/autocoder-agent) |
```
> ⚠️ Note: API is hosted on Render free tier — first request may take 30-50 seconds to wake up.


## 👩‍💻 Author

**Diksha Sharma**  
Final Year Project — 2026
