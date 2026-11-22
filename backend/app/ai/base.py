from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseLLMProvider(ABC):
    """Abstract interface for Large Language Model generation."""

    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generates conversational text completion."""
        pass


class BaseEmbeddingProvider(ABC):
    """Abstract interface for text embedding generation."""

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """Generates a dense vector embedding for a single text chunk."""
        pass

    @abstractmethod
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates dense vector embeddings for a list of text chunks."""
        pass


class BaseVisionProvider(ABC):
    """Abstract interface for multimodal image comprehension."""

    @abstractmethod
    def analyze_image(
        self,
        image_path: str,
        user_query: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """Understands image content and answers questions grounded in visual data."""
        pass


class BaseSpeechProvider(ABC):
    """Abstract interface for Speech-to-Text and Text-to-Speech."""

    @abstractmethod
    def transcribe(self, audio_file_path: str) -> str:
        """Converts spoken audio into text."""
        pass

    @abstractmethod
    def synthesize(self, text: str, output_path: str) -> str:
        """Synthesizes text into spoken audio and returns the output file path."""
        pass
