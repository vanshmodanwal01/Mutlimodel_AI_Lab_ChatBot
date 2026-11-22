import streamlit as st
from typing import Tuple, Optional, Any


def render_multimodal_inputs() -> Tuple[Optional[Any], Optional[Any]]:
    """Renders expandable drawers for Image and Audio attachments."""
    attached_image = None
    attached_audio = None

    with st.expander("📎 Attach Image or Audio Input", expanded=False):
        col_img, col_aud = st.columns(2)
        with col_img:
            st.markdown("🖼️ **Image Input** (JPG, PNG, WEBP)")
            attached_image = st.file_uploader(
                "Upload Image",
                type=["jpg", "jpeg", "png", "webp"],
                key="chat_image_uploader",
                label_visibility="collapsed"
            )
            if attached_image is not None:
                st.image(attached_image, width=180, caption="Preview")

        with col_aud:
            st.markdown("🎙️ **Audio Recording or File** (WAV, MP3)")
            # Support audio file upload or microphone recording
            attached_audio = st.file_uploader(
                "Upload Audio",
                type=["wav", "mp3", "m4a", "ogg"],
                key="chat_audio_uploader",
                label_visibility="collapsed"
            )
            if attached_audio is not None:
                st.audio(attached_audio)

    return attached_image, attached_audio
