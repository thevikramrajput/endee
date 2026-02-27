"""
CodeDNA Searcher Module
=======================
Semantic search engine powered by Endee vector database.
Supports dense, sparse, and hybrid search modes with advanced filtering.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from endee import Endee

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from core.embedder import CodeEmbedder
from core.sparse import SparseVectorGenerator

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a single search result from Endee."""
    id: str
    similarity: float
    metadata: Dict[str, Any]
    code_preview: str = ""

    def __repr__(self):
        return (
            f"SearchResult(name={self.metadata.get('name', '?')}, "
            f"sim={self.similarity:.4f}, "
            f"lang={self.metadata.get('language', '?')})"
        )


class CodeSearcher:
    """
    Semantic code search engine using Endee.

    Supports three search modes:
    1. Dense search — find semantically similar code
    2. Sparse search — keyword-based code search
    3. Hybrid search — combined dense + sparse for best results

    Also supports advanced Endee filtering with $eq, $in, $range operators.
    """

    def __init__(
        self,
        embedder: Optional[CodeEmbedder] = None,
        sparse_gen: Optional[SparseVectorGenerator] = None,
    ):
        """
        Initialize the searcher.

        Args:
            embedder: CodeEmbedder for generating query embeddings.
            sparse_gen: SparseVectorGenerator for generating sparse query vectors.
        """
        if config.ENDEE_AUTH_TOKEN:
            self.client = Endee(config.ENDEE_AUTH_TOKEN)
        else:
            self.client = Endee()

        base_url = f"http://{config.ENDEE_HOST}:{config.ENDEE_PORT}/api/v1"
        self.client.set_base_url(base_url)

        self.embedder = embedder
        self.sparse_gen = sparse_gen

    def _parse_results(self, raw_results: List[Dict]) -> List[SearchResult]:
        """Parse raw Endee results into SearchResult objects."""
        results = []
        for item in raw_results:
            results.append(
                SearchResult(
                    id=item.get("id", ""),
                    similarity=item.get("similarity", 0.0),
                    metadata=item.get("meta", {}),
                )
            )
        return results

    # ─── Dense Search ────────────────────────────────────────────────

    def search_dense(
        self,
        query: str,
        top_k: int = 10,
        language: Optional[str] = None,
        unit_type: Optional[str] = None,
        min_complexity: Optional[int] = None,
        max_complexity: Optional[int] = None,
        min_loc: Optional[int] = None,
        max_loc: Optional[int] = None,
    ) -> List[SearchResult]:
        """
        Perform dense (semantic) search on the code_functions index.

        Args:
            query: Natural language or code query.
            top_k: Number of results to return.
            language: Filter by programming language.
            unit_type: Filter by unit type ("function", "class", "module").
            min_complexity: Filter by minimum complexity.
            max_complexity: Filter by maximum complexity.
            min_loc: Filter by minimum lines of code.
            max_loc: Filter by maximum lines of code.

        Returns:
            List of SearchResult objects sorted by similarity.
        """
        if not self.embedder:
            raise RuntimeError("Embedder required for dense search")

        # Generate query embedding
        query_vector = self.embedder.embed_query(query)

        # Build Endee filters using $eq, $in, $range operators
        filters = self._build_filters(
            language=language,
            unit_type=unit_type,
            min_complexity=min_complexity,
            max_complexity=max_complexity,
            min_loc=min_loc,
            max_loc=max_loc,
        )

        try:
            index = self.client.get_index(name=config.DENSE_INDEX_NAME)
            raw_results = index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filters if filters else None,
            )
            return self._parse_results(raw_results)

        except Exception as e:
            logger.error(f"Dense search failed: {e}")
            return []

    # ─── Hybrid Search ───────────────────────────────────────────────

    def search_hybrid(
        self,
        query: str,
        top_k: int = 10,
        language: Optional[str] = None,
        unit_type: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Perform hybrid (dense + sparse) search on the code_hybrid index.
        Combines semantic understanding with keyword matching.

        Args:
            query: Search query (natural language or code).
            top_k: Number of results.
            language: Filter by language.
            unit_type: Filter by unit type.

        Returns:
            List of SearchResult objects.
        """
        if not self.embedder:
            raise RuntimeError("Embedder required for hybrid search")
        if not self.sparse_gen:
            raise RuntimeError("SparseVectorGenerator required for hybrid search")

        # Generate dense query vector
        dense_vector = self.embedder.embed_query(query)

        # Generate sparse query vector
        sparse_indices, sparse_values = self.sparse_gen.query_sparse(query)

        # Build filters
        filters = self._build_filters(
            language=language, unit_type=unit_type
        )

        try:
            index = self.client.get_index(name=config.HYBRID_INDEX_NAME)
            raw_results = index.query(
                vector=dense_vector,
                sparse_indices=sparse_indices,
                sparse_values=sparse_values,
                top_k=top_k,
                filter=filters if filters else None,
            )
            return self._parse_results(raw_results)

        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []

    # ─── Similarity Search ───────────────────────────────────────────

    def find_similar_code(
        self, code_snippet: str, top_k: int = 10
    ) -> List[SearchResult]:
        """
        Find code similar to a given code snippet.

        Args:
            code_snippet: Raw code to find similar matches for.
            top_k: Number of results.

        Returns:
            List of similar code search results.
        """
        if not self.embedder:
            raise RuntimeError("Embedder required")

        query_vector = self.embedder.embed_text(code_snippet)

        try:
            index = self.client.get_index(name=config.DENSE_INDEX_NAME)
            raw_results = index.query(vector=query_vector, top_k=top_k)
            return self._parse_results(raw_results)
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []

    # ─── Anti-Pattern Search ─────────────────────────────────────────

    def find_antipattern_matches(
        self, code_snippet: str, top_k: int = 5
    ) -> List[SearchResult]:
        """
        Search for anti-patterns similar to a given code snippet.

        Args:
            code_snippet: Code to check against anti-pattern database.
            top_k: Number of anti-pattern matches to return.

        Returns:
            List of matching anti-patterns with similarity scores.
        """
        if not self.embedder:
            raise RuntimeError("Embedder required")

        query_vector = self.embedder.embed_text(code_snippet)

        try:
            index = self.client.get_index(name=config.ANTIPATTERN_INDEX_NAME)
            raw_results = index.query(vector=query_vector, top_k=top_k)
            return self._parse_results(raw_results)
        except Exception as e:
            logger.error(f"Anti-pattern search failed: {e}")
            return []

    # ─── Filter Builder ──────────────────────────────────────────────

    def _build_filters(
        self,
        language: Optional[str] = None,
        unit_type: Optional[str] = None,
        min_complexity: Optional[int] = None,
        max_complexity: Optional[int] = None,
        min_loc: Optional[int] = None,
        max_loc: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Build Endee filter dict using $eq, $in, $range operators.

        Demonstrates Endee's advanced filtering capabilities.
        """
        filters = {}

        # Exact match filter ($eq)
        if language:
            filters["language"] = {"$eq": language}

        if unit_type:
            filters["unit_type"] = {"$eq": unit_type}

        # Range filter ($range)
        if min_complexity is not None or max_complexity is not None:
            complexity_range = {}
            if min_complexity is not None:
                complexity_range["gte"] = min_complexity
            if max_complexity is not None:
                complexity_range["lte"] = max_complexity
            filters["complexity"] = {"$range": complexity_range}

        if min_loc is not None or max_loc is not None:
            loc_range = {}
            if min_loc is not None:
                loc_range["gte"] = min_loc
            if max_loc is not None:
                loc_range["lte"] = max_loc
            filters["loc"] = {"$range": loc_range}

        return filters

    # ─── Multi-Language Search ───────────────────────────────────────

    def search_across_languages(
        self,
        query: str,
        languages: List[str],
        top_k_per_language: int = 5,
    ) -> Dict[str, List[SearchResult]]:
        """
        Search for similar code across multiple languages.
        Demonstrates cross-language semantic understanding.

        Args:
            query: Search query.
            languages: List of language names to search in.
            top_k_per_language: Results per language.

        Returns:
            Dict mapping language -> list of results.
        """
        results = {}
        for lang in languages:
            lang_results = self.search_dense(
                query=query,
                top_k=top_k_per_language,
                language=lang,
            )
            results[lang] = lang_results
        return results
