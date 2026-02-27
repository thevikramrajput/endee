"""
CodeDNA — Seed Anti-Patterns Script
====================================
Seeds the Endee anti-patterns index with known code smells and bad practices.

Usage:
    python scripts/seed_patterns.py
"""

import os
import sys
import json
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rich.console import Console
from rich.table import Table

import config
from core.embedder import CodeEmbedder
from core.indexer import EndeeIndexer

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
console = Console()


def seed_antipatterns():
    """Load anti-patterns from JSON and upsert to Endee."""
    console.rule("[bold cyan]🧬 CodeDNA — Seeding Anti-Patterns[/]")

    # Load patterns
    patterns_file = os.path.join(config.PATTERNS_DIR, "anti_patterns.json")
    if not os.path.exists(patterns_file):
        console.print(f"[red]✖ Anti-patterns file not found: {patterns_file}[/]")
        return

    with open(patterns_file, "r") as f:
        patterns = json.load(f)

    console.print(f"[bold]Loaded {len(patterns)} anti-patterns[/]")

    # Initialize embedder and indexer
    embedder = CodeEmbedder()
    indexer = EndeeIndexer(embedder=embedder)

    # Setup indexes (ensures anti-pattern index exists)
    indexer.setup_indexes()

    # Upsert patterns
    count = indexer.upsert_antipatterns(patterns)

    # Display results
    table = Table(title="🔍 Seeded Anti-Patterns")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="yellow")
    table.add_column("Category", style="green")
    table.add_column("Severity", style="red")

    for p in patterns:
        table.add_row(p["id"], p["name"], p["category"], p["severity"])

    console.print(table)
    console.print(f"\n[green]✔ Successfully seeded {count} anti-patterns to Endee[/]")


if __name__ == "__main__":
    seed_antipatterns()
