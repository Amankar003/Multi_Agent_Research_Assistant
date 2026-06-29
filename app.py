"""
app.py — The Streamlit Frontend (User Interface)
=================================================
This file creates a beautiful web page where:
  - The user types a research topic
  - Clicks a button
  - Sees the results from all 3 agents

Streamlit is a Python library that turns simple Python scripts
into interactive web apps. No HTML/CSS/JS needed!

We run this with: streamlit run app.py
"""

import streamlit as st
import requests
import time

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
# This MUST be the first Streamlit command in the file.
# It sets the browser tab title, icon, and page layout.
# "wide" layout uses the full width of the screen.
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide"
)

# ──────────────────────────────────────────────
# Custom CSS for better styling
# ──────────────────────────────────────────────
# Streamlit lets us inject custom CSS using st.markdown
# This makes the app look more polished and professional
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        text-align: center;
        background: linear-gradient(120deg, #6C63FF, #3B82F6, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #94A3B8;
        font-size: 1.1rem;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    
    /* Agent status cards */
    .agent-card {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    .agent-card:hover {
        transform: translateY(-2px);
    }
    
    /* Pipeline flow visualization */
    .pipeline-flow {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-radius: 12px;
        margin-bottom: 2rem;
        font-size: 1rem;
        color: #CBD5E1;
    }
    
    /* Result section headers */
    .section-header {
        background: linear-gradient(90deg, #6C63FF, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.4rem;
        font-weight: 700;
        margin-top: 1.5rem;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #64748B;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid #334155;
    }
    
    /* Hide Streamlit default elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Style the input box */
    .stTextInput > div > div > input {
        background-color: #1E293B;
        color: #E2E8F0;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 0.75rem;
    }
    
    /* Style the button */
    .stButton > button {
        background: linear-gradient(90deg, #6C63FF, #3B82F6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #5B52E0, #2563EB);
        box-shadow: 0 4px 15px rgba(108, 99, 255, 0.4);
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# FastAPI backend URL
# ──────────────────────────────────────────────
# Our FastAPI server runs on localhost:8000
# Streamlit will send HTTP requests to this URL
# ──────────────────────────────────────────────
FASTAPI_URL = "http://localhost:8000"

# ──────────────────────────────────────────────
# App Header
# ──────────────────────────────────────────────
st.markdown('<h1 class="main-title">🔬 Multi-Agent Research Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Powered by 3 AI Agents — Search, Summarize, and Report</p>', unsafe_allow_html=True)

# Show the pipeline flow
st.markdown("""
<div class="pipeline-flow">
    📥 <strong>Your Topic</strong> &nbsp;→&nbsp; 
    🔍 <strong>Agent 1: Researcher</strong> &nbsp;→&nbsp; 
    📝 <strong>Agent 2: Summarizer</strong> &nbsp;→&nbsp; 
    📄 <strong>Agent 3: Report Writer</strong> &nbsp;→&nbsp; 
    📊 <strong>Final Report</strong>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Input Section
# ──────────────────────────────────────────────
# Create two columns: one for the text input, one for the button
# st.columns() splits the page into columns
# ──────────────────────────────────────────────
col1, col2 = st.columns([4, 1])

with col1:
    # st.text_input creates a text box
    # The value the user types is stored in "topic"
    topic = st.text_input(
        "Enter your research topic",
        placeholder="e.g., Quantum Computing, Climate Change, CRISPR Gene Editing...",
        label_visibility="collapsed"  # Hide the label, we have our own header
    )

with col2:
    # st.button creates a clickable button
    # It returns True when clicked, False otherwise
    research_button = st.button("🚀 Research", use_container_width=True)

# ──────────────────────────────────────────────
# What happens when the user clicks the button
# ──────────────────────────────────────────────
if research_button:
    # Check if the user actually typed something
    if not topic.strip():
        st.warning("⚠️ Please enter a research topic first!")
    else:
        # ── Show a spinner while the agents are working ──
        # st.spinner shows a loading animation with a message
        # Everything inside the "with" block runs while the spinner shows
        with st.spinner("🤖 Agents are performing deep research... This may take 60-90 seconds (8 search queries + 2 AI analyses)."):
            try:
                # ── Send the topic to our FastAPI backend ──
                # requests.post() sends a POST request
                # json={"topic": topic} sends the topic as JSON data
                # timeout=300 means wait up to 5 minutes for a response
                # (the enhanced pipeline runs 8 searches + 2 LLM calls)
                response = requests.post(
                    f"{FASTAPI_URL}/research",
                    json={"topic": topic},
                    timeout=300
                )

                # ── Check if the request was successful ──
                # raise_for_status() throws an error if something went wrong
                # (like if the server returned a 500 error)
                response.raise_for_status()

                # ── Parse the JSON response ──
                # .json() converts the response from JSON to a Python dictionary
                data = response.json()

                # ── SUCCESS! Show the results ──
                st.success("✅ Research complete! Here are your results:")

                # ── Display results in tabs ──
                # st.tabs creates clickable tabs (like browser tabs)
                # Each tab shows a different part of the results
                tab1, tab2, tab3 = st.tabs([
                    "📄 Final Report",
                    "📝 Research Notes",
                    "🔍 Raw Search Results"
                ])

                # Tab 1: The Final Report (most important — shown first)
                with tab1:
                    st.markdown(f'<p class="section-header">Research Report: {topic}</p>', unsafe_allow_html=True)
                    st.markdown(data["report"])

                # Tab 2: The comprehensive research notes from the Analyst agent
                with tab2:
                    st.markdown(f'<p class="section-header">Research Notes: {topic}</p>', unsafe_allow_html=True)
                    st.markdown(data["summary"])

                # Tab 3: Raw search results (for the curious)
                with tab3:
                    st.markdown(f'<p class="section-header">Raw Search Results: {topic}</p>', unsafe_allow_html=True)
                    # st.code shows text in a code block with monospace font
                    # This is good for raw data since it preserves formatting
                    st.code(data["search_results"], language=None)

            except requests.exceptions.ConnectionError:
                # This error means FastAPI is not running
                st.error(
                    "❌ **Cannot connect to the backend server!**\n\n"
                    "Make sure the FastAPI server is running:\n"
                    "```\nuvicorn main:app --reload\n```"
                )
            except requests.exceptions.Timeout:
                # This error means the request took too long
                st.error("⏱️ **Request timed out.** The research is taking too long. Try a simpler topic.")
            except Exception as e:
                # Catch any other unexpected errors
                st.error(f"❌ **Something went wrong:** {str(e)}")

# ──────────────────────────────────────────────
# Sidebar — About Section
# ──────────────────────────────────────────────
# st.sidebar creates content in the left sidebar
# Good for additional info that doesn't clutter the main page
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 How It Works")
    st.markdown("""
    This app uses **3 AI agents** that work together like a relay team:
    
    **1. 🔍 Research Agent**
    - Runs **8 targeted sub-queries** via DuckDuckGo
    - Covers overview, history, applications, challenges, future, stats, and more
    - Returns comprehensive raw research data
    
    **2. 📝 Research Analyst**
    - Analyzes all the raw search data
    - Uses Groq (Llama 3.3 70B) to create **detailed research notes**
    - Produces ~1500-2500 words of structured analysis
    
    **3. 📄 Report Writer**
    - Transforms research notes into a **professional report**
    - Uses Groq (Llama 3.3 70B) to generate **3000-5000+ words**
    - Includes executive summary, tables, case studies, and more
    """)

    st.markdown("---")
    st.markdown("## 🛠️ Tech Stack")
    st.markdown("""
    - 🐍 **Python** — Core language
    - 🦜 **LangChain** — Agent framework
    - ⚡ **FastAPI** — Backend API
    - 🎨 **Streamlit** — Frontend UI
    - 🦙 **Groq (Llama 3.3 70B)** — AI analysis & report writing
    - 🔍 **DuckDuckGo** — Free multi-query search
    """)

    st.markdown("---")
    st.markdown(
        '<div class="footer">Built by <a href="https://github.com/Amankar003" target="_blank">Amankar003</a> 🚀</div>',
        unsafe_allow_html=True
    )
