"""
CodeDNA Sparse Vector Module
=============================
Generates sparse vector representations of code using TF-IDF.
Used for Endee's hybrid search (dense + sparse) capability.
"""

import re
import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from core.parser import CodeUnit

logger = logging.getLogger(__name__)


class CodeTokenizer:
    """
    Specialized tokenizer for source code.
    Handles camelCase, snake_case, and code-specific tokens.
    """

    # Common programming keywords to keep as-is
    KEYWORDS = {
        "def", "class", "function", "return", "if", "else", "for",
        "while", "import", "from", "try", "except", "catch", "throw",
        "async", "await", "yield", "lambda", "new", "this", "self",
        "public", "private", "protected", "static", "final", "const",
        "let", "var", "interface", "enum", "struct", "void", "int",
        "string", "float", "bool", "boolean", "list", "dict", "map",
        "array", "set", "null", "none", "true", "false", "isinstance",
        "typeof", "switch", "case", "break", "continue", "extends",
        "implements", "abstract", "override", "super", "with", "as",
    }

    @staticmethod
    def tokenize(code: str) -> List[str]:
        """
        Tokenize source code into meaningful tokens.

        Handles:
        - camelCase splitting
        - snake_case splitting
        - Preserving keywords
        - Removing noise (brackets, operators, etc.)
        """
        # Remove comments
        code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)  # Python
        code = re.sub(r"//.*$", "", code, flags=re.MULTILINE)  # JS/Java
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)  # Block comments
        code = re.sub(r'""".*?"""', "", code, flags=re.DOTALL)  # Python docstrings
        code = re.sub(r"'''.*?'''", "", code, flags=re.DOTALL)

        # Remove string literals
        code = re.sub(r'"[^"]*"', " STR ", code)
        code = re.sub(r"'[^']*'", " STR ", code)

        # Remove numbers but keep a marker
        code = re.sub(r"\b\d+\.?\d*\b", " NUM ", code)

        # Split camelCase
        code = re.sub(r"([a-z])([A-Z])", r"\1 \2", code)

        # Replace non-alphanumeric with spaces
        code = re.sub(r"[^a-zA-Z_]", " ", code)

        # Tokenize and filter
        tokens = code.lower().split()
        tokens = [t for t in tokens if len(t) > 1 and t not in {"str", "num"}]

        return tokens


class SparseVectorGenerator:
    """
    Generates sparse vectors for code using TF-IDF.
    These are used in Endee's hybrid search alongside dense embeddings.
    """

    def __init__(self, max_features: int = None):
        """
        Initialize the sparse vector generator.

        Args:
            max_features: Maximum vocabulary size. Defaults to HYBRID_SPARSE_DIM.
        """
        self.max_features = max_features or config.HYBRID_SPARSE_DIM
        self.tokenizer = CodeTokenizer()
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            tokenizer=self._tokenize_for_tfidf,
            token_pattern=None,
            lowercase=True,
            max_df=0.95,  # Ignore terms appearing in >95% of documents
            min_df=2,  # Ignore terms appearing in <2 documents
            norm="l2",
        )
        self.is_fitted = False

    def _tokenize_for_tfidf(self, text: str) -> List[str]:
        """Tokenizer function for TF-IDF vectorizer."""
        return self.tokenizer.tokenize(text)

    def fit(self, units: List[CodeUnit]) -> None:
        """
        Fit the TF-IDF vectorizer on a corpus of code units.

        Args:
            units: List of CodeUnit objects to build vocabulary from.
        """
        texts = [unit.code for unit in units]
        logger.info(f"Fitting sparse vectorizer on {len(texts)} code units...")
        self.vectorizer.fit(texts)
        self.is_fitted = True
        vocab_size = len(self.vectorizer.vocabulary_)
        logger.info(f"Vocabulary size: {vocab_size}")

    def generate_sparse_vector(
        self, unit: CodeUnit
    ) -> Tuple[List[int], List[float]]:
        """
        Generate a sparse vector for a single code unit.

        Returns:
            Tuple of (indices, values) representing the sparse vector.
            - indices: List of non-zero dimension indices
            - values: List of corresponding TF-IDF values
        """
        if not self.is_fitted:
            raise RuntimeError(
                "Vectorizer not fitted. Call fit() first or use generate_simple_sparse()."
            )

        tfidf_vector = self.vectorizer.transform([unit.code])
        csr = tfidf_vector.tocsr()

        indices = csr.indices.tolist()
        values = csr.data.tolist()

        return indices, values

    def generate_sparse_vectors(
        self, units: List[CodeUnit]
    ) -> List[Tuple[List[int], List[float]]]:
        """
        Generate sparse vectors for multiple code units.

        Returns:
            List of (indices, values) tuples.
        """
        if not self.is_fitted:
            raise RuntimeError("Vectorizer not fitted. Call fit() first.")

        texts = [unit.code for unit in units]
        tfidf_matrix = self.vectorizer.transform(texts)

        results = []
        for i in range(tfidf_matrix.shape[0]):
            row = tfidf_matrix.getrow(i).tocsr()
            indices = row.indices.tolist()
            values = row.data.tolist()
            results.append((indices, values))

        return results

    def generate_simple_sparse(
        self, text: str, vocab_size: int = None
    ) -> Tuple[List[int], List[float]]:
        """
        Generate a simple sparse vector without fitting (using hash-based approach).
        Useful for queries when the vectorizer isn't fitted.

        Args:
            text: Raw text/code to vectorize.
            vocab_size: Size of sparse vector space.

        Returns:
            Tuple of (indices, values).
        """
        vocab_size = vocab_size or self.max_features
        tokens = self.tokenizer.tokenize(text)
        token_counts = Counter(tokens)
        total = sum(token_counts.values()) or 1

        indices = []
        values = []
        for token, count in token_counts.items():
            # Hash token to get index
            idx = hash(token) % vocab_size
            if idx < 0:
                idx += vocab_size
            tf = count / total
            indices.append(idx)
            values.append(float(tf))

        return indices, values

    def query_sparse(
        self, query: str
    ) -> Tuple[List[int], List[float]]:
        """
        Generate sparse vector for a search query.

        Uses the fitted vectorizer if available, otherwise falls back
        to hash-based approach.

        Args:
            query: Search query string.

        Returns:
            Tuple of (indices, values).
        """
        if self.is_fitted:
            tfidf_vector = self.vectorizer.transform([query])
            csr = tfidf_vector.tocsr()
            return csr.indices.tolist(), csr.data.tolist()
        else:
            return self.generate_simple_sparse(query)
