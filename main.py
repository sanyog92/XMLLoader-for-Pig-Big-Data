#!/usr/bin/env python3
"""
FIFA 2026 Shorts Bot — Main Entry Point

Usage:
  python main.py               # Start the scheduler (runs indefinitely)
  python main.py --once        # Run the pipeline once and exit
  python main.py --setup       # Interactive first-time setup wizard
  python main.py --dry-run     # Run pipeline without uploading
"""

import os
import sys
import click
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import logger


@click.command()
@click.option("--once", is_flag=True, help="Run pipeline once and exit.")
@click.option("--dry-run", is_flag=True, help="Run without uploading.")
@click.option("--setup", is_flag=True, help="Run interactive setup wizard.")
@click.option("--crawl-only", is_flag=True, help="Discover & print candidates (no download/edit/upload).")
def main(once: bool, dry_run: bool, setup: bool, crawl_only: bool) -> None:
    if setup:
        _run_setup()
        return

    if dry_run:
        os.environ["DRY_RUN"] = "true"
        logger.info("DRY RUN mode enabled — no uploads will be made.")

    from pipeline import Pipeline
    pipeline = Pipeline()

    if crawl_only:
        _crawl_only(pipeline)
        return

    if once:
        logger.info("Running pipeline once...")
        pipeline.run()
        return

    # Default: start scheduler
    from scheduler.job_scheduler import BotScheduler
    scheduler = BotScheduler(
        pipeline_fn=pipeline.run,
        cleanup_fn=pipeline.cleanup_old_files,
    )

    # Run once immediately on startup, then on interval
    logger.info("Running pipeline immediately on startup...")
    try:
        pipeline.run()
    except Exception as exc:
        logger.error(f"Initial pipeline run failed: {exc}")

    scheduler.start()


def _crawl_only(pipeline) -> None:
    from rich.table import Table
    from rich.console import Console
    from crawler.youtube_crawler import YouTubeCrawler

    console = Console()
    logger.info("Crawl-only mode — discovering content...")
    crawler = YouTubeCrawler()
    candidates = crawler.discover()

    table = Table(title=f"Discovered {len(candidates)} Candidates", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", max_width=50)
    table.add_column("Channel", max_width=20)
    table.add_column("Duration", justify="right")
    table.add_column("Views", justify="right")
    table.add_column("Score", justify="right")

    for i, v in enumerate(candidates[:30], 1):
        from utils.helpers import format_duration
        table.add_row(
            str(i),
            v.title[:50],
            v.channel[:20],
            format_duration(v.duration),
            f"{v.view_count:,}",
            f"{v.viral_score:.3f}",
        )

    console.print(table)


def _run_setup() -> None:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    console = Console()

    console.print("\n[bold green]FIFA 2026 Shorts Bot — Setup Wizard[/bold green]\n")

    env_path = Path(".env")
    example_path = Path(".env.example")

    if not env_path.exists() and example_path.exists():
        import shutil
        shutil.copy(example_path, env_path)
        console.print("[yellow].env file created from .env.example[/yellow]")

    console.print("\nPlease edit [bold].env[/bold] and fill in your credentials:")
    console.print("  • YOUTUBE_CLIENT_ID / CLIENT_SECRET / REFRESH_TOKEN")
    console.print("  • INSTAGRAM_ACCESS_TOKEN / BUSINESS_ACCOUNT_ID")
    console.print("  • OPENAI_API_KEY (optional, for AI captions)")
    console.print("\nThen run:  [bold cyan]python main.py --once[/bold cyan]  to test\n")


if __name__ == "__main__":
    main()
