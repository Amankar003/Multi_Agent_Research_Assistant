"""
agents.py — The Brain of Our Project (v2.0 — Enhanced Edition)
================================================================
This file defines 3 agents that work like a relay team:
  1. Research Agent       → Deep multi-query internet search
  2. Research Analyst     → Comprehensive structured research notes
  3. Report Writer Agent  → Professional long-form research report

All LLM calls use Groq (Llama 3.3 70B) — free tier.
Search uses DuckDuckGo — free, no API key needed.

Architecture:
  Topic → 8 Sub-Queries → Merged Search Data → Research Notes → Final Report
"""

import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.prompts import ChatPromptTemplate

# ──────────────────────────────────────────────
# Load environment variables from .env file
# This reads your API keys from the .env file
# so we never hardcode secrets in our code
# ──────────────────────────────────────────────
load_dotenv()


# ══════════════════════════════════════════════
# LLM CONFIGURATION
# ══════════════════════════════════════════════
# We create TWO separate LLM instances with settings
# tuned for each agent's specific task.
#
# WHY two instances?
#   - Agent 2 (Analyst) needs to be highly factual
#     → lower temperature (0.2), moderate output (4096 tokens)
#   - Agent 3 (Report Writer) needs some writing flair
#     → slightly higher temperature (0.3), large output (8192 tokens)
#
# temperature: Controls randomness/creativity
#   0.0 = very strict, deterministic
#   0.2 = mostly factual with slight variety (good for analysis)
#   0.3 = factual but allows smooth writing style (good for reports)
#   1.0 = very creative, unpredictable
#
# max_tokens: Maximum length of the AI's response
#   4096 tokens ≈ ~3000 words (enough for research notes)
#   8192 tokens ≈ ~6000 words (enough for detailed reports)
# ══════════════════════════════════════════════

# LLM for Agent 2 — Research Analyst
# Lower temperature for maximum factual accuracy
analyst_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    max_tokens=4096,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# LLM for Agent 3 — Report Writer
# Slightly higher temperature for natural, engaging writing
# Higher max_tokens to allow 3000–5000+ word reports
report_writer_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    max_tokens=8192,
    groq_api_key=os.getenv("GROQ_API_KEY")
)


# ──────────────────────────────────────────────
# Initialize the DuckDuckGo search tool
# We configure it to return MORE results per query
# (default is only 4, we want 5 per sub-query)
# ──────────────────────────────────────────────
search_wrapper = DuckDuckGoSearchAPIWrapper(max_results=5)
search_tool = DuckDuckGoSearchResults(api_wrapper=search_wrapper)


# ══════════════════════════════════════════════
# SEARCH QUERY TEMPLATES
# ══════════════════════════════════════════════
# Instead of searching once, we search from 8 different
# angles to get comprehensive coverage of any topic.
#
# Think of it like a journalist who doesn't just Google
# "quantum computing" — they search for its history,
# applications, challenges, latest news, key players, etc.
#
# {topic} gets replaced with the user's actual topic.
# ══════════════════════════════════════════════
SEARCH_ANGLES = [
    "{topic} overview and explanation",
    "{topic} history and background",
    "{topic} applications and use cases",
    "{topic} challenges and limitations",
    "{topic} future trends and predictions",
    "{topic} latest research and developments 2024 2025",
    "{topic} key companies and organizations",
    "{topic} statistics and data",
]


# ══════════════════════════════════════════════
# AGENT 1: RESEARCH AGENT (Deep Multi-Query Search)
# ══════════════════════════════════════════════
# What it does:
#   Takes a topic (like "quantum computing")
#   Generates 8 targeted sub-queries
#   Searches DuckDuckGo for EACH sub-query
#   Merges and deduplicates all results
#   Returns a large, organized block of raw research data
#
# Think of it like: A research assistant who doesn't
# just do one Google search — they systematically search
# from every angle and compile ALL the findings.
#
# This gives Agent 2 approximately 10x more material
# to work with compared to the original single search.
#
# NOTE: This agent doesn't use an LLM — it just
# searches the internet. No API key needed!
# ══════════════════════════════════════════════
def research_agent(topic):
    """
    Performs deep, multi-angle internet research on the given topic.

    Instead of a single search, it runs 8 targeted sub-queries
    covering overview, history, applications, challenges, future,
    latest research, key players, and statistics.

    Returns a large block of organized search results as a string.
    """
    print(f"\n🔍 Research Agent: Starting deep search for '{topic}'...")
    print(f"   Running {len(SEARCH_ANGLES)} targeted sub-queries...\n")

    all_results = []       # Stores all search results
    seen_links = set()     # Tracks URLs we've already seen (for deduplication)

    for i, angle_template in enumerate(SEARCH_ANGLES, 1):
        # Create the actual search query from the template
        query = angle_template.format(topic=topic)
        print(f"   🔎 [{i}/{len(SEARCH_ANGLES)}] Searching: '{query}'")

        try:
            # Run the search — returns results as a string
            results = search_tool.invoke(query)

            # Only add if we got meaningful results
            if results and len(str(results)) > 20:
                # Add with a header so Agent 2 knows which angle this covers
                all_results.append(f"\n--- Search Results for: '{query}' ---\n{results}")

        except Exception as e:
            # If one search fails, skip it and continue with the others
            # This makes the pipeline resilient to individual search failures
            print(f"   ⚠️  Search failed for '{query}': {str(e)[:80]}")
            continue

    # Merge all results into one large text block
    merged_results = "\n\n".join(all_results)

    # Show some stats
    result_count = len(all_results)
    total_chars = len(merged_results)
    print(f"\n✅ Research Agent: Done! Collected results from {result_count}/{len(SEARCH_ANGLES)} searches")
    print(f"   📊 Total research data: {total_chars:,} characters\n")

    return merged_results


