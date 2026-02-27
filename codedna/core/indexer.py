"""
CodeDNA Indexer Module
======================
Manages all interactions with the Endee vector database.
Handles index creation, vector upserting, and index management.
Showcases Endee's dense, hybrid, and multi-precision capabilities.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple

from endee import Endee, Precision

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from core.parser import CodeUnit
from core.embedder import CodeEmbedder
from core.sparse import SparseVectorGenerator

logger = logging.getLogger(__name__)


class EndeeIndexer:
    """
    Manages Endee vector database operations for CodeDNA.

    Creates and manages three types of indexes:
    1. Dense index (code_functions) — function-level semantic search
    2. Hybrid index (code_hybrid) — combined dense + sparse search
    3. Anti-pattern index (anti_patterns) — code smell detection
    """

    def __init__(
        self,
        embedder: Optional[CodeEmbedder] = None,
        sparse_gen: Optional[SparseVectorGenerator] = None,
    ):
        """
        Initialize the Endee indexer.

        Args:
            embedder: CodeEmbedder instance for generating dense vectors.
            sparse_gen: SparseVectorGenerator for generating sparse vectors.
        """
        # Connect to Endee
        if config.ENDEE_AUTH_TOKEN:
            self.client = Endee(config.ENDEE_AUTH_TOKEN)
        else:
            self.client = Endee()

        # Set custom base URL if needed
        base_url = f"http://{config.ENDEE_HOST}:{config.ENDEE_PORT}/api/v1"
        self.client.set_base_url(base_url)

        self.embedder = embedder
        self.sparse_gen = sparse_gen

        logger.info(f"Connected to Endee at {base_url}")

    def _wait_for_endee(self, max_retries: int = 10, delay: float = 2.0):
        """Wait for Endee server to be ready."""
        for attempt in range(max_retries):
            try:
                self.client.list_indexes()
                logger.info("Endee server is ready!")
                return True
            except Exception as e:
                logger.warning(
                    f"Endee not ready (attempt {attempt + 1}/{max_retries}): {e}"
                )
                time.sleep(delay)
        raise ConnectionError("Could not connect to Endee server")

    # ─── Index Management ───────────────────────────────────────────

    def setup_indexes(self) -> Dict[str, bool]:
        """
        Create all required indexes in Endee.
        Returns dict of index_name -> success status.
        """
        self._wait_for_endee()
        results = {}

        # 1. Dense index for function-level code search
        results["dense"] = self._create_dense_index()

        # 2. Hybrid index for combined search
        results["hybrid"] = self._create_hybrid_index()

        # 3. Anti-pattern reference index
        results["antipattern"] = self._create_antipattern_index()

        return results

    def _create_dense_index(self) -> bool:
        """Create the dense code functions index."""
        try:
            raw = self.client.list_indexes()
            index_list = raw.get("indexes", []) if isinstance(raw, dict) else raw
            existing = [idx["name"] for idx in index_list if isinstance(idx, dict)]
            if config.DENSE_INDEX_NAME in existing:
                logger.info(
                    f"Index '{config.DENSE_INDEX_NAME}' already exists, skipping."
                )
                return True

            dim = self.embedder.get_dimension() if self.embedder else config.DENSE_DIMENSION
            self.client.create_index(
                name=config.DENSE_INDEX_NAME,
                dimension=dim,
                space_type=config.DENSE_SPACE_TYPE,
                precision=Precision.FLOAT16,  # Good balance of speed & accuracy
            )
            logger.info(
                f"Created dense index '{config.DENSE_INDEX_NAME}' "
                f"(dim={dim}, precision=FLOAT16)"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create dense index: {e}")
            return False

    def _create_hybrid_index(self) -> bool:
        """Create the hybrid (dense + sparse) index."""
        try:
            raw = self.client.list_indexes()
            index_list = raw.get("indexes", []) if isinstance(raw, dict) else raw
            existing = [idx["name"] for idx in index_list if isinstance(idx, dict)]
            if config.HYBRID_INDEX_NAME in existing:
                logger.info(
                    f"Index '{config.HYBRID_INDEX_NAME}' already exists, skipping."
                )
                return True

            dim = self.embedder.get_dimension() if self.embedder else config.HYBRID_DENSE_DIM
            self.client.create_index(
                name=config.HYBRID_INDEX_NAME,
                dimension=dim,
                sparse_dim=config.HYBRID_SPARSE_DIM,
                space_type=config.DENSE_SPACE_TYPE,
                precision=Precision.FLOAT16,  # Compatible with hybrid dense+sparse
            )
            logger.info(
                f"Created hybrid index '{config.HYBRID_INDEX_NAME}' "
                f"(dense_dim={dim}, sparse_dim={config.HYBRID_SPARSE_DIM}, precision=FLOAT16)"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create hybrid index: {e}")
            return False

    def _create_antipattern_index(self) -> bool:
        """Create the anti-pattern reference index."""
        try:
            raw = self.client.list_indexes()
            index_list = raw.get("indexes", []) if isinstance(raw, dict) else raw
            existing = [idx["name"] for idx in index_list if isinstance(idx, dict)]
            if config.ANTIPATTERN_INDEX_NAME in existing:
                logger.info(
                    f"Index '{config.ANTIPATTERN_INDEX_NAME}' already exists, skipping."
                )
                return True

            dim = self.embedder.get_dimension() if self.embedder else config.ANTIPATTERN_DIMENSION
            self.client.create_index(
                name=config.ANTIPATTERN_INDEX_NAME,
                dimension=dim,
                space_type="cosine",
                precision=Precision.FLOAT32,  # Highest accuracy for pattern matching
            )
            logger.info(
                f"Created anti-pattern index '{config.ANTIPATTERN_INDEX_NAME}' "
                f"(dim={dim}, precision=FLOAT32)"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create anti-pattern index: {e}")
            return False

    def list_indexes(self) -> List[Dict]:
        """List all existing indexes in Endee."""
        try:
            raw = self.client.list_indexes()
            if isinstance(raw, dict):
                return raw.get("indexes", [])
            return raw
        except Exception as e:
            logger.error(f"Failed to list indexes: {e}")
            return []

    def delete_all_indexes(self) -> None:
        """Delete all CodeDNA indexes (useful for reset)."""
        for name in [
            config.DENSE_INDEX_NAME,
            config.HYBRID_INDEX_NAME,
            config.ANTIPATTERN_INDEX_NAME,
        ]:
            try:
                self.client.delete_index(name=name)
                logger.info(f"Deleted index: {name}")
            except Exception:
                pass

    # ─── Vector Upserting ────────────────────────────────────────────

    def upsert_to_dense(self, units: List[CodeUnit]) -> int:
        """
        Embed and upsert code units to the dense index.

        Args:
            units: List of CodeUnit objects to index.

        Returns:
            Number of vectors successfully upserted.
        """
        if not self.embedder:
            raise RuntimeError("Embedder not initialized")

        index = self.client.get_index(name=config.DENSE_INDEX_NAME)
        embeddings = self.embedder.embed_units(units)
        count = 0

        # Batch upsert
        for i in range(0, len(units), config.BATCH_SIZE):
            batch_units = units[i : i + config.BATCH_SIZE]
            batch_embeddings = embeddings[i : i + config.BATCH_SIZE]

            vectors = []
            for unit, embedding in zip(batch_units, batch_embeddings):
                vectors.append(
                    {
                        "id": unit.id,
                        "vector": embedding,
                        "meta": unit.to_metadata(),
                        "filter": unit.to_filter(),
                    }
                )

            try:
                index.upsert(vectors)
                count += len(vectors)
                logger.info(
                    f"Upserted batch {i // config.BATCH_SIZE + 1} "
                    f"({count}/{len(units)} vectors)"
                )
            except Exception as e:
                logger.error(f"Failed to upsert batch: {e}")

        return count

    def upsert_to_hybrid(self, units: List[CodeUnit]) -> int:
        """
        Embed and upsert code units to the hybrid index (dense + sparse).

        Args:
            units: List of CodeUnit objects.

        Returns:
            Number of vectors successfully upserted.
        """
        if not self.embedder or not self.sparse_gen:
            raise RuntimeError("Embedder and SparseVectorGenerator required")

        index = self.client.get_index(name=config.HYBRID_INDEX_NAME)

        # Generate dense embeddings
        dense_embeddings = self.embedder.embed_units(units)

        # Generate sparse vectors
        sparse_vectors = self.sparse_gen.generate_sparse_vectors(units)

        count = 0
        for i in range(0, len(units), config.BATCH_SIZE):
            batch_units = units[i : i + config.BATCH_SIZE]
            batch_dense = dense_embeddings[i : i + config.BATCH_SIZE]
            batch_sparse = sparse_vectors[i : i + config.BATCH_SIZE]

            vectors = []
            for unit, dense, (sparse_idx, sparse_val) in zip(
                batch_units, batch_dense, batch_sparse
            ):
                vectors.append(
                    {
                        "id": f"hybrid_{unit.id}",
                        "vector": dense,
                        "sparse_indices": sparse_idx,
                        "sparse_values": sparse_val,
                        "meta": unit.to_metadata(),
                        "filter": unit.to_filter(),
                    }
                )

            try:
                index.upsert(vectors)
                count += len(vectors)
                logger.info(
                    f"Upserted hybrid batch {i // config.BATCH_SIZE + 1} "
                    f"({count}/{len(units)} vectors)"
                )
            except Exception as e:
                logger.error(f"Failed to upsert hybrid batch: {e}")

        return count

    def upsert_antipatterns(
        self, patterns: List[Dict[str, Any]]
    ) -> int:
        """
        Upsert anti-pattern reference vectors.

        Args:
            patterns: List of dicts with keys: id, name, code, category, severity, description

        Returns:
            Number of patterns upserted.
        """
        if not self.embedder:
            raise RuntimeError("Embedder not initialized")

        index = self.client.get_index(name=config.ANTIPATTERN_INDEX_NAME)

        vectors = []
        for pattern in patterns:
            embedding = self.embedder.embed_text(pattern["code"])
            vectors.append(
                {
                    "id": pattern["id"],
                    "vector": embedding,
                    "meta": {
                        "name": pattern["name"],
                        "category": pattern["category"],
                        "severity": pattern["severity"],
                        "description": pattern["description"],
                    },
                    "filter": {
                        "category": pattern["category"],
                        "severity": pattern["severity"],
                    },
                }
            )

        try:
            index.upsert(vectors)
            logger.info(f"Upserted {len(vectors)} anti-patterns")
            return len(vectors)
        except Exception as e:
            logger.error(f"Failed to upsert anti-patterns: {e}")
            return 0

    # ─── Full Indexing Pipeline ──────────────────────────────────────

    def index_codebase(self, units: List[CodeUnit]) -> Dict[str, int]:
        """
        Run the full indexing pipeline: upsert to both dense and hybrid indexes.

        Args:
            units: All parsed code units from a repository.

        Returns:
            Dict with counts: {"dense": N, "hybrid": N}
        """
        results = {}

        # Fit sparse vectorizer on the corpus
        if self.sparse_gen and len(units) > 5:
            self.sparse_gen.fit(units)

        # Upsert to dense index
        logger.info("=== Indexing to Dense Index ===")
        results["dense"] = self.upsert_to_dense(units)

        # Upsert to hybrid index (if sparse gen is available and fitted)
        if self.sparse_gen and self.sparse_gen.is_fitted:
            logger.info("=== Indexing to Hybrid Index ===")
            results["hybrid"] = self.upsert_to_hybrid(units)
        else:
            results["hybrid"] = 0
            logger.warning("Skipping hybrid indexing (sparse vectorizer not fitted)")

        return results

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about all CodeDNA indexes."""
        stats = {}
        for name in [
            config.DENSE_INDEX_NAME,
            config.HYBRID_INDEX_NAME,
            config.ANTIPATTERN_INDEX_NAME,
        ]:
            try:
                idx = self.client.get_index(name=name)
                stats[name] = {"status": "active", "name": name}
            except Exception:
                stats[name] = {"status": "not_found", "name": name}
        return stats
