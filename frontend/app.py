import uuid
import streamlit as st
from pathlib import Path

from frontend.services.api_client import APIClient
from frontend.components.sidebar import render_sidebar
from frontend.components.chat_view import render_chat_view
from frontend.components.file_uploader import render_multimodal_inputs

# Configure page layout
st.set_page_config(
    page_title="MindBridge AI | Multimodal Conversational Platform",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = Path(__file__).resolve().parent / "assets" / "custom.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize API Client
api_client = APIClient()

# Render Sidebar (Session manager, RAG document uploader, toggles)
render_sidebar(api_client)

# Main Application Header
st.markdown('<div class="main-header">MindBridge AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Secure Multimodal AI Companion & Retrieval-Augmented Generation Platform</div>',
    unsafe_allow_html=True
)

# Render Chat View
render_chat_view(st.session_state.messages)

# Render Multimodal Attachments Drawer (Image / Audio)
attached_image, attached_audio = render_multimodal_inputs()

# Chat Input Field
user_query = st.chat_input("Message MindBridge AI...")

if user_query or attached_image or attached_audio:
    query_text = user_query or ""
    
    # Construct User Message for UI
    user_msg_item = {
        "role": "user",
        "content": query_text if query_text else "[Multimodal Attachment]",
        "image_preview": attached_image.getvalue() if attached_image else None
    }
    st.session_state.messages.append(user_msg_item)

    # Process Request via FastAPI Backend
    with st.spinner("MindBridge AI is thinking..."):
        try:
            if attached_image or attached_audio:
                # Multimodal Endpoint
                res = api_client.send_multimodal_message(
                    session_id=st.session_state.session_id,
                    message=query_text,
                    image_file=attached_image,
                    audio_file=attached_audio,
                    enable_rag=st.session_state.get("enable_rag", True),
                    enable_tts=st.session_state.get("enable_tts", False)
                )
            else:
                # Text Chat Endpoint
                res = api_client.send_chat_message(
                    session_id=st.session_state.session_id,
                    message=query_text,
                    enable_rag=st.session_state.get("enable_rag", True),
                    enable_tts=st.session_state.get("enable_tts", False)
                )

            # Append Assistant Message to UI
            assistant_msg_item = {
                "role": "assistant",
                "content": res.get("reply", "No response received."),
                "citations": res.get("citations", []),
                "crisis_detected": res.get("crisis_detected", False),
                "audio_base64": res.get("audio_base64")
            }
            st.session_state.messages.append(assistant_msg_item)
            st.rerun()

        except Exception as e:
            st.error(f"Communication error with MindBridge backend: {str(e)}")
