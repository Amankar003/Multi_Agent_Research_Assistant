# 🔬 Multi-Agent Research Assistant

> **An AI-powered research assistant that uses 3 intelligent agents to search, summarize, and write professional research reports on any topic.**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)

---

## 📌 How It Works

The user enters a research topic, and **3 AI agents** process it in a pipeline — each agent takes the output of the previous one:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RESEARCH PIPELINE                                │
│                                                                         │
│   📥 User Topic                                                         │
│       │                                                                 │
│       ▼                                                                 │
│   ┌─────────────────────┐                                               │
│   │  🔍 Agent 1:        │  Searches the internet using DuckDuckGo       │
│   │  RESEARCHER         │  Returns raw search results                   │
│   └────────┬────────────┘                                               │
│            │                                                            │
│            ▼                                                            │
│   ┌─────────────────────┐                                               │
│   │  📝 Agent 2:        │  Summarizes results into bullet points        │
│   │  SUMMARIZER         │  using Google Gemini                          │
│   └────────┬────────────┘                                               │
│            │                                                            │
│            ▼                                                            │
│   ┌─────────────────────┐                                               │
│   │  📄 Agent 3:        │  Writes a professional research report        │
│   │  REPORT WRITER      │  with sections, analysis, and conclusion      │
│   └────────┬────────────┘                                               │
│            │                                                            │
│            ▼                                                            │
│   📊 Final Report                                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.9+** | Core programming language |
| **LangChain** | Framework for building AI agents |
| **FastAPI** | Backend REST API |
| **Streamlit** | Frontend web interface |
| **Google Gemini** | LLM for summarization (free tier) |
| **Groq (Llama 3.3 70B)** | LLM for report writing (free, open-source) |
| **DuckDuckGo Search** | Free internet search (no API key needed) |

---

## 📂 Project Structure

```
multi-agent-research-assistant/
├── agents.py          ← All 3 agent definitions + pipeline function
├── main.py            ← FastAPI backend with /research endpoint
├── app.py             ← Streamlit frontend UI
├── requirements.txt   ← Python dependencies
├── .env.example       ← Environment variable template
└── README.md          ← You are here!
```

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.9 or higher installed
- A Google Gemini API key ([get one here — free](https://aistudio.google.com/apikey))
- A Groq API key ([get one here — free](https://console.groq.com/keys))

### Step 1: Clone the Repository

```bash
git clone https://github.com/Amankar003/multi-agent-research-assistant.git
cd multi-agent-research-assistant
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Open .env and add your API keys
# Both are FREE to get!
```

Your `.env` file should look like this:
```
GOOGLE_API_KEY=your_google_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### Step 4: Start the FastAPI Backend

```bash
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 5: Start the Streamlit Frontend (Open a NEW terminal)

```bash
streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Step 6: Use the App!

1. Open http://localhost:8501 in your browser
2. Type a research topic (e.g., "Quantum Computing")
3. Click the **🚀 Research** button
4. Wait 30-60 seconds for the agents to work
5. View the **Final Report**, **Summary**, and **Raw Results** in separate tabs

---

## 📸 Sample Input & Output

### Input
```
Topic: "Quantum Computing"
```

### Output (Final Report)

```markdown
# Research Report: Quantum Computing

## Introduction
Quantum computing is a rapidly evolving field that leverages the principles
of quantum mechanics to process information in fundamentally new ways...

## Key Findings
• Quantum computers use qubits instead of classical bits
• Major players include IBM, Google, and Microsoft
• Google achieved "quantum supremacy" in 2019
• Current quantum computers are in the NISQ era
• Applications include cryptography, drug discovery, and optimization

## Analysis
The field of quantum computing has made significant strides in recent years...

## Conclusion
Quantum computing represents a paradigm shift in computational capability...

---
*Report generated by Multi-Agent Research Assistant*
```

---

## 🏗️ Architecture

```
┌──────────────┐     HTTP POST     ┌──────────────┐     Pipeline     ┌──────────────┐
│   Streamlit  │ ───────────────▶  │   FastAPI    │ ──────────────▶  │   agents.py  │
│   Frontend   │                   │   Backend    │                   │  (3 Agents)  │
│  (port 8501) │ ◀─────────────── │  (port 8000) │ ◀────────────── │              │
└──────────────┘     JSON Response └──────────────┘     Results      └──────────────┘
```

---

## 🔑 API Reference

### `POST /research`

**Request Body:**
```json
{
    "topic": "Quantum Computing"
}
```

**Response:**
```json
{
    "topic": "Quantum Computing",
    "search_results": "Raw search results...",
    "summary": "• Bullet point 1\n• Bullet point 2...",
    "report": "# Research Report: Quantum Computing\n\n## Introduction..."
}
```

### `GET /health`

Returns server health status.

---

## 👤 Author

Built with ❤️ by [**Amankar003**](https://github.com/Amankar003)

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).
#   M u l t i _ A g e n t _ R e s e a r c h _ A s s i s t a n t  
 