# ══════════════════════════════════════════════
# AGENT 2: RESEARCH ANALYST (Comprehensive Notes)
# ══════════════════════════════════════════════
# What it does:
#   Takes the large block of search results from Agent 1
#   Sends them to Groq with a detailed analytical prompt
#   Returns comprehensive, structured research notes
#   (~1500–2500 words instead of the old 5–7 bullets)
#
# Think of it like: A research analyst who reads through
# piles of articles and creates detailed, organized notes
# covering every important aspect of the topic.
#
# KEY DIFFERENCE from v1.0:
#   Old: "Summarize into 5-7 bullet points" → lost 90% of info
#   New: "Create comprehensive research notes" → preserves details
# ══════════════════════════════════════════════
def research_analyst_agent(search_results, topic):
    """
    Analyzes raw search results and creates comprehensive,
    structured research notes (~1500-2500 words).

    Unlike a simple summarizer, this agent preserves details,
    statistics, names, and dates from the source material.
    """
    print(f"📝 Research Analyst (Groq): Analyzing results for '{topic}'...")

    # ── SYSTEM PROMPT ──
    # Tells the AI WHO it is and HOW to behave
    # Uses advanced prompt engineering techniques:
    #   - Role assignment ("You are a senior research analyst")
    #   - Anti-hallucination guard ("Only use provided information")
    #   - Explicit constraints ("Do NOT aggressively compress")
    system_prompt = """You are a senior research analyst with expertise in creating \
comprehensive, well-structured research notes from raw search data.

CRITICAL RULES:
1. ONLY use information that is directly present in the provided search results.
2. Do NOT invent, fabricate, or hallucinate any facts, statistics, or claims.
3. Do NOT aggressively compress or oversimplify the information.
4. PRESERVE all specific statistics, numbers, dates, names, and factual details.
5. If the search results lack information for a particular section, write \
"Insufficient data available from search results" for that section.
6. Write in clear, professional English.
7. Use markdown formatting throughout."""

    # ── HUMAN PROMPT ──
    # Tells the AI WHAT to do with the specific input
    # Explicitly lists every section we want in the output
    # This prevents the AI from being lazy or skipping sections
    human_prompt = """Topic: {topic}

Below are the raw search results gathered from multiple search queries covering \
different angles of this topic. Analyze ALL the data thoroughly.

--- RAW SEARCH RESULTS START ---
{search_results}
--- RAW SEARCH RESULTS END ---

Create COMPREHENSIVE research notes covering ALL of the following sections. \
Write 1500–2500 words total. Each section should have multiple sentences with \
specific details from the search results.

## Definitions & Overview
Define the topic clearly. What is it? Why does it matter?

## Historical Background
When did it originate? Key milestones and evolution over time.

## Core Concepts & Technical Explanation
Explain the fundamental concepts. How does it work technically?

## Current State & Latest Developments
What is happening right now? Recent breakthroughs, news, research.

## Industry Applications & Use Cases
Where is it being used? Which industries? Specific examples.

## Key Companies & Organizations
Who are the major players? Startups, corporations, research institutions.

## Statistics & Market Data
Numbers, market size, growth rates, adoption statistics.

## Advantages & Benefits
What are the positive aspects? Why is it valuable?

## Disadvantages, Risks & Challenges
What are the problems? Ethical concerns? Technical barriers?

## Future Scope & Emerging Trends
Where is this heading? Predictions and emerging directions.

## Notable Real-World Examples & Case Studies
Specific examples of real-world implementation or impact.

## Interesting Facts
Any surprising or noteworthy facts from the research.

IMPORTANT: Write substantive content for each section. Do NOT use single-line \
bullet points. Write in detailed paragraphs with specific facts from the search \
results. Aim for 1500–2500 words total."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

    # Create the chain: prompt → LLM
    chain = prompt | analyst_llm

    # Run the chain
    response = chain.invoke({
        "topic": topic,
        "search_results": search_results
    })

    # Show output stats
    word_count = len(response.content.split())
    print(f"✅ Research Analyst (Groq): Done! Generated ~{word_count:,} words of research notes\n")

    return response.content


# ══════════════════════════════════════════════
# AGENT 3: REPORT WRITER AGENT (Professional Report)
# ══════════════════════════════════════════════
# What it does:
#   Takes the comprehensive research notes from Agent 2
#   Sends them to Groq with a professional report-writing prompt
#   Returns a polished, publication-ready research report
#   (~3000–5000+ words with 15+ sections)
#
# Think of it like: A professional writer who takes
# detailed research notes and transforms them into a
# polished, well-structured report ready for publication.
#
# KEY DIFFERENCE from v1.0:
#   Old: 4 sections, ~500 words
#   New: 15+ sections, 3000–5000+ words, tables, citations
# ══════════════════════════════════════════════
def report_writer_agent(research_notes, topic):
    """
    Transforms comprehensive research notes into a professional,
    long-form research report (~3000-5000+ words).

    Produces a publication-ready document with executive summary,
    table of contents, detailed sections, comparison tables,
    and proper conclusions.
    """
    print(f"📄 Report Writer (Groq/Llama 3.3): Writing professional report for '{topic}'...")

    # ── SYSTEM PROMPT ──
    # Establishes the AI's role as a professional report writer
    # with specific quality standards and anti-hallucination rules
    system_prompt = """You are a world-class professional research report writer. \
