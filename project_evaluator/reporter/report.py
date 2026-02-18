"""
Report generation module with multiple output formats.

Generates beautiful terminal reports using Rich and
exports to JSON for programmatic consumption.
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.text import Text

from scanner.stats import ProjectStats
from analyzer.quality import QualityMetrics
from scorer.score import EvaluationScores
from recommender.suggest import Recommendation, Priority
from utils.logger import get_logger


class ReportGenerator:
    """
    Generates formatted evaluation reports.
    
    Implements Factory Pattern - creates different report
    formats from the same data.
    """
    
    def __init__(self):
        """Initialize the report generator."""
        self.console = Console()
        self.logger = get_logger()
    
    def generate_terminal_report(self,
                                repo_url: str,
                                project_stats: ProjectStats,
                                quality_metrics: QualityMetrics,
                                scores: EvaluationScores,
                                recommendations: List[Recommendation]) -> None:
        """
        Generate and display a beautiful terminal report using Rich.
        
        Args:
            repo_url: GitHub repository URL
            project_stats: Project statistics
            quality_metrics: Quality metrics
            scores: Evaluation scores
            recommendations: Improvement recommendations
        """
        self.console.clear()
        
        # Header
        self._print_header(repo_url, scores)
        
        # Overview Section
        self._print_overview(project_stats, quality_metrics)
        
        # Scores Section
        self._print_scores(scores)
        
        # Quality Details
        self._print_quality_details(quality_metrics)
        
        # Project Features
        self._print_project_features(project_stats)
        
        # Recommendations
        self._print_recommendations(recommendations)
        
        # Footer
        self._print_footer()
    
    def _print_header(self, repo_url: str, scores: EvaluationScores) -> None:
        """Print report header."""
        grade_color = self._get_grade_color(scores.grade)
        
        header = Text()
        header.append("🔍 AI PROJECT AUTO-EVALUATOR\n", style="bold cyan")
        header.append(f"Repository: {repo_url}\n", style="dim")
        header.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
        
        panel = Panel(
            header,
            title="[bold]Evaluation Report[/bold]",
            border_style="cyan",
            box=box.DOUBLE
        )
        self.console.print(panel)
        self.console.print()
    
    def _print_overview(self, project_stats: ProjectStats, quality_metrics: QualityMetrics) -> None:
        """Print project overview."""
        self.console.rule("[bold blue]📊 Project Overview[/bold blue]")
        self.console.print()
        
        table = Table(show_header=False, box=box.SIMPLE)
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Value", style="white")
        
        table.add_row("Total Files", f"{project_stats.total_files:,}")
        table.add_row("Total Lines of Code", f"{project_stats.total_lines:,}")
        table.add_row("Code Lines", f"{project_stats.total_code_lines:,}")
        table.add_row("Languages", ", ".join(sorted(project_stats.languages)))
        table.add_row("Files Analyzed", f"{quality_metrics.files_analyzed}")
        
        self.console.print(table)
        self.console.print()
    
    def _print_scores(self, scores: EvaluationScores) -> None:
        """Print evaluation scores."""
        self.console.rule("[bold blue]⭐ Evaluation Scores[/bold blue]")
        self.console.print()
        
        # Overall Score
        grade_color = self._get_grade_color(scores.grade)
        overall_panel = Panel(
            f"[bold {grade_color}]{scores.overall_score}/100[/bold {grade_color}] "
            f"[bold white](Grade: {scores.grade})[/bold white]",
            title="[bold]Overall Score[/bold]",
            border_style=grade_color,
            box=box.HEAVY
        )
        self.console.print(overall_panel)
        self.console.print()
        
        # Detailed Scores
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("Category", style="cyan", width=25)
        table.add_column("Score", justify="right", width=10)
        table.add_column("Rating", justify="center", width=20)
        
        score_data = [
            ("Code Quality", scores.code_quality_score),
            ("Architecture", scores.architecture_score),
            ("Maintainability", scores.maintainability_score),
            ("Test Coverage", scores.test_coverage_score),
            ("ML/AI Readiness", scores.ml_ai_readiness_score),
        ]
        
        for category, score in score_data:
            rating = self._get_rating_bar(score)
            color = self._get_score_color(score)
            table.add_row(
                category,
                f"[{color}]{score:.1f}/100[/{color}]",
                rating
            )
        
        self.console.print(table)
        self.console.print()
    
    def _print_quality_details(self, quality_metrics: QualityMetrics) -> None:
        """Print quality analysis details."""
        self.console.rule("[bold blue]🔬 Code Quality Analysis[/bold blue]")
        self.console.print()
        
        table = Table(box=box.SIMPLE, show_header=False)
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="white")
        
        table.add_row("Average Complexity", f"{quality_metrics.average_complexity:.2f}")
        table.add_row("Max Complexity", f"{quality_metrics.max_complexity:.2f}")
        table.add_row("Average Maintainability", f"{quality_metrics.average_maintainability:.2f}")
        table.add_row("Total Functions", f"{quality_metrics.total_functions}")
        table.add_row("Complex Functions (>10)", f"{quality_metrics.complex_functions}")
        table.add_row("Very Complex Functions (>20)", f"{quality_metrics.very_complex_functions}")
        
        self.console.print(table)
        self.console.print()
        
        # Complexity Distribution
        if quality_metrics.quality_distribution:
            dist = quality_metrics.quality_distribution
            self.console.print("[bold cyan]Complexity Distribution:[/bold cyan]")
            
            dist_table = Table(box=box.MINIMAL)
            dist_table.add_column("Level", style="cyan")
            dist_table.add_column("Count", justify="right")
            dist_table.add_column("Percentage", justify="right")
            
            total = sum(dist.values())
            for level, count in dist.items():
                pct = (count / total * 100) if total > 0 else 0
                dist_table.add_row(level.title(), str(count), f"{pct:.1f}%")
            
            self.console.print(dist_table)
            self.console.print()
    
    def _print_project_features(self, project_stats: ProjectStats) -> None:
        """Print project features checklist."""
        self.console.rule("[bold blue]✅ Project Features[/bold blue]")
        self.console.print()
        
        features = [
            ("Tests", project_stats.has_tests),
            ("Documentation", project_stats.has_docs),
            ("Configuration Files", project_stats.has_config),
            ("Requirements/Dependencies", project_stats.has_requirements),
            ("Docker Support", project_stats.has_dockerfile),
            ("CI/CD Pipeline", project_stats.has_ci_cd),
        ]
        
        for feature, present in features:
            icon = "✅" if present else "❌"
            color = "green" if present else "red"
            self.console.print(f"{icon} [{color}]{feature}[/{color}]")
        
        self.console.print()
    
    def _print_recommendations(self, recommendations: List[Recommendation]) -> None:
        """Print improvement recommendations."""
        self.console.rule("[bold blue]💡 Improvement Recommendations[/bold blue]")
        self.console.print()
        
        if not recommendations:
            self.console.print("[dim]No recommendations - excellent work![/dim]")
            return
        
        # Group by priority
        by_priority = {
            Priority.CRITICAL: [],
            Priority.HIGH: [],
            Priority.MEDIUM: [],
            Priority.LOW: []
        }
        
        for rec in recommendations:
            by_priority[rec.priority].append(rec)
        
        # Print each priority group
        for priority in [Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
            recs = by_priority[priority]
            if not recs:
                continue
            
            priority_color = self._get_priority_color(priority)
            self.console.print(f"\n[bold {priority_color}]{priority.value} Priority:[/bold {priority_color}]")
            
            for i, rec in enumerate(recs, 1):
                self.console.print(f"\n{i}. [bold]{rec.title}[/bold] [{rec.category}]")
                self.console.print(f"   [dim]{rec.description}[/dim]")
                self.console.print(f"   Impact: {rec.impact} | Effort: {rec.effort}")
                
                if rec.action_steps:
                    self.console.print("   [cyan]Action Steps:[/cyan]")
                    for step in rec.action_steps[:3]:  # Show first 3 steps
                        self.console.print(f"   • {step}")
        
        self.console.print()
    
    def _print_footer(self) -> None:
        """Print report footer."""
        self.console.print()
        self.console.rule()
        self.console.print(
            "[dim]Generated by AI Project Auto-Evaluator | "
            "https://github.com/yourname/project-evaluator[/dim]",
            justify="center"
        )
    
    def generate_json_report(self,
                            repo_url: str,
                            project_stats: ProjectStats,
                            quality_metrics: QualityMetrics,
                            scores: EvaluationScores,
                            recommendations: List[Recommendation],
                            output_file: Optional[Path] = None) -> str:
        """
        Generate JSON report for programmatic consumption.
        
        Args:
            repo_url: GitHub repository URL
            project_stats: Project statistics
            quality_metrics: Quality metrics
            scores: Evaluation scores
            recommendations: Improvement recommendations
            output_file: Optional output file path
        
        Returns:
            str: JSON string
        """
        report_data = {
            "metadata": {
                "repository": repo_url,
                "generated_at": datetime.now().isoformat(),
                "evaluator_version": "1.0.0"
            },
            "overview": {
                "total_files": project_stats.total_files,
                "total_lines": project_stats.total_lines,
                "code_lines": project_stats.total_code_lines,
                "languages": list(project_stats.languages),
                "files_analyzed": quality_metrics.files_analyzed
            },
            "scores": {
                "overall": scores.overall_score,
                "grade": scores.grade,
                "code_quality": scores.code_quality_score,
                "architecture": scores.architecture_score,
                "maintainability": scores.maintainability_score,
                "test_coverage": scores.test_coverage_score,
                "ml_ai_readiness": scores.ml_ai_readiness_score
            },
            "quality_metrics": {
                "average_complexity": quality_metrics.average_complexity,
                "max_complexity": quality_metrics.max_complexity,
                "average_maintainability": quality_metrics.average_maintainability,
                "total_functions": quality_metrics.total_functions,
                "complex_functions": quality_metrics.complex_functions,
                "distribution": quality_metrics.quality_distribution
            },
            "features": {
                "has_tests": project_stats.has_tests,
                "has_docs": project_stats.has_docs,
                "has_config": project_stats.has_config,
                "has_requirements": project_stats.has_requirements,
                "has_dockerfile": project_stats.has_dockerfile,
                "has_ci_cd": project_stats.has_ci_cd
            },
            "recommendations": [
                {
                    "title": rec.title,
                    "description": rec.description,
                    "priority": rec.priority.value,
                    "category": rec.category,
                    "impact": rec.impact,
                    "effort": rec.effort,
                    "action_steps": rec.action_steps
                }
                for rec in recommendations
            ]
        }
        
        json_str = json.dumps(report_data, indent=2)
        
        if output_file:
            output_file = Path(output_file)
            output_file.write_text(json_str)
            self.logger.info(f"JSON report saved to: {output_file}")
        
        return json_str
    
    # Helper methods for styling
    
    def _get_grade_color(self, grade: str) -> str:
        """Get color for grade."""
        colors = {
            'A': 'green',
            'B': 'cyan',
            'C': 'yellow',
            'D': 'orange',
            'F': 'red'
        }
        return colors.get(grade, 'white')
    
    def _get_score_color(self, score: float) -> str:
        """Get color for score value."""
        if score >= 80:
            return 'green'
        elif score >= 60:
            return 'yellow'
        else:
            return 'red'
    
    def _get_priority_color(self, priority: Priority) -> str:
        """Get color for priority."""
        colors = {
            Priority.CRITICAL: 'red',
            Priority.HIGH: 'orange',
            Priority.MEDIUM: 'yellow',
            Priority.LOW: 'cyan'
        }
        return colors.get(priority, 'white')
    
    def _get_rating_bar(self, score: float) -> str:
        """Generate visual rating bar."""
        filled = int(score / 10)
        empty = 10 - filled
        
        color = self._get_score_color(score)
        bar = f"[{color}]{'█' * filled}{'░' * empty}[/{color}]"
        return bar


def generate_report(repo_url: str,
                   project_stats: ProjectStats,
                   quality_metrics: QualityMetrics,
                   scores: EvaluationScores,
                   recommendations: List[Recommendation],
                   format: str = 'terminal',
                   output_file: Optional[Path] = None) -> Optional[str]:
    """
    Convenience function to generate reports.
    
    Args:
        repo_url: GitHub repository URL
        project_stats: Project statistics
        quality_metrics: Quality metrics
        scores: Evaluation scores
        recommendations: Recommendations
        format: Output format ('terminal' or 'json')
        output_file: Optional output file for JSON
    
    Returns:
        Optional[str]: JSON string if format is 'json', None otherwise
    
    Example:
        >>> generate_report(url, stats, quality, scores, recs, format='terminal')
    """
    generator = ReportGenerator()
    
    if format == 'terminal':
        generator.generate_terminal_report(
            repo_url, project_stats, quality_metrics, scores, recommendations
        )
        return None
    elif format == 'json':
        return generator.generate_json_report(
            repo_url, project_stats, quality_metrics, scores, recommendations, output_file
        )
    else:
        raise ValueError(f"Unknown format: {format}")
