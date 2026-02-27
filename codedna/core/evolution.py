"""
CodeDNA Evolution Module
========================
Tracks how a codebase's vector "genome" evolves over time.
Analyzes architectural drift, code migration patterns, and
structural changes using Endee vector comparisons.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from core.parser import CodeUnit
from core.embedder import CodeEmbedder

logger = logging.getLogger(__name__)


@dataclass
class EvolutionSnapshot:
    """A point-in-time snapshot of the codebase's vector genome."""
    timestamp: str
    label: str  # e.g., commit hash, version tag
    total_units: int
    centroid: List[float]  # Average embedding vector
    spread: float  # Standard deviation of embeddings
    language_distribution: Dict[str, int] = field(default_factory=dict)
    type_distribution: Dict[str, int] = field(default_factory=dict)
    avg_complexity: float = 0.0
    total_loc: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "label": self.label,
            "total_units": self.total_units,
            "spread": round(self.spread, 4),
            "language_distribution": self.language_distribution,
            "type_distribution": self.type_distribution,
            "avg_complexity": round(self.avg_complexity, 2),
            "total_loc": self.total_loc,
        }


@dataclass
class DriftMetric:
    """Measures the drift between two snapshots."""
    from_label: str
    to_label: str
    centroid_drift: float  # Cosine distance between centroids
    spread_change: float  # Change in code diversity
    complexity_change: float
    loc_change: int
    new_patterns: int  # Number of new distinct code patterns
    removed_patterns: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_label,
            "to": self.to_label,
            "centroid_drift": round(self.centroid_drift, 4),
            "spread_change": round(self.spread_change, 4),
            "complexity_change": round(self.complexity_change, 2),
            "loc_change": self.loc_change,
            "new_patterns": self.new_patterns,
            "removed_patterns": self.removed_patterns,
        }


class EvolutionTracker:
    """
    Tracks the evolution of a codebase's vector genome over time.

    Creates snapshots of the codebase's embedding space and measures
    how it drifts over different versions/commits.
    """

    def __init__(self, embedder: CodeEmbedder):
        """
        Initialize the evolution tracker.

        Args:
            embedder: CodeEmbedder for generating embeddings.
        """
        self.embedder = embedder
        self.snapshots: List[EvolutionSnapshot] = []

    def create_snapshot(
        self,
        units: List[CodeUnit],
        label: str,
        timestamp: Optional[str] = None,
    ) -> EvolutionSnapshot:
        """
        Create a snapshot of the current codebase state.

        Args:
            units: Parsed code units representing the codebase.
            label: Label for this snapshot (e.g., commit hash, version).
            timestamp: ISO timestamp. Defaults to now.

        Returns:
            EvolutionSnapshot object.
        """
        if not timestamp:
            timestamp = datetime.now().isoformat()

        # Generate embeddings for all units
        embeddings = self.embedder.embed_units(units)
        embed_array = np.array(embeddings)

        # Calculate centroid (average embedding)
        centroid = np.mean(embed_array, axis=0).tolist()

        # Calculate spread (std dev of distances from centroid)
        centroid_array = np.array(centroid)
        distances = np.array(
            [
                np.linalg.norm(e - centroid_array)
                for e in embed_array
            ]
        )
        spread = float(np.std(distances))

        # Language & type distributions
        lang_dist = defaultdict(int)
        type_dist = defaultdict(int)
        total_complexity = 0
        total_loc = 0

        for unit in units:
            lang_dist[unit.language] += 1
            type_dist[unit.unit_type] += 1
            total_complexity += unit.complexity
            total_loc += unit.loc

        n = len(units) or 1

        snapshot = EvolutionSnapshot(
            timestamp=timestamp,
            label=label,
            total_units=len(units),
            centroid=centroid,
            spread=spread,
            language_distribution=dict(lang_dist),
            type_distribution=dict(type_dist),
            avg_complexity=total_complexity / n,
            total_loc=total_loc,
        )

        self.snapshots.append(snapshot)
        logger.info(
            f"Created snapshot '{label}': {len(units)} units, "
            f"spread={spread:.4f}"
        )

        return snapshot

    def measure_drift(
        self,
        snapshot_a: EvolutionSnapshot,
        snapshot_b: EvolutionSnapshot,
    ) -> DriftMetric:
        """
        Measure the drift between two snapshots.

        Args:
            snapshot_a: Earlier snapshot.
            snapshot_b: Later snapshot.

        Returns:
            DriftMetric with various drift measurements.
        """
        # Cosine distance between centroids
        a = np.array(snapshot_a.centroid)
        b = np.array(snapshot_b.centroid)
        cosine_sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        centroid_drift = 1.0 - cosine_sim

        # Spread change
        spread_change = snapshot_b.spread - snapshot_a.spread

        # Complexity change
        complexity_change = (
            snapshot_b.avg_complexity - snapshot_a.avg_complexity
        )

        # LOC change
        loc_change = snapshot_b.total_loc - snapshot_a.total_loc

        return DriftMetric(
            from_label=snapshot_a.label,
            to_label=snapshot_b.label,
            centroid_drift=float(centroid_drift),
            spread_change=float(spread_change),
            complexity_change=float(complexity_change),
            loc_change=loc_change,
            new_patterns=max(0, snapshot_b.total_units - snapshot_a.total_units),
            removed_patterns=max(0, snapshot_a.total_units - snapshot_b.total_units),
        )

    def get_evolution_timeline(self) -> List[Dict[str, Any]]:
        """
        Get the full evolution timeline with drift metrics.

        Returns:
            List of dicts with snapshot data and inter-snapshot drift.
        """
        timeline = []

        for i, snapshot in enumerate(self.snapshots):
            entry = snapshot.to_dict()

            if i > 0:
                drift = self.measure_drift(self.snapshots[i - 1], snapshot)
                entry["drift_from_previous"] = drift.to_dict()
            else:
                entry["drift_from_previous"] = None

            timeline.append(entry)

        return timeline

    def get_embedding_projections(
        self,
        units: List[CodeUnit],
        method: str = "tsne",
        n_components: int = 2,
    ) -> Dict[str, Any]:
        """
        Generate 2D/3D projections of code embeddings for visualization.

        Args:
            units: Code units to project.
            method: Projection method ("tsne" or "umap").
            n_components: 2 or 3 dimensions.

        Returns:
            Dict with projection coordinates, labels, and metadata.
        """
        embeddings = self.embedder.embed_units(units)
        embed_array = np.array(embeddings)

        if method == "umap":
            try:
                import umap
                reducer = umap.UMAP(
                    n_components=n_components,
                    random_state=42,
                    n_neighbors=min(15, len(units) - 1),
                    min_dist=0.1,
                )
                projected = reducer.fit_transform(embed_array)
            except ImportError:
                logger.warning("umap-learn not available, falling back to t-SNE")
                method = "tsne"

        if method == "tsne":
            from sklearn.manifold import TSNE
            perplexity = min(30, max(5, len(units) // 3))
            tsne = TSNE(
                n_components=n_components,
                random_state=42,
                perplexity=perplexity,
            )
            projected = tsne.fit_transform(embed_array)

        # Build result
        result = {
            "method": method,
            "n_components": n_components,
            "points": [],
        }

        for i, unit in enumerate(units):
            point = {
                "x": float(projected[i][0]),
                "y": float(projected[i][1]),
                "name": unit.name,
                "language": unit.language,
                "type": unit.unit_type,
                "file": unit.file_path,
                "complexity": unit.complexity,
                "loc": unit.loc,
            }
            if n_components == 3:
                point["z"] = float(projected[i][2])
            result["points"].append(point)

        return result
