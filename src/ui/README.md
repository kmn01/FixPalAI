# FixPalAI UI

## `fixpalai.jsx`

React reference UI for FixPalAI. This is a **standalone prototype** and is not wired to the FixPalAI backend.

- **Stack**: React, Lucide React icons, Tailwind-style utility classes (requires Tailwind CSS in your React project).
- **Use case**: Design reference or base for a future React/Next.js front end that would call a FixPalAI API (e.g. FastAPI or Streamlit backend).
- **Running it**: Add this component to a React app that has Tailwind and `lucide-react` installed. This repo does not include a React build; the main app is Streamlit.

## Main app (Streamlit)

The integrated UI lives in the Streamlit app:

- **Default**: `streamlit run app/main.py`
- **Improved UI** (same backend, different layout): `streamlit run app/fixpal_ui_improved.py`

Both use the same backend: coordinator, RAG, vector store, ingestion, and TTS.