You produce comprehensive, well-researched reports that rival those from top \
consulting firms and academic institutions.

WRITING STANDARDS:
1. Write in a formal yet accessible tone — professional but easy to understand.
2. Every claim must be supported by information from the research notes provided.
3. Do NOT fabricate statistics, quotes, or facts not present in the research notes.
4. Each section must contain MULTIPLE detailed paragraphs (minimum 3-4 sentences per paragraph).
5. Use markdown formatting: headers, bold, italic, tables, and bullet points where appropriate.
6. Avoid repetition — each section should contribute unique information.
7. Include smooth transitions between sections.
8. Write a MINIMUM of 3000 words. Aim for 4000–5000 words when sufficient information exists.
9. If the research notes lack information for a section, briefly acknowledge this \
rather than inventing content."""

    # ── HUMAN PROMPT ──
    # Detailed blueprint for the exact report structure
    # Each section includes guidance on what to write
    human_prompt = """Topic: {topic}

Below are the comprehensive research notes compiled by our research analyst. \
Use ALL of this information to write a professional research report.

--- RESEARCH NOTES START ---
{research_notes}
--- RESEARCH NOTES END ---

Write a COMPLETE professional research report following this EXACT structure. \
Every section must contain detailed, substantive content — not just a sentence or two.

# Research Report: {topic}

## Executive Summary
Write a compelling 200-300 word overview that captures the essence of the entire \
report. Cover what the topic is, why it matters, key findings, and main conclusions. \
A busy executive should be able to read just this section and understand the full picture.

## Table of Contents
List all sections of the report as a numbered list.

## 1. Introduction
Introduce the topic thoroughly. Explain what it is, why it is important in today's \
world, what problems it solves or addresses, and what this report covers. \
Write at least 2-3 paragraphs.

## 2. Background & History
Cover the historical origins and evolution. When did this start? What were the key \
milestones? How has it evolved over the decades? Write a detailed chronological narrative.

## 3. Core Concepts & How It Works
Explain the fundamental concepts and mechanisms. Break down the technical aspects \
in a way that is thorough yet accessible. Use analogies where helpful.

## 4. Technical Deep Dive
Go deeper into the technical architecture, methodologies, or scientific principles. \
Explain how things work under the hood. Include technical details from the research.

## 5. Current Industry Landscape
Describe the current state of the field. Who are the major players? What are the \
dominant approaches? What does the competitive landscape look like? \
Include a markdown table of key companies/organizations if data is available.

## 6. Market Analysis & Statistics
Present available data on market size, growth rates, adoption statistics, investment \
figures, and other quantitative data. Use a markdown table to present key statistics \
if available.

## 7. Industry Applications & Use Cases
Detail the practical applications across different industries. Provide specific \
examples of how the technology/concept is being applied in the real world.

