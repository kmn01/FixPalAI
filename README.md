# FixPalAI

An intelligent multi-agent AI system that provides home repair diagnosis and guidance. FixPalAI acts as a technician copilot by combining RAG-powered knowledge retrieval, vision analysis, and domain-specialized agents.

## Features

- **Multi-Domain Specialists**: Dedicated agents for plumbing, electrical, carpentry, HVAC, and general repairs
- **RAG-Powered Answers**: Grounds responses in uploaded repair manuals and documentation
- **Vision Analysis**: Analyzes uploaded images to identify repair issues using Gemini via Dedalus
- **Safety Validation**: Built-in checks for dangerous operations 
- **Text-to-Speech**: Hands-free response playback during repairs
- **Evaluation Logging**: Tracks all interactions in SQLite for quality analysis

## Tech Stack

| Category | Technologies |
|----------|-------------|
| LLM & AI | Google Gemini 2.5-flash, Dedalus Labs, LangChain, LangGraph |
| Embeddings | Google Gemini, Sentence-Transformers (HuggingFace) |
| Vector DB | Chroma |
| UI | Streamlit, React, Tailwind|
| Document Processing | PyMuPDF, TikToken |
| Speech | gTTS (Google Text-to-Speech) |
| Database | SQLite |

## Getting Started

### Prerequisites

- Python 3.10+
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
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables by copying `.env` and filling in your keys:
   ```bash
   GOOGLE_API_KEY=your-gemini-api-key

   # Optional
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

### Running the App

```bash
streamlit run app/fixpal_ui_improved.py
```

Opens at `http://localhost:8501`

### Ingesting Repair Manuals (Optional)

Place PDF or text manuals in a directory and run:
```bash
python -m src.ingestion.manuals data/manuals --namespace manuals
```

## Project Structure

```
FixPalAI/
├── app/
│   ├── main.py                   # Basic Streamlit UI
│   └── fixpal_ui_improved.py     # Enhanced Streamlit UI
├── src/
│   ├── agents/
│   │   ├── coordinator.py        # Routes queries to domain specialists
│   │   ├── vision_analysis.py    # Image analysis
│   │   ├── rag_agent.py          # Retrieval-Augmented Generation
│   │   ├── safety_validation.py  # Safety checks
│   │   └── specialists/          # Domain-specific agents
│   ├── services/
│   │   ├── vector_store.py       # Chroma/Pinecone abstraction
│   │   ├── embeddings.py         # Embedding providers
│   │   ├── llm_utils.py          # LLM integration
│   │   ├── document_loader.py    # PDF & text parsing
│   │   └── chunker.py            # Semantic chunking
│   ├── ingestion/
│   │   └── manuals.py            # CLI for ingesting documents
│   └── evaluation/
│       └── eval_agent.py         # Interaction logging
├── chroma_db/                    # Vector database (persisted)
├── eval.db                       # SQLite evaluation database
├── requirements.txt
└── pyproject.toml
```

## Architecture

```
User Input (Text/Image)
        ↓
Coordinator → classifies domain → routes to specialist
        ↓
Vision Analysis (if image provided)
        ↓
Specialist Agent + RAG (retrieves relevant docs)
        ↓
Safety Validation
        ↓
Response → User (text + optional TTS)
        ↓
Evaluation Logging (SQLite)
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | required | Google Gemini API key |
| `VECTOR_DB` | chroma | Vector store: `chroma` or `pinecone` |
| `LLM_MODEL` | gemini-2.5-flash | LLM model identifier |
| `EMBEDDING_MODEL` | sentence-transformers | Embeddings provider |
| `TEMPERATURE` | 0.7 | LLM response temperature (0-1) |
| `CHROMA_PERSIST_DIR` | ./chroma_db | Chroma storage path |
