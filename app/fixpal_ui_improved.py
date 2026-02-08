"""FixPalAI Streamlit app - improved UI with real backend integration."""

import sys
from pathlib import Path
import tempfile
import uuid

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
from src.agents.coordinator import classify_domain
from src.agents.specialists.registry import get_specialist_response
from src.agents.vision_analysis import analyze_image
from src.evaluation.eval_agent import log_interaction

DOMAIN_META = {
    "plumbing":   {"emoji": "💧", "color": "#2563EB"},
    "electrical": {"emoji": "⚡", "color": "#D97706"},
    "carpentry":  {"emoji": "🔨", "color": "#7C3AED"},
    "hvac":       {"emoji": "❄️", "color": "#0891B2"},
    "general":    {"emoji": "🔧", "color": "#6B7280"},
}

st.set_page_config(
    page_title="FixPalAI - AI Technician Copilot",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS (same as your design)
st.markdown("""
<style>
    :root { --primary: #4F46E5; --success: #10B981; --warning: #F59E0B; --danger: #EF4444; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem; border-radius: 10px; color: white;
        margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 { margin: 0; font-size: 2.5rem; font-weight: 700; }
    .main-header p { margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; }
    .quick-card {
        background: white; border: 2px solid #e5e7eb; border-radius: 12px;
        padding: 1.5rem; text-align: center; cursor: pointer;
        transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .quick-card:hover { border-color: #4F46E5; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2); }
    .user-message { background: #EEF2FF; border-left: 4px solid #4F46E5; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .ai-message { background: #F0FDF4; border-left: 4px solid #10B981; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .sidebar-section { background: #F9FAFB; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
    .sidebar-section h3 { font-size: 0.9rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem; }
    .status-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.875rem; font-weight: 600; }
    .status-connected { background: #D1FAE5; color: #065F46; }
    .recent-chat { padding: 0.75rem; border-radius: 6px; cursor: pointer; border-left: 3px solid transparent; }
    .recent-chat:hover { background: #F3F4F6; border-left-color: #4F46E5; }
</style>
""", unsafe_allow_html=True)


def get_all_sources(vs) -> list[dict]:
    """Get unique sources from the vector store with chunk counts."""
    try:
        collection = vs._collection
        results = collection.get(include=["metadatas"])
        source_map: dict[str, dict] = {}
        for meta in (results.get("metadatas") or []):
            if not meta or "source" not in meta:
                continue
            src = meta["source"]
            if src not in source_map:
                source_map[src] = {
                    "name": src,
                    "type": meta.get("source_type", "unknown"),
                    "domain": meta.get("domain", ""),
                    "chunks": 0,
                }
            source_map[src]["chunks"] += 1
        return sorted(source_map.values(), key=lambda x: x["name"])
    except Exception:
        return []


def delete_source(vs, source_name: str) -> int:
    """Delete all chunks belonging to a source. Returns count deleted."""
    try:
        collection = vs._collection
        results = collection.get(where={"source": source_name}, include=[])
        ids = results.get("ids", [])
        if ids:
            collection.delete(ids=ids)
        return len(ids)
    except Exception as e:
        st.error(f"Failed to remove source: {e}")
        return 0


@st.dialog("📚 Manage Knowledge Sources", width="large")
def manage_sources_dialog():
    vs = st.session_state.get("vector_store")
    if vs is None:
        st.warning("⚠️ No knowledge base connected. Upload and ingest documents first.")
        return

    sources = get_all_sources(vs)
    if not sources:
        st.info("📭 No sources ingested yet. Use the Upload Materials section to add repair manuals.")
        return

    count = len(sources)
    st.markdown(
        f"<p style='color:#6B7280;font-size:0.9rem;margin-bottom:0.5rem'>"
        f"{count} source{'s' if count != 1 else ''} in knowledge base</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    for src in sources:
        name = src["name"]
        chunks = src["chunks"]
        domain = src["domain"]
        src_type = src["type"]

        ext = Path(name).suffix.lower()
        if ext == ".pdf":
            icon = "📄"
        elif ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            icon = "🖼️"
        elif ext in (".txt", ".text"):
            icon = "📝"
        else:
            icon = "📎"

        col_info, col_btn = st.columns([5, 1])
        with col_info:
            domain_tag = f" &nbsp;`{domain}`" if domain else ""
            st.markdown(
                f"<div style='padding:0.1rem 0'>{icon} <strong>{name}</strong>{domain_tag}</div>",
                unsafe_allow_html=True,
            )
            st.caption(f"{src_type} · {chunks} chunk{'s' if chunks != 1 else ''}")
        with col_btn:
            if st.button("Remove", key=f"remove_{name}", use_container_width=True):
                removed = delete_source(vs, name)
                if removed > 0:
                    st.toast(f"Removed '{name}' ({removed} chunks)", icon="✅")
                    st.rerun()


def text_to_speech(text: str, max_chars: int = 4000) -> bytes | None:
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
    if "vector_store" not in st.session_state:
        try:
            vs, _ = get_vector_store(namespace="manuals")
            st.session_state.vector_store = vs
        except Exception as e:
            st.session_state.vector_store = None
            st.session_state.vector_store_error = str(e)
    return st.session_state.get("vector_store")


# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Handle clearing input before widget creation
if st.session_state.get("should_clear_input"):
    st.session_state.user_input = ""
    st.session_state.should_clear_input = False

# ---- Sidebar ----
with st.sidebar:
    st.markdown("""
        <div class="main-header" style="padding: 1.5rem; margin-bottom: 1.5rem;">
            <h1 style="font-size: 1.5rem;">🔧 FixPalAI</h1>
            <p style="font-size: 0.9rem;">AI Technician Copilot</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 📚 Knowledge Base")
    if st.session_state.get("vector_store") is not None:
        st.markdown('<span class="status-badge status-connected">✓ Connected</span>', unsafe_allow_html=True)
    else:
        st.caption("Upload & ingest below to connect")
    if st.button("⚙️ Manage Sources", use_container_width=True):
        manage_sources_dialog()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Materials")
    uploaded = st.file_uploader(
        "Add PDF, text, or images",
        type=["pdf", "txt", "jpg", "jpeg", "png", "gif", "webp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if st.button("Ingest uploaded files", use_container_width=True) and uploaded:
        vs = ensure_vector_store()
        if vs is None:
            st.error("Could not connect to vector store. Check API key and setup.")
        else:
            with st.spinner("Processing..."):
                all_chunks = []
                for f in uploaded:
                    ext = Path(f.name).suffix.lower()
                    data = f.read()
                    tmp_dir = Path(tempfile.gettempdir())
                    path = tmp_dir / f"{uuid.uuid4().hex}_{f.name}"
                    path.write_bytes(data)
                    if ext == ".pdf":
                        docs = list(load_document(path, source_type="user"))
                    elif ext in (".txt", ".text"):
                        docs = list(load_document(path, source_type="user"))
                    elif ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
                        try:
                            desc = analyze_image(
                                data,
                                user_query="Describe this image for home repair context. Extract any visible text, labels, or repair-relevant details.",
                            )
                            docs = [DocumentChunk(content=desc, source=f.name, source_type="user")] if desc else []
                        except Exception:
                            docs = []
                    else:
                        docs = []
                    all_chunks.extend(chunk_documents(docs))
                if all_chunks:
                    add_chunks_to_store(vs, all_chunks)
                    st.success(f"Indexed {len(all_chunks)} chunks from {len(uploaded)} file(s).")
                else:
                    st.warning("No content extracted.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 💬 Recent")
    for i, msg in enumerate(reversed(st.session_state.messages)):
        if msg["role"] == "user":
            title = (msg.get("content") or "")[:40] + ("..." if len(msg.get("content") or "") > 40 else "")
            if title:
                st.caption(f"• {title}")
            if i >= 4:
                break
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.should_clear_input = True
        st.rerun()

# ---- Main ----
st.markdown("""
    <div class="main-header">
        <h1>👋 Welcome to FixPalAI</h1>
        <p>Get instant repair guidance — ingest documents in the sidebar, then describe your issue below.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("### 💬 Describe Your Issue")

col_input, col_image = st.columns([2, 1])
with col_input:
    user_input = st.text_area(
        "What's the problem?",
        value=st.session_state.get("user_input", ""),
        placeholder="e.g., My HVAC unit is making a loud grinding noise",
        height=120,
        label_visibility="collapsed",
        key="user_input",
    )
with col_image:
    uploaded_image = st.file_uploader(
        "📷 Upload Photo",
        type=["png", "jpg", "jpeg"],
        help="Optional: upload a photo for visual diagnosis",
    )
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded", use_container_width=True)

col_send, _, col_clear = st.columns([2, 1, 1])
with col_send:
    if st.button("🚀 Get Repair Guide", type="primary", use_container_width=True):
        prompt = (user_input or "").strip()
        if not prompt and not uploaded_image:
            st.warning("Please describe the issue or upload a photo.")
        elif prompt or uploaded_image:
            prompt = prompt or "What do you see in this image? Please suggest repair steps."
            st.session_state.messages.append({
                "role": "user",
                "content": prompt,
                "image": None,
            })
            vs = ensure_vector_store()
            if vs is None:
                err = st.session_state.get("vector_store_error", "Could not connect to vector store.")
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {err}", "domain": "error"})
            else:
                try:
                    with st.status("🔧 Working on your repair guide...", expanded=True) as status:
                        # Step 1: Vision analysis
                        image_context = None
                        if uploaded_image:
                            st.write("📷 Analyzing uploaded image...")
                            data = uploaded_image.read()
                            try:
                                image_context = analyze_image(
                                    data,
                                    user_query=f"User asks: {prompt}. Describe what you see for home repair diagnosis.",
                                )
                                st.write("✓ Image analyzed")
                            except Exception as e:
                                st.write(f"⚠️ Could not analyze image ({e}), continuing without it")

                        # Step 2: Domain classification
                        st.write("🔍 Classifying issue domain...")
                        context_for_domain = prompt
                        if image_context:
                            context_for_domain += f"\nImage context: {image_context}"
                        domain = classify_domain(context_for_domain)
                        dm = DOMAIN_META.get(domain, DOMAIN_META["general"])
                        st.write(f"✓ Routed to **{dm['emoji']} {domain.title()} Specialist**")

                        # Step 3: RAG + specialist response
                        st.write("📚 Searching knowledge base and generating response...")
                        answer, meta = get_specialist_response(
                            domain=domain,
                            user_query=prompt,
                            vector_store=vs,
                            image_context=image_context,
                        )
                        rag_count = meta.get("rag_docs_found", 0)
                        if rag_count:
                            st.write(f"✓ Found **{rag_count}** relevant source(s) in knowledge base")
                        else:
                            st.write("ℹ️ No matching documents found — using general knowledge")

                        # Step 4: Safety
                        warnings = meta.get("safety_warnings", [])
                        if warnings:
                            st.write(f"⚠️ **{len(warnings)} safety warning(s)** added to response")
                        else:
                            st.write("🛡️ Safety check passed")

                        status.update(label="✅ Repair guide ready!", state="complete", expanded=False)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "domain": domain,
                        "meta": meta,
                    })
                    log_interaction(prompt=prompt, response=answer, domain=domain, image_provided=bool(uploaded_image))
                except Exception as e:
                    err = str(e)
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {err}", "domain": "error", "meta": {}})
                    log_interaction(prompt=prompt, response=f"Error: {err}", domain="error", image_provided=bool(uploaded_image))
            st.session_state.should_clear_input = True
            st.rerun()
with col_clear:
    if st.button("🔄 Clear", use_container_width=True):
        st.session_state.should_clear_input = True
        st.rerun()

# ---- Display messages ----
if st.session_state.messages:
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.markdown("### 📋 Repair Guidance")
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            safe_content = (msg.get("content") or "").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            st.markdown(f"""
                <div class="user-message">
                    <strong>🧑‍🔧 You:</strong> {safe_content}
                </div>
            """, unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            domain = msg.get("domain", "general")
            meta = msg.get("meta", {})
            if domain and domain != "error":
                dm = DOMAIN_META.get(domain, DOMAIN_META["general"])
                rag_count = meta.get("rag_docs_found", 0)
                safety_ok = not meta.get("safety_warnings")
                safety_label = "🛡️ Safety cleared" if safety_ok else f"⚠️ {len(meta.get('safety_warnings', []))} warning(s)"
                sources_label = f"📚 {rag_count} source(s)" if rag_count else "📚 General knowledge"
                st.caption(f"{dm['emoji']} **{domain.title()} Specialist** &nbsp;·&nbsp; {sources_label} &nbsp;·&nbsp; {safety_label}")
            st.markdown(f'<div class="ai-message">', unsafe_allow_html=True)
            st.markdown(msg.get("content") or "")
            st.markdown("</div>", unsafe_allow_html=True)
            if msg.get("content"):
                col_tts, col_trace = st.columns([1, 3])
                with col_tts:
                    if st.button("🔊 Read aloud", key=f"tts_ui_{i}"):
                        audio_bytes = text_to_speech(msg["content"])
                        if audio_bytes:
                            st.session_state[f"tts_audio_ui_{i}"] = audio_bytes
                if meta:
                    with col_trace:
                        with st.expander("🔍 Processing trace"):
                            st.markdown(f"- **Domain:** {domain.title()}")
                            st.markdown(f"- **Sources retrieved:** {meta.get('rag_docs_found', 0)}")
                            warnings = meta.get("safety_warnings", [])
                            if warnings:
                                for w in warnings:
                                    st.markdown(f"- ⚠️ {w}")
                            else:
                                st.markdown("- 🛡️ No safety warnings")
                if f"tts_audio_ui_{i}" in st.session_state:
                    b64 = base64.b64encode(st.session_state[f"tts_audio_ui_{i}"]).decode("utf-8")
                    st.markdown(
                        f'<audio src="data:audio/mp3;base64,{b64}" autoplay controls playsinline></audio>',
                        unsafe_allow_html=True,
                    )
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("👆 Describe your issue above or pick a category, then click **Get Repair Guide**.")
    st.markdown("#### 💡 Example queries")
    for ex in [
        "My water heater is leaking from the bottom",
        "HVAC unit won't turn on and thermostat shows error E3",
        "Circuit breaker keeps tripping when I use the microwave",
    ]:
        if st.button(f"💬 {ex}", key=ex):
            st.session_state.user_input = ex
            st.rerun()
