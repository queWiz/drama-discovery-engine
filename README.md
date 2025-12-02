# 🎬 Drama Discovery Engine

> A RAG-powered recommendation engine that understands narrative tropes, not just metadata.

[![Demo Video](link_to_gif_or_thumbnail)](link_to_video)

## 🚀 The Problem
Generic search engines (like MyDramaList) rely on static tags. They can't answer "I want a show that feels like *Goblin* but with a happier ending." LLMs (like ChatGPT) hallucinate shows that don't exist.

## 💡 The Solution
I built a **Hybrid Search Engine** that combines:
1.  **Determinism:** SQL filtering for hard constraints (Rating, Year).
2.  **Semantics:** Vector Search (ChromaDB) for narrative vibes.
3.  **Data Enrichment:** An offline AI Agent that analyzes user reviews to tag shows as "Underrated" or "Overrated" and extracts tropes not found in official metadata.

## 🛠️ Tech Stack
*   **AI/LLM:** Google Gemini 2.5 Flash, LangChain, HuggingFace Embeddings
*   **Vector DB:** ChromaDB
*   **Backend:** FastAPI, SQLAlchemy (SQLite), Cloudscraper
*   **Frontend:** Vue 3, Lucide Icons, Glassmorphism UI

## 🏗️ Architecture
[Insert Screenshot of Excalidraw Diagram here]

## ✨ Key Features
*   **Trope Hunter:** Offline agent analyzes thousands of reviews to identify specific tropes (e.g., "Contract Marriage").
*   **Verdict System:** AI acts as a critic to label shows based on the disparity between Rating and Sentiment.
*   **Deep Pagination:** Custom scraper capable of ingesting unlimited datasets from MDL.