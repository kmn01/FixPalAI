"""FixPalAI Streamlit app - document ingestion, RAG, vision, safety validation."""

import sys
from pathlib import Path
import tempfile
import uuid

# Ensure project root is on path when running via streamlit run
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import base64
import io

import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

from src.services.chunker import chunk_documents
from src.services.document_loader import DocumentChunk, load_document
from src.services.vector_store import add_chunks_to_store, get_vector_store
from src.agents.coordinator import coordinator_invoke
from src.agents.vision_analysis import analyze_image
from src.evaluation.eval_agent import log_interaction

st.set_page_config(page_title="FixPalAI", page_icon="🔧", layout="wide")

st.title("🔧 FixPalAI")
st.caption("Home repair diagnosis via RAG — ingest documents and images in the sidebar, then ask questions.")


def text_to_speech(text: str, max_chars: int = 4000) -> bytes | None:
    """Generate MP3 audio from text using gTTS. Returns None on failure."""
    if not (text or text.strip()):
        return None
    clean = text.strip()
    if len(clean) > max_chars:
        clean = clean[: max_chars - 3] + "..."
    try:
        tts = gTTS(text=clean, lang="en")
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return None


def ensure_vector_store():
    """Get or init session vector store."""
    if "vector_store" not in st.session_state:
        try:
            vs, _ = get_vector_store(namespace="manuals")
            st.session_state.vector_store = vs
        except Exception as e:
            st.session_state.vector_store = None
            st.session_state.vector_store_error = str(e)
    return st.session_state.get("vector_store")


# ---- Sidebar: Ingest ----
with st.sidebar:
    st.header("Document Ingestion")
    st.markdown("Upload PDF, text, or image files. Documents are chunked and indexed; images are described and indexed by type.")

    uploaded = st.file_uploader(
        "Upload files",
        type=["pdf", "txt", "jpg", "jpeg", "png", "gif", "webp"],
        accept_multiple_files=True,
    )

    if st.button("Ingest uploaded files") and uploaded:
        vs = ensure_vector_store()
        if vs is None:
            st.error("Could not connect to vector store. Check API key and setup.")
        else:
            with st.spinner("Processing and indexing..."):
                all_chunks: list[DocumentChunk] = []
                for f in uploaded:
                    ext = Path(f.name).suffix.lower()
                    data = f.read()

                    tmp_dir = Path(tempfile.gettempdir())
                    safe_name = f"{uuid.uuid4().hex}_{f.name}"
                    path = tmp_dir / safe_name
                    path.write_bytes(data)
                    if ext == ".pdf":
                        docs = list(load_document(path, source_type="user"))
                    elif ext in (".txt", ".text"):
                        docs = list(load_document(path, source_type="user"))
                    elif ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
                        try:
                            desc = analyze_image(data, user_query="Describe this image for home repair context. Extract any visible text, labels, or repair-relevant details.")
                            if desc:
                                docs = [DocumentChunk(content=desc, source=f.name, source_type="user")]
                            else:
                                docs = []
                        except Exception:
                            docs = []
                    else:
                        docs = []
                    all_chunks.extend(chunk_documents(docs))
                if all_chunks:
                    add_chunks_to_store(vs, all_chunks)
                    st.success(f"Indexed {len(all_chunks)} chunks from {len(uploaded)} file(s).")
                else:
                    st.warning("No content extracted from files.")

# ---- Main: Chat ----
# Vector store is created on first use (ingest or first message) to keep startup fast.
if "messages" not in st.session_state:
    st.session_state.messages = []

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("image"):
            st.image(msg["image"], use_container_width=True)
        if msg["role"] == "assistant" and msg.get("domain") and msg["domain"] != "error":
            st.caption(f"Routed to: **{msg['domain'].title()}** specialist")
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("content"):
            col1, _ = st.columns([1, 4])
            with col1:
                if st.button("🔊 Read aloud", key=f"tts_{i}"):
                    audio_bytes = text_to_speech(msg["content"])
                    if audio_bytes is not None:
                        st.session_state[f"tts_audio_{i}"] = audio_bytes
                    else:
                        st.session_state[f"tts_error_{i}"] = True
            if f"tts_audio_{i}" in st.session_state:
                b64 = base64.b64encode(st.session_state[f"tts_audio_{i}"]).decode("utf-8")
                st.markdown(
                    f'<audio src="data:audio/mp3;base64,{b64}" autoplay controls playsinline></audio>',
                    unsafe_allow_html=True,
                )
            elif st.session_state.get(f"tts_error_{i}"):
                st.caption("Could not generate audio for this message.")

prompt = st.chat_input("Enter your question or describe the problem you're facing...")

if prompt:
    vs = ensure_vector_store()
    if vs is None:
        err = st.session_state.get("vector_store_error", "Could not connect to vector store.")
        st.error(err)
        st.info("Set OPENAI_API_KEY in .env. For Chroma, ensure chromadb is installed.")
        st.session_state.messages.append({"role": "user", "content": prompt, "image": None})
        st.session_state.messages.append({"role": "assistant", "content": f"Error: {err}", "domain": "error"})
    else:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "image": None,
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Routing and thinking..."):
                try:
                    answer, domain = coordinator_invoke(
                        prompt, vector_store=vs, image_context=None
                    )
                    st.caption(f"Routed to: **{domain.title()}** specialist")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer, "domain": domain})
                    idx = len(st.session_state.messages) - 1
                    if st.button("🔊 Read aloud", key=f"tts_{idx}"):
                        audio_bytes = text_to_speech(answer)
                        if audio_bytes is not None:
                            st.session_state[f"tts_audio_{idx}"] = audio_bytes
                        else:
                            st.session_state[f"tts_error_{idx}"] = True
                    if f"tts_audio_{idx}" in st.session_state:
                        b64 = base64.b64encode(st.session_state[f"tts_audio_{idx}"]).decode("utf-8")
                        st.markdown(
                            f'<audio src="data:audio/mp3;base64,{b64}" autoplay controls playsinline></audio>',
                            unsafe_allow_html=True,
                        )
                    elif st.session_state.get(f"tts_error_{idx}"):
                        st.caption("Could not generate audio for this message.")
                    log_interaction(
                        prompt=prompt,
                        response=answer,
                        domain=domain,
                        image_provided=False,
                    )
                except Exception as e:
                    err = str(e)
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {err}", "domain": "error"})
                    log_interaction(prompt=prompt, response=f"Error: {err}", domain="error", image_provided=False)

if not st.session_state.messages:
    st.info("👆 Ingest documents and images in the sidebar first, then ask questions.")
