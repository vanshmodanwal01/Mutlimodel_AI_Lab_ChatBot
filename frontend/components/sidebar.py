import streamlit as st
import uuid
from frontend.services.api_client import APIClient


def render_sidebar(client: APIClient):
    """Renders session manager, RAG document uploader, and system status widgets."""
    with st.sidebar:
        st.markdown("### 🌉 MindBridge AI")
        st.caption("Secure Multimodal AI Companion")

        # Backend Health Status Badge
        health = client.check_health()
        if health.get("status") == "healthy":
            db_engine = health.get("database", {}).get("engine", "DB")
            gemini_ready = "✅ API Key Ready" if health.get("gemini_configured") else "⚙️ Local Fallback"
            st.success(f"🟢 Backend Online ({db_engine.upper()}) | {gemini_ready}")
        else:
            st.error(f"🔴 Backend Offline: {health.get('error', 'Unreachable')}")
            st.info("Start backend: `uvicorn backend.app.main:app --reload`")

        st.markdown("---")

        # Session Controls
        st.markdown("#### 💬 Conversation Session")
        st.text_input("Active Session ID", value=st.session_state.session_id, disabled=True)

        col_new, col_clear = st.columns(2)
        with col_new:
            if st.button("➕ New", use_container_width=True, help="Start a fresh conversation"):
                st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"
                st.session_state.messages = []
                st.rerun()

        with col_clear:
            if st.button("🗑️ Clear", use_container_width=True, help="Clear active conversation history"):
                try:
                    client.clear_conversation_history(st.session_state.session_id)
                    st.session_state.messages = []
                    st.success("Cleared!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear: {e}")

        st.markdown("---")

        # Modality & RAG Toggles
        st.markdown("#### ⚙️ Chat Settings")
        st.session_state.enable_rag = st.toggle("Enable Document RAG", value=st.session_state.get("enable_rag", True))
        st.session_state.enable_tts = st.toggle("Audio Voice Playback (TTS)", value=st.session_state.get("enable_tts", False))

        st.markdown("---")

        # Document Knowledge Manager
        st.markdown("#### 📚 Knowledge Documents")
        st.caption("Upload PDF, DOCX, or TXT to query via RAG.")

        uploaded_doc = st.file_uploader(
            "Upload knowledge file",
            type=["pdf", "docx", "txt"],
            key="doc_uploader",
            label_visibility="collapsed"
        )
        if uploaded_doc is not None:
            if st.button("📥 Ingest Document", use_container_width=True):
                with st.spinner(f"Ingesting '{uploaded_doc.name}'..."):
                    try:
                        res = client.upload_document(st.session_state.session_id, uploaded_doc)
                        st.success(f"Ingested '{res['filename']}' ({res['chunks_created']} chunks)")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Upload failed: {e}")

        # List Existing Documents for Session
        try:
            doc_list_res = client.list_documents(st.session_state.session_id)
            docs = doc_list_res.get("documents", [])
            if docs:
                st.markdown("**Active Session Files:**")
                for d in docs:
                    col_info, col_del = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"📄 **{d['filename']}**  \n`{d['chunk_count']} chunks | {round(d['file_size']/1024, 1)} KB`")
                    with col_del:
                        if st.button("❌", key=f"del_{d['id']}", help="Delete document"):
                            client.delete_document(d['id'])
                            st.rerun()
            else:
                st.caption("No documents ingested yet.")
        except Exception:
            pass

        st.markdown("---")
        st.markdown(
            "<small style='color: #94a3b8;'>"
            "MindBridge AI is an empathetic support companion and educational platform, not a licensed medical professional."
            "</small>",
            unsafe_allow_html=True
        )
