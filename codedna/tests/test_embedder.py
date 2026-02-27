"""
CodeDNA — Embedder & Searcher Tests
====================================
Tests for the embedding pipeline and search engine.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.parser import CodeUnit


class TestCodeEmbedder:
    """Tests for the code embedding pipeline."""

    @pytest.fixture
    def sample_unit(self):
        return CodeUnit(
            id="test001",
            name="sort_array",
            code=(
                "def sort_array(arr):\n"
                '    """Sort an array using quicksort."""\n'
                "    if len(arr) <= 1:\n"
                "        return arr\n"
                "    pivot = arr[len(arr) // 2]\n"
                "    left = [x for x in arr if x < pivot]\n"
                "    middle = [x for x in arr if x == pivot]\n"
                "    right = [x for x in arr if x > pivot]\n"
                "    return sort_array(left) + middle + sort_array(right)\n"
            ),
            language="python",
            file_path="utils.py",
            unit_type="function",
            start_line=1,
            end_line=9,
            loc=9,
            docstring="Sort an array using quicksort.",
            complexity=3,
            parameters=["arr"],
        )

    def test_embed_unit_dimension(self, sample_unit):
        """Test that embeddings have correct dimension."""
        from core.embedder import CodeEmbedder

        embedder = CodeEmbedder()
        embedding = embedder.embed_unit(sample_unit)

        assert isinstance(embedding, list)
        assert len(embedding) == embedder.get_dimension()
        assert all(isinstance(v, float) for v in embedding)

    def test_embed_multiple_units(self, sample_unit):
        """Test batch embedding."""
        from core.embedder import CodeEmbedder

        embedder = CodeEmbedder()
        units = [sample_unit, sample_unit]
        embeddings = embedder.embed_units(units)

        assert len(embeddings) == 2
        assert len(embeddings[0]) == embedder.get_dimension()

    def test_query_embedding(self):
        """Test query embedding."""
        from core.embedder import CodeEmbedder

        embedder = CodeEmbedder()
        embedding = embedder.embed_query("function to sort an array")

        assert isinstance(embedding, list)
        assert len(embedding) == embedder.get_dimension()

    def test_similarity_computation(self, sample_unit):
        """Test cosine similarity computation."""
        from core.embedder import CodeEmbedder

        embedder = CodeEmbedder()
        emb1 = embedder.embed_unit(sample_unit)
        emb2 = embedder.embed_unit(sample_unit)

        similarity = embedder.compute_similarity(emb1, emb2)
        assert 0.99 <= similarity <= 1.01  # Same input = ~1.0 similarity


class TestSparseVectorGenerator:
    """Tests for sparse vector generation."""

    @pytest.fixture
    def sample_units(self):
        return [
            CodeUnit(
                id=f"test{i:03d}",
                name=f"function_{i}",
                code=f"def function_{i}(x, y):\n    result = x + y\n    return result * {i}\n",
                language="python",
                file_path=f"file_{i}.py",
                unit_type="function",
                start_line=1,
                end_line=3,
                loc=3,
            )
            for i in range(10)
        ]

    def test_simple_sparse_generation(self):
        """Test hash-based sparse vector generation."""
        from core.sparse import SparseVectorGenerator

        gen = SparseVectorGenerator()
        indices, values = gen.generate_simple_sparse("def sort(arr): return sorted(arr)")

        assert isinstance(indices, list)
        assert isinstance(values, list)
        assert len(indices) == len(values)
        assert len(indices) > 0

    def test_fitted_sparse_generation(self, sample_units):
        """Test TF-IDF based sparse vector generation."""
        from core.sparse import SparseVectorGenerator

        gen = SparseVectorGenerator()
        gen.fit(sample_units)

        assert gen.is_fitted

        indices, values = gen.generate_sparse_vector(sample_units[0])
        assert isinstance(indices, list)
        assert isinstance(values, list)

    def test_query_sparse(self):
        """Test sparse query vector generation."""
        from core.sparse import SparseVectorGenerator

        gen = SparseVectorGenerator()
        indices, values = gen.query_sparse("sort array function")

        assert len(indices) == len(values)
        assert len(indices) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
