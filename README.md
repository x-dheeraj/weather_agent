# 🌦️ Weather Agent

A simple agentic AI weather assistant built with **Python, Ollama, and Qwen3 0.6B**.

The project demonstrates how an LLM can follow a structured reasoning loop, decide when a tool is required, execute a weather API call, observe the result, and generate a final response.


## 📋 Requirements

Make sure you have:

- **Python 3**
- **Ollama**
- **Qwen3 0.6B model** (`qwen3:0.6b`)
- **Internet connection** for the weather API

## 🧠 Architecture

```text
User
 │
 ▼
Python Agent
 │
 ▼
Ollama
 │
 ▼
Qwen3 0.6B
 │
 ├── PLAN
 │
 ├── TOOL → get_weather()
 │              │
 │              ▼
 │          wttr.in API
 │              │
 │              ▼
 │          Weather Result
 │
 └── OUTPUT
       │
       ▼
     User
