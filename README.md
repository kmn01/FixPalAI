# FixPalAI

An intelligent multi-agent AI system that provides home repair diagnosis and step-by-step guidance. FixPalAI acts as a home repair copilot by combining RAG-powered knowledge retrieval, vision analysis, and domain-specialized agents.

## Features

- **Multi-Domain Specialists** — Dedicated agents for plumbing, electrical, carpentry, HVAC, and general repairs
- **RAG-Powered Answers** — Grounds responses in your uploaded repair manuals and documentation
- **Vision Analysis** — Analyzes uploaded photos to identify repair issues
- **Safety Validation** — Built-in checks that flag dangerous operations before they're recommended
- **Text-to-Speech** — Hands-free response playback the user can follow along during repairs
- **Evaluation Logging** — Tracks all interactions in SQLite for quality analysis

## Tech Stack

| Category | Technologies |
|---|---|
| LLM & AI | Google Gemini 2.5-flash, Dedalus Labs, LangChain |
| Embeddings | Google Gemini, Sentence-Transformers (HuggingFace) |
| Vector DB | ChromaDB |
| UI | Streamlit |
| Document Processing | PyMuPDF, TikToken |
| Speech | gTTS (Google Text-to-Speech) |
| Evaluation | SQLite |

## Architecture

```
User Input (Text / Image)
        ↓
Coordinator — classifies domain → routes to specialist
        ↓
Vision Analysis  (if image provided)
        ↓
Specialist Agent + RAG  (retrieves relevant docs from knowledge base)
        ↓
Safety Validation
        ↓
Response → User  (text + TTS)
        ↓
Evaluation Logging  (SQLite)
```

## Project Structure

```
FixPalAI/
├── app/
│   └── main.py               # Streamlit UI
├── src/
│   ├── agents/
│   │   ├── coordinator.py    # Routes queries to domain specialists
│   │   ├── vision_analysis.py
│   │   ├── rag_agent.py      # Retrieval-Augmented Generation
│   │   ├── safety_validation.py
│   │   └── specialists/
│   │       ├── registry.py   # Specialist lookup
│   │       └── router.py
│   ├── services/
│   │   ├── vector_store.py   # Chroma abstraction
│   │   ├── embeddings.py
│   │   ├── llm_utils.py      # LLM integration
│   │   ├── dedalus_wrapper.py
│   │   ├── document_loader.py
│   │   └── chunker.py
│   ├── ingestion/
│   │   └── manuals.py        # CLI for ingesting documents
│   └── evaluation/
│       └── eval_agent.py     # Interaction logging
├── chroma_db/                # Persisted vector database
├── eval.db                   # SQLite evaluation database
├── requirements.txt
└── pyproject.toml
```

## Getting Started

### Prerequisites

- Python 3.10+
- Dedalus API Key
- Google Gemini API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FixPalAI.git
   cd FixPalAI
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in your keys:
   ```env
   GOOGLE_API_KEY=your-gemini-api-key

   # Dedalus vision
   DEDALUS_API_KEY=your-dedalus-key
   USE_DEDALUS=1
   DEDALUS_MODEL=anthropic/claude-opus-4-5

   # Vector DB
   VECTOR_DB=chroma
   CHROMA_PERSIST_DIR=./chroma_db

   # Model settings
   LLM_MODEL=gemini-2.5-flash
   EMBEDDING_MODEL=sentence-transformers
   TEMPERATURE=0.7
   ```

### Run the App

```bash
streamlit run app/main.py
```

Opens at `http://localhost:8501`

### Ingest Repair Manuals 

Place PDF or text manuals in a directory, then run:
```bash
python -m src.ingestion.manuals data/manuals --namespace manuals
```

You can also upload files directly from the sidebar in the UI.

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_API_KEY` | required | Google Gemini API key |
| `DEDALUS_API_KEY` | — | Dedalus Labs API key |
| `USE_DEDALUS` | `0` | Set to `1` to enable Dedalus vision |
| `VECTOR_DB` | `chroma` | Vector store: `chroma` |
| `LLM_MODEL` | `gemini-2.5-flash` | LLM model identifier |
| `EMBEDDING_MODEL` | `sentence-transformers` | Embeddings provider |
| `TEMPERATURE` | `0.7` | LLM response temperature (0–1) |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | Chroma storage path |
