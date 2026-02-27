"""
CodeDNA — Repository Ingestion Script
======================================
Clones a GitHub repository and indexes all code into Endee.

Usage:
    python scripts/ingest_repo.py --repo https://github.com/pallets/flask
    python scripts/ingest_repo.py --path /path/to/local/repo --label v2.0
"""

import os
import sys
import json
import shutil
import logging
import argparse
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint

import config
from core.parser import CodeParser
from core.embedder import CodeEmbedder
from core.sparse import SparseVectorGenerator
from core.indexer import EndeeIndexer
from core.analyzer import CodeHealthAnalyzer
from core.searcher import CodeSearcher
from core.evolution import EvolutionTracker

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
console = Console()


def clone_repo(repo_url: str, target_dir: str) -> str:
    """Clone a git repository to a temporary directory."""
    try:
        import git

        console.print(f"[bold blue]📥 Cloning repository:[/] {repo_url}")
        repo = git.Repo.clone_from(repo_url, target_dir, depth=1)
        console.print(f"[green]✔ Cloned to {target_dir}[/]")
        return target_dir
    except ImportError:
        # Fallback to system git
        os.system(f"git clone --depth=1 {repo_url} {target_dir}")
        return target_dir
    except Exception as e:
        console.print(f"[red]✖ Failed to clone: {e}[/]")
        raise


def ingest(
    repo_path: str,
    label: str = "latest",
    skip_hybrid: bool = False,
    run_health: bool = True,
):
    """
    Main ingestion pipeline.

    1. Parse all source files
    2. Generate embeddings (dense + sparse)
    3. Create/connect to Endee indexes
    4. Upsert vectors to Endee
    5. Run health analysis
    6. Create evolution snapshot
    """

    console.rule("[bold cyan]🧬 CodeDNA — Codebase Ingestion Pipeline[/]")
    console.print(f"[bold]Repository:[/] {repo_path}")
    console.print(f"[bold]Label:[/] {label}")
    console.print()

    # ─── Step 1: Parse ───────────────────────────────────────────────
    console.print("[bold yellow]Step 1/5:[/] Parsing source files...")
    parser = CodeParser()
    units = parser.parse_directory(repo_path, recursive=True)

    if not units:
        console.print("[red]✖ No code units found! Check the repository path.[/]")
        return

    # Display parsing results
    table = Table(title="📊 Parsing Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    lang_counts = {}
    type_counts = {}
    for unit in units:
        lang_counts[unit.language] = lang_counts.get(unit.language, 0) + 1
        type_counts[unit.unit_type] = type_counts.get(unit.unit_type, 0) + 1

    table.add_row("Total Code Units", str(len(units)))
    table.add_row("Total LOC", str(sum(u.loc for u in units)))
    for lang, count in lang_counts.items():
        table.add_row(f"  {lang}", str(count))
    for utype, count in type_counts.items():
        table.add_row(f"  {utype}s", str(count))

    console.print(table)
    console.print()

    # ─── Step 2: Initialize Models ───────────────────────────────────
    console.print("[bold yellow]Step 2/5:[/] Loading embedding models...")

    embedder = CodeEmbedder()
    sparse_gen = SparseVectorGenerator()

    # Fit sparse vectorizer on corpus
    if len(units) > 5:
        sparse_gen.fit(units)

    console.print(f"[green]✔ Embedding dimension: {embedder.get_dimension()}[/]")
    console.print()

    # ─── Step 3: Setup Endee Indexes ─────────────────────────────────
    console.print("[bold yellow]Step 3/5:[/] Connecting to Endee & creating indexes...")

    indexer = EndeeIndexer(embedder=embedder, sparse_gen=sparse_gen)
    setup_results = indexer.setup_indexes()

    for idx_name, success in setup_results.items():
        status = "[green]✔[/]" if success else "[red]✖[/]"
        console.print(f"  {status} Index '{idx_name}'")
    console.print()

    # ─── Step 4: Upsert Vectors ──────────────────────────────────────
    console.print("[bold yellow]Step 4/5:[/] Indexing code vectors to Endee...")

    index_results = indexer.index_codebase(units)

    table = Table(title="📊 Indexing Results")
    table.add_column("Index", style="cyan")
    table.add_column("Vectors Upserted", style="green")
    for idx_name, count in index_results.items():
        table.add_row(idx_name, str(count))
    console.print(table)
    console.print()

    # ─── Step 5: Health Analysis & Evolution ─────────────────────────
    if run_health:
        console.print("[bold yellow]Step 5/5:[/] Running health analysis & evolution tracking...")

        searcher = CodeSearcher(embedder=embedder, sparse_gen=sparse_gen)
        analyzer = CodeHealthAnalyzer(searcher=searcher)
        report = analyzer.analyze_codebase(units)

        table = Table(title="🏥 Health Report")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        report_dict = report.to_dict()
        table.add_row("Overall Score", f"{report_dict['overall_score']}/100")
        table.add_row("Grade", f"[bold]{report_dict['grade']}[/]")
        table.add_row("Critical Violations", str(report_dict['critical_violations']))
        table.add_row("High Violations", str(report_dict['high_violations']))
        table.add_row("Medium Violations", str(report_dict['medium_violations']))
        table.add_row("Low Violations", str(report_dict['low_violations']))
        table.add_row("Avg Complexity", str(report_dict['metrics']['avg_complexity']))
        table.add_row("Documentation %", f"{report_dict['metrics']['documentation_ratio']}%")
        console.print(table)

        # Evolution snapshot
        tracker = EvolutionTracker(embedder=embedder)
        snapshot = tracker.create_snapshot(units, label=label)
        console.print(f"[green]✔ Evolution snapshot created: '{label}'[/]")

    console.rule("[bold green]🎉 Ingestion Complete![/]")
    console.print(
        f"\n[bold]Next steps:[/]\n"
        f"  1. Launch the dashboard: [cyan]streamlit run app/main.py[/]\n"
        f"  2. Search your code: Visit [cyan]http://localhost:8501[/]\n"
    )


def main():
    parser = argparse.ArgumentParser(
        description="🧬 CodeDNA — Ingest a repository into Endee"
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="GitHub repository URL to clone and ingest",
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Path to a local repository directory",
    )
    parser.add_argument(
        "--label",
        type=str,
        default="latest",
        help="Label for this snapshot (e.g., commit hash, version)",
    )
    parser.add_argument(
        "--skip-hybrid",
        action="store_true",
        help="Skip hybrid index(sparse + dense) ingestion",
    )
    parser.add_argument(
        "--no-health",
        action="store_true",
        help="Skip health analysis",
    )
    args = parser.parse_args()

    if not args.repo and not args.path:
        console.print("[red]Error: Provide either --repo URL or --path directory[/]")
        parser.print_help()
        sys.exit(1)

    repo_path = args.path
    if args.repo:
        tmp_dir = os.path.join(tempfile.gettempdir(), "codedna_repo")
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        repo_path = clone_repo(args.repo, tmp_dir)

    ingest(
        repo_path=repo_path,
        label=args.label,
        skip_hybrid=args.skip_hybrid,
        run_health=not args.no_health,
    )


if __name__ == "__main__":
    main()
