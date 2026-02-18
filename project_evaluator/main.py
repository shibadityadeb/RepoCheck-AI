#!/usr/bin/env python3
"""
AI Project Auto-Evaluator - Main CLI Entry Point

A production-quality tool for automated GitHub repository evaluation,
providing comprehensive code quality, architecture, and maintainability analysis.

Usage:
    python main.py --repo https://github.com/user/repo
    python main.py --repo https://github.com/user/repo --format json
    python main.py --repo https://github.com/user/repo --format json --output report.json
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
import logging

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from fetcher.github import GitHubFetcher
from scanner.stats import ProjectScanner
from analyzer.quality import QualityAnalyzer
from scorer.score import ScoringEngine
from recommender.suggest import RecommendationEngine
from reporter.report import ReportGenerator
from utils.logger import get_logger


class ProjectEvaluator:
    """
    Main orchestrator for project evaluation pipeline.
    
    Implements Facade Pattern - provides simple interface
    to complex subsystems.
    """
    
    def __init__(self, 
                 config_path: Optional[Path] = None,
                 cache_dir: str = ".cache/repos",
                 verbose: bool = False):
        """
        Initialize the project evaluator.
        
        Args:
            config_path: Path to config.yaml
            cache_dir: Cache directory for repositories
            verbose: Enable verbose logging
        """
        # Set up logging
        log_level = logging.DEBUG if verbose else logging.INFO
        self.logger = get_logger(level=log_level)
        
        # Initialize components
        self.fetcher = GitHubFetcher(cache_dir=cache_dir)
        self.scanner = ProjectScanner()
        self.analyzer = QualityAnalyzer()
        self.scorer = ScoringEngine(config_path=config_path)
        self.recommender = RecommendationEngine()
        self.reporter = ReportGenerator()
        
        self.console = Console()
    
    def evaluate(self, 
                repo_url: str,
                force_refresh: bool = False,
                output_format: str = 'terminal',
                output_file: Optional[Path] = None) -> bool:
        """
        Run complete evaluation pipeline for a repository.
        
        Args:
            repo_url: GitHub repository URL
            force_refresh: Force fresh clone (ignore cache)
            output_format: Output format ('terminal' or 'json')
            output_file: Optional output file path for JSON
        
        Returns:
            bool: True if successful, False otherwise
        
        Example:
            >>> evaluator = ProjectEvaluator()
            >>> evaluator.evaluate("https://github.com/user/repo")
        """
        try:
            # Display welcome message
            self._display_welcome()
            
            # Step 1: Fetch repository
            self.logger.info(f"Fetching repository: {repo_url}")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Cloning repository...", total=None)
                repo_path = self.fetcher.fetch(repo_url, force_refresh=force_refresh)
            
            if repo_path is None:
                self.logger.error("Failed to fetch repository")
                return False
            
            self.logger.info(f"Repository available at: {repo_path}")
            
            # Step 2: Scan project structure
            self.logger.info("Scanning project structure...")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Analyzing project structure...", total=None)
                project_stats = self.scanner.scan(repo_path)
            
            # Step 3: Analyze code quality
            self.logger.info("Analyzing code quality...")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Evaluating code quality...", total=None)
                quality_metrics = self.analyzer.analyze_repository(repo_path)
            
            # Step 4: Calculate scores
            self.logger.info("Calculating scores...")
            scores = self.scorer.calculate_scores(project_stats, quality_metrics)
            
            # Step 5: Generate recommendations
            self.logger.info("Generating recommendations...")
            recommendations = self.recommender.generate_recommendations(
                project_stats, quality_metrics, scores
            )
            
            # Step 6: Generate report
            self.logger.info("Generating report...")
            
            if output_format == 'terminal':
                self.reporter.generate_terminal_report(
                    repo_url, project_stats, quality_metrics, scores, recommendations
                )
            elif output_format == 'json':
                json_output = self.reporter.generate_json_report(
                    repo_url, project_stats, quality_metrics, 
                    scores, recommendations, output_file
                )
                
                if output_file is None:
                    # Print to console
                    self.console.print(json_output)
            else:
                self.logger.error(f"Unknown output format: {output_format}")
                return False
            
            return True
        
        except KeyboardInterrupt:
            self.logger.warning("\nEvaluation interrupted by user")
            return False
        except Exception as e:
            self.logger.error(f"Evaluation failed: {e}", exc_info=True)
            return False
    
    def _display_welcome(self) -> None:
        """Display welcome message."""
        welcome_text = """
[bold cyan]AI Project Auto-Evaluator[/bold cyan]
[dim]Automated engineering-style evaluation of GitHub repositories[/dim]

Analyzing:
• Code Quality & Complexity
• Architecture & Structure
• Maintainability Index
• Test Coverage
• ML/AI Readiness
        """
        
        panel = Panel(welcome_text.strip(), 
                     title="[bold]Welcome[/bold]",
                     border_style="cyan")
        self.console.print(panel)
        self.console.print()


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="AI Project Auto-Evaluator - Analyze GitHub repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --repo https://github.com/user/repo
  %(prog)s --repo https://github.com/user/repo --format json
  %(prog)s --repo https://github.com/user/repo --format json --output report.json
  %(prog)s --repo https://github.com/user/repo --force-refresh --verbose
        """
    )
    
    parser.add_argument(
        '--repo',
        type=str,
        required=True,
        help='GitHub repository URL to evaluate'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['terminal', 'json'],
        default='terminal',
        help='Output format (default: terminal)'
    )
    
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file path (for JSON format)'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to custom config.yaml file'
    )
    
    parser.add_argument(
        '--cache-dir',
        type=str,
        default='.cache/repos',
        help='Directory for caching cloned repositories (default: .cache/repos)'
    )
    
    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='Force fresh clone, ignore cache'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Parse arguments
    args = parse_arguments()
    
    # Create evaluator
    evaluator = ProjectEvaluator(
        config_path=args.config,
        cache_dir=args.cache_dir,
        verbose=args.verbose
    )
    
    # Run evaluation
    success = evaluator.evaluate(
        repo_url=args.repo,
        force_refresh=args.force_refresh,
        output_format=args.format,
        output_file=args.output
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
