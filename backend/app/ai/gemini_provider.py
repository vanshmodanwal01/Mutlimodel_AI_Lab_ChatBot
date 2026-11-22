import os
import re
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
from PIL import Image
import numpy as np

from backend.app.ai.base import BaseLLMProvider, BaseEmbeddingProvider, BaseVisionProvider
from backend.app.core.config import settings
from backend.app.core.logging import logger


class GeminiProvider(BaseLLMProvider, BaseEmbeddingProvider, BaseVisionProvider):
    """Google Gemini AI integration supporting text chat, vision, and embeddings."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.embedding_model_name = settings.EMBEDDING_MODEL
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initializes Google GenAI client if credentials are configured."""
        if self.api_key and self.api_key.strip():
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized Gemini client with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Google GenAI SDK: {e}")
                self._client = None
        else:
            logger.info("GEMINI_API_KEY not configured. Running in guided configuration mode.")

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generates conversational response using Gemini."""
        if not self.is_configured:
            return (
                "**MindBridge AI System Notice**:\n\n"
                "The Gemini API key is currently not configured. "
                "To enable live AI generation, please obtain an API key from "
                "[Google AI Studio](https://aistudio.google.com/) and paste it into your `.env` file under `GEMINI_API_KEY=`.\n\n"
                f"Your query was received: *\"{prompt}\"*"
            )

        try:
            contents = []
            if chat_history:
                for msg in chat_history:
                    contents.append(f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}")
            contents.append(f"User: {prompt}")
            full_prompt = "\n\n".join(contents)

            config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
            if system_instruction:
                config["system_instruction"] = system_instruction

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=config
            )
            return response.text or "I understand, but I couldn't generate a text response."
        except Exception as e:
            logger.error(f"Gemini LLM generation error: {e}", exc_info=True)
            return f"I encountered a temporary issue while generating a response. Details: {str(e)}"

    def _fallback_hash_embedding(self, text: str, dim: int = 768) -> List[float]:
        """Feature hashing token embedding used when running without cloud credentials."""
        vec = np.zeros(dim, dtype=np.float32)
        words = re.findall(r"\w+", text.lower())
        if not words:
            return [0.0] * dim
        for word in words:
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest()[:8], 16)
            idx = h % dim
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def generate_embedding(self, text: str) -> List[float]:
        """Generates dense vector embedding for single text chunk."""
        if not self.is_configured:
            return self._fallback_hash_embedding(text)

        try:
            result = self._client.models.embed_content(
                model=self.embedding_model_name,
                contents=text
            )
            if hasattr(result, "embedding") and hasattr(result.embedding, "values"):
                return result.embedding.values
            elif hasattr(result, "embeddings") and len(result.embeddings) > 0:
                return result.embeddings[0].values
            return self._fallback_hash_embedding(text)
        except Exception as e:
            logger.error(f"Gemini embedding error: {e}", exc_info=True)
            return self._fallback_hash_embedding(text)

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for multiple text passages."""
        return [self.generate_embedding(t) for t in texts]

    def analyze_image(
        self,
        image_path: str,
        user_query: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """Analyzes an image file using Gemini Vision capabilities."""
        if not self.is_configured:
            return (
                "**MindBridge AI Notice**: Gemini API key required for vision analysis. "
                f"Image '{Path(image_path).name}' was uploaded and verified successfully."
            )

        try:
            pil_image = Image.open(image_path)
            prompt_parts = [user_query, pil_image]

            config = {}
            if system_instruction:
                config["system_instruction"] = system_instruction

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt_parts,
                config=config if config else None
            )
            return response.text or "I analyzed the image, but could not produce a descriptive response."
        except Exception as e:
            logger.error(f"Gemini Vision analysis error: {e}", exc_info=True)
            return f"Failed to analyze the image: {str(e)}"