## 8. Case Studies & Real-World Examples
Highlight 2-3 notable real-world implementations or examples. Describe what was \
done, what the results were, and what lessons were learned.

## 9. Advantages & Benefits
Present a thorough analysis of the positive aspects. Organize by category if applicable. \
Explain WHY each advantage matters, not just what it is.

## 10. Disadvantages, Risks & Challenges
Present a balanced analysis of the challenges, risks, ethical concerns, technical \
barriers, and limitations. Be specific and detailed.

## 11. Comparative Analysis
Create a markdown comparison table where relevant — for example, comparing different \
approaches, technologies, or solutions within the topic. Format as a proper table.

## 12. Future Scope & Emerging Trends
Discuss where this field is heading. What are the emerging trends? What predictions \
do experts make? What developments are on the horizon?

## 13. Key Takeaways
List 8-10 critical takeaways that a reader should remember from this report. \
Each takeaway should be a substantive sentence, not just a few words.

## 14. Conclusion
Write a thorough conclusion that synthesizes the main findings, restates the \
significance of the topic, and provides a forward-looking perspective. \
Write at least 2-3 paragraphs.

## 15. References & Sources
List the sources referenced in the research notes. If specific URLs or source \
names were mentioned in the research data, include them here.

---
*Report generated by Multi-Agent Research Assistant | Powered by Groq (Llama 3.3 70B)*

CRITICAL REMINDERS:
- Write a MINIMUM of 3000 words. Aim for 4000-5000 words.
- Every section must have multiple detailed paragraphs.
- Do NOT skip any section.
- Do NOT write shallow, one-line sections.
- Use markdown tables in sections 5, 6, and 11.
- Maintain professional quality throughout."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

    # Create the chain: prompt → LLM
    chain = prompt | report_writer_llm

    # Run the chain
    response = chain.invoke({
        "topic": topic,
        "research_notes": research_notes
    })

    # Show output stats
    word_count = len(response.content.split())
    print(f"✅ Report Writer (Groq/Llama 3.3): Done! Generated ~{word_count:,} words\n")

    return response.content


# ══════════════════════════════════════════════
# THE PIPELINE — Runs All 3 Agents In Sequence
# ══════════════════════════════════════════════
# This is the main function that connects everything.
# It runs the agents one after another like a relay race:
#
#   Topic → Agent 1 (8 searches) → Agent 2 (analysis) → Agent 3 (report) → Done
#
# Each agent passes its output to the next agent.
#
# Agent 1 (Research Agent):    DuckDuckGo multi-query search (free, no LLM)
# Agent 2 (Research Analyst):  Groq / Llama 3.3 70B (free tier)
# Agent 3 (Report Writer):    Groq / Llama 3.3 70B (free tier)
#
# NOTE: There is a 5-second delay between Agent 2 and Agent 3.
# This prevents hitting Groq's free-tier rate limit
# (30 requests per minute / 12,000 tokens per minute).
# ══════════════════════════════════════════════
def run_research_pipeline(topic):
    """
    Runs the complete enhanced research pipeline:
    1. Research Agent performs deep multi-query search (DuckDuckGo)
    2. Research Analyst creates comprehensive notes (Groq/Llama 3.3)
    3. Report Writer creates a professional report (Groq/Llama 3.3)

    Returns a dictionary with results from each step.
    """
    print(f"\n{'='*60}")
    print(f"🚀 Starting Enhanced Research Pipeline for: '{topic}'")
    print(f"{'='*60}\n")

    # ── Step 1: Deep Multi-Query Research ──
    # Runs 8 sub-queries across different angles of the topic
    search_results = research_agent(topic)

    # ── Step 2: Research Analysis ──
    # Creates comprehensive structured notes from the raw search data
    research_notes = research_analyst_agent(search_results, topic)

    # ── Rate Limit Protection ──
    # Wait 5 seconds before the next LLM call to avoid
    # hitting Groq's free-tier rate limits (12K TPM / 30 RPM)
    print("⏳ Waiting 5 seconds to respect API rate limits...\n")
    time.sleep(5)

    # ── Step 3: Professional Report Writing ──
    # Transforms research notes into a polished, long-form report
    report = report_writer_agent(research_notes, topic)

    print(f"{'='*60}")
    print(f"🎉 Pipeline Complete! Professional report generated.")
    print(f"{'='*60}\n")

    # Return everything as a dictionary
    # FastAPI will automatically convert this to JSON
    return {
        "topic": topic,
        "search_results": str(search_results),
        "summary": research_notes,     # "summary" key kept for API compatibility
        "report": report
    }
