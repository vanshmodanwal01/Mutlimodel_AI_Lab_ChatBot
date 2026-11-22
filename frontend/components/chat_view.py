import base64
import streamlit as st
from typing import List, Dict, Any


def render_chat_view(messages: List[Dict[str, Any]]):
    """Renders the conversational message history with markdown, citations, crisis cards, and audio players."""
    if not messages:
        st.markdown(
            """
            <div style="text-align: center; padding: 40px 20px; color: #64748b;">
                <h3>🌉 Welcome to MindBridge AI</h3>
                <p>I am your secure, empathetic conversational companion with multimodal understanding and RAG knowledge retrieval.</p>
                <p style="font-size: 0.88rem;">Type a query below, upload an image or audio note, or attach a document in the sidebar to begin.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    for idx, msg in enumerate(messages):
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        citations = msg.get("citations", [])
        crisis_detected = msg.get("crisis_detected", False)
        audio_b64 = msg.get("audio_base64")
        image_preview = msg.get("image_preview")

        with st.chat_message(role):
            # Display image if user attached one
            if image_preview:
                st.image(image_preview, width=320, caption="Attached Image")

            # Crisis Card rendering
            if crisis_detected:
                st.markdown(
                    f"""
                    <div class="crisis-card">
                        <h4>⚠️ Immediate Support & Crisis Help</h4>
                        <div>{content.replace(chr(10), '<br>')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(content)

            # Audio voice response playback
            if audio_b64:
                try:
                    audio_bytes = base64.b64decode(audio_b64)
                    st.audio(audio_bytes, format="audio/mp3")
                except Exception:
                    pass

            # RAG Citations & Source Attributions
            if citations:
                with st.expander(f"📚 Verified Sources ({len(citations)} citations)", expanded=False):
                    for cit in citations:
                        filename = cit.get("filename", "Document")
                        chunk_idx = cit.get("chunk_index", 0) + 1
                        score = cit.get("score", 0.0)
                        snippet = cit.get("snippet", "")
                        st.markdown(
                            f"""
                            <div style="margin-bottom: 8px; padding: 8px; background: rgba(0,0,0,0.02); border-radius: 6px;">
                                <span class="citation-pill">{filename} (Chunk {chunk_idx})</span>
                                <small style="color: #64748b;">Relevance: {score}</small>
                                <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #334155;"><em>"{snippet}"</em></p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
