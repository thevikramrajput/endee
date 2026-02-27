"""
CodeDNA Embedder Module
=======================
Generates dense vector embeddings from code using sentence-transformers.
Supports multiple embedding models including CodeBERT and all-MiniLM-L6-v2.
"""

import logging
import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from core.parser import CodeUnit

logger = logging.getLogger(__name__)


class CodeEmbedder:
    """
    Generates dense vector embeddings from code units.

    Uses sentence-transformers models to create fixed-dimension
    embeddings that capture the semantic meaning of code.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the embedder with a pre-trained model.

        Args:
            model_name: HuggingFace model name. Defaults to config.EMBEDDING_MODEL.
        """
        self.model_name = model_name or config.EMBEDDING_MODEL
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")

    def _prepare_code_text(self, unit: CodeUnit) -> str:
        """
        Prepare code text for embedding by creating a rich textual representation.

        Combines the function signature, docstring, and code body into a single
        string that captures both the intent and implementation.
        """
        parts = []

        # Add unit type and name
        parts.append(f"{unit.unit_type}: {unit.name}")

        # Add language context
        parts.append(f"language: {unit.language}")

        # Add docstring if available (high semantic value)
        if unit.docstring:
            parts.append(f"description: {unit.docstring}")

        # Add parameters
        if unit.parameters:
            parts.append(f"parameters: {', '.join(unit.parameters)}")

        # Add the actual code (truncated to max length)
        code_text = unit.code[: config.MAX_SEQUENCE_LENGTH * 4]
        parts.append(f"code:\n{code_text}")

        return "\n".join(parts)

    def embed_unit(self, unit: CodeUnit) -> List[float]:
        """
        Generate embedding for a single code unit.

        Args:
            unit: A CodeUnit extracted by the parser.

        Returns:
            List of floats representing the dense vector embedding.
        """
        text = self._prepare_code_text(unit)
        embedding = self.model.encode(text, show_progress_bar=False)
        return embedding.tolist()

    def embed_units(
        self, units: List[CodeUnit], batch_size: int = 32
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple code units in batches.

        Args:
            units: List of CodeUnit objects.
            batch_size: Number of units to process in each batch.

        Returns:
            List of embedding vectors.
        """
        texts = [self._prepare_code_text(unit) for unit in units]
        logger.info(f"Generating embeddings for {len(texts)} code units...")

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.

        Args:
            query: Natural language or code query string.

        Returns:
            Embedding vector for the query.
        """
        embedding = self.model.encode(
            query,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return embedding.tolist()

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for arbitrary text.

        Args:
            text: Any text string.

        Returns:
            Embedding vector.
        """
        embedding = self.model.encode(
            text,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return embedding.tolist()

    def compute_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First vector.
            embedding2: Second vector.

        Returns:
            Cosine similarity score (0 to 1).
        """
        a = np.array(embedding1)
        b = np.array(embedding2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def get_dimension(self) -> int:
        """Return the embedding dimension of the loaded model."""
        return self.dimension
