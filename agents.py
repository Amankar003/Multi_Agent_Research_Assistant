"""
agents.py — The Brain of Our Project
=====================================
This file defines 3 agents that work like a relay team:
  1. Researcher Agent  → Searches the internet for info on a topic
  2. Summarizer Agent  → Summarizes the raw search results into bullet points
  3. Report Writer Agent → Writes a polished final report

LLM Providers:
  - Google Gemini (gemini-2.0-flash) → Used for summarization (Agent 2)
  - Groq (llama-3.3-70b-versatile) → Used for report writing (Agent 3)

Both are FREE to use with their respective API keys.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.prompts import ChatPromptTemplate

# ──────────────────────────────────────────────
# Load environment variables from .env file
# This reads your API keys from the .env file
# so we never hardcode secrets in our code
# ──────────────────────────────────────────────
load_dotenv()

# ──────────────────────────────────────────────
# Initialize the LLMs (Large Language Models)
# We use TWO free LLM providers:
#
# 1. Google Gemini (gemini-2.0-flash)
#    - Free tier available at https://aistudio.google.com/apikey
#    - Fast and capable for summarization tasks
#
# 2. Groq (llama-3.3-70b-versatile)
#    - Free tier at https://console.groq.com/keys
#    - Uses Meta's Llama 3.3 70B — one of the most
#      powerful open-source models available
#    - Groq's hardware makes it EXTREMELY fast
#
# temperature=0.3 means the AI will be mostly factual
# (0 = very strict, 1 = very creative)
# ──────────────────────────────────────────────

# Gemini LLM — used for Agent 2 (Summarizer)
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Groq LLM — used for Agent 3 (Report Writer)
# llama-3.3-70b-versatile is the most powerful free model on Groq
groq_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# ──────────────────────────────────────────────
# Initialize the DuckDuckGo search tool
# This is FREE — no API key needed!
# It searches the internet just like you would
# ──────────────────────────────────────────────
search_tool = DuckDuckGoSearchResults()


# ══════════════════════════════════════════════
# AGENT 1: RESEARCHER AGENT
# ══════════════════════════════════════════════
# What it does:
#   Takes a topic (like "quantum computing")
#   Searches the internet using DuckDuckGo
#   Returns the raw search results as text
#
# Think of it like: A student who Googles a topic
# and copies all the search results into a document
#
# NOTE: This agent doesn't use an LLM — it just
# searches the internet. No API key needed!
# ══════════════════════════════════════════════
def researcher_agent(topic):
    """
    Searches the internet for information about the given topic.
    Returns raw search results as a string.
    """
    print(f"🔍 Researcher Agent: Searching for '{topic}'...")

    # Use DuckDuckGo to search for the topic
    # .invoke() runs the search and returns results as text
    search_results = search_tool.invoke(topic)

    print("✅ Researcher Agent: Done searching!")
    return search_results


# ══════════════════════════════════════════════
# AGENT 2: SUMMARIZER AGENT (Powered by Gemini)
# ══════════════════════════════════════════════
# What it does:
#   Takes the messy search results from Agent 1
#   Sends them to Google Gemini with a prompt saying
#   "please summarize this into bullet points"
#   Returns a clean, readable summary
#
# Think of it like: A friend who reads 10 articles
# and gives you just the important highlights
# ══════════════════════════════════════════════
def summarizer_agent(search_results, topic):
    """
    Takes raw search results and summarizes them into
    clean bullet points using Google Gemini.
    """
    print(f"📝 Summarizer Agent (Gemini): Summarizing results for '{topic}'...")

    # This is a "prompt template" — it's like a fill-in-the-blank letter
    # We tell the AI exactly what we want it to do
    # {topic} and {search_results} will be replaced with real values
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful research summarizer. Your job is to take raw search results and create a clear, concise summary."),
        ("human", """
        Topic: {topic}
        
        Here are the raw search results:
        {search_results}
        
        Please summarize the above search results into 5-7 clear bullet points.
        Focus on the most important and relevant information.
        Each bullet point should be 1-2 sentences.
        Start each bullet point with a "•" symbol.
        """)
    ])

    # Create a "chain" — this connects the prompt to the LLM
    # The "|" symbol means "pipe" — send the prompt's output into the LLM
    # Using Gemini for summarization
    chain = prompt | gemini_llm

    # Run the chain with our actual values
    # .invoke() sends the prompt to Gemini and gets back the response
    response = chain.invoke({
        "topic": topic,
        "search_results": search_results
    })

    print("✅ Summarizer Agent (Gemini): Done summarizing!")

    # response.content contains the actual text the AI wrote
    return response.content


# ══════════════════════════════════════════════
# AGENT 3: REPORT WRITER AGENT (Powered by Groq)
# ══════════════════════════════════════════════
# What it does:
#   Takes the summary bullet points from Agent 2
#   Sends them to Groq (Llama 3.3 70B) with a prompt
#   saying "please write a professional report"
#   Returns a formatted report with title, sections,
#   and conclusion
#
# Think of it like: A TA who takes your notes and
# turns them into a polished, submission-ready document
#
# We use Groq here because Llama 3.3 70B is excellent
# at long-form writing and it's blazing fast!
# ══════════════════════════════════════════════
def report_writer_agent(summary, topic):
    """
    Takes the summary and writes a nicely formatted
    final research report using Groq (Llama 3.3 70B).
    """
    print(f"📄 Report Writer Agent (Groq/Llama 3.3): Writing report for '{topic}'...")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional report writer. You write clear, well-structured research reports."),
        ("human", """
        Topic: {topic}
        
        Here is the summarized research:
        {summary}
        
        Please write a well-formatted research report with the following structure:
        
        # Research Report: [Topic Title]
        
        ## Introduction
        (A brief 2-3 sentence introduction to the topic)
        
        ## Key Findings
        (The main findings from the research, organized clearly)
        
        ## Analysis
        (Your analysis and insights based on the findings)
        
        ## Conclusion
        (A brief conclusion summarizing the key takeaways)
        
        ---
        *Report generated by Multi-Agent Research Assistant*
        
        Make it professional but easy to read. Use markdown formatting.
        """)
    ])

    # Using Groq (Llama 3.3 70B) for report writing
    chain = prompt | groq_llm

    response = chain.invoke({
        "topic": topic,
        "summary": summary
    })

    print("✅ Report Writer Agent (Groq/Llama 3.3): Done writing report!")
    return response.content


# ══════════════════════════════════════════════
# THE PIPELINE — Runs All 3 Agents In Sequence
# ══════════════════════════════════════════════
# This is the main function that connects everything.
# It runs the agents one after another like a relay race:
#   Topic → Agent 1 → Agent 2 → Agent 3 → Final Report
#
# Each agent passes its output to the next agent.
#
# Agent 1 (Researcher): DuckDuckGo search (free, no LLM)
# Agent 2 (Summarizer): Google Gemini (free tier)
# Agent 3 (Report Writer): Groq / Llama 3.3 70B (free tier)
# ══════════════════════════════════════════════
def run_research_pipeline(topic):
    """
    Runs the complete research pipeline:
    1. Researcher searches the internet (DuckDuckGo)
    2. Summarizer creates bullet points (Gemini)
    3. Report Writer creates a final report (Groq/Llama 3.3)
    
    Returns a dictionary with results from each step.
    """
    print(f"\n{'='*50}")
    print(f"🚀 Starting Research Pipeline for: '{topic}'")
    print(f"{'='*50}\n")

    # Step 1: Researcher Agent searches the internet
    search_results = researcher_agent(topic)

    # Step 2: Summarizer Agent summarizes the search results (Gemini)
    summary = summarizer_agent(search_results, topic)

    # Step 3: Report Writer Agent creates the final report (Groq)
    report = report_writer_agent(summary, topic)

    print(f"\n{'='*50}")
    print(f"🎉 Pipeline Complete!")
    print(f"{'='*50}\n")

    # Return everything as a dictionary
    # This makes it easy for FastAPI to send as JSON
    return {
        "topic": topic,
        "search_results": str(search_results),
        "summary": summary,
        "report": report
    }
