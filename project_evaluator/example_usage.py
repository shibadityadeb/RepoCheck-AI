"""
Example usage of the AI Project Auto-Evaluator as a library.

This demonstrates how to use the evaluator programmatically
instead of via the CLI.
"""

from pathlib import Path

from fetcher import fetch_github_repo
from scanner import scan_project
from analyzer import analyze_code_quality
from scorer import calculate_project_scores
from recommender import generate_improvement_roadmap
from reporter import generate_report


def evaluate_repository_example():
    """Example of evaluating a repository programmatically."""
    
    # Step 1: Fetch a repository
    repo_url = "https://github.com/psf/requests"  # Example: popular Python library
    print(f"Fetching repository: {repo_url}")
    
    repo_path = fetch_github_repo(repo_url, cache_dir=".cache/repos")
    
    if repo_path is None:
        print("Failed to fetch repository")
        return
    
    print(f"Repository cloned to: {repo_path}")
    
    # Step 2: Scan project structure
    print("\nScanning project structure...")
    project_stats = scan_project(repo_path)
    
    print(f"Found {project_stats.total_files} files")
    print(f"Total lines: {project_stats.total_lines}")
    print(f"Languages: {', '.join(project_stats.languages)}")
    
    # Step 3: Analyze code quality
    print("\nAnalyzing code quality...")
    quality_metrics = analyze_code_quality(repo_path)
    
    print(f"Average complexity: {quality_metrics.average_complexity:.2f}")
    print(f"Average maintainability: {quality_metrics.average_maintainability:.2f}")
    print(f"Files analyzed: {quality_metrics.files_analyzed}")
    
    # Step 4: Calculate scores
    print("\nCalculating scores...")
    scores = calculate_project_scores(project_stats, quality_metrics)
    
    print(f"Overall Score: {scores.overall_score}/100 (Grade: {scores.grade})")
    print(f"Code Quality: {scores.code_quality_score}/100")
    print(f"Architecture: {scores.architecture_score}/100")
    print(f"Maintainability: {scores.maintainability_score}/100")
    
    # Step 5: Generate recommendations
    print("\nGenerating recommendations...")
    recommendations = generate_improvement_roadmap(
        project_stats, quality_metrics, scores
    )
    
    print(f"Generated {len(recommendations)} recommendations")
    
    # Step 6: Generate report
    print("\nGenerating terminal report...")
    generate_report(
        repo_url=repo_url,
        project_stats=project_stats,
        quality_metrics=quality_metrics,
        scores=scores,
        recommendations=recommendations,
        format='terminal'
    )
    
    # Also generate JSON report
    print("\nGenerating JSON report...")
    json_report = generate_report(
        repo_url=repo_url,
        project_stats=project_stats,
        quality_metrics=quality_metrics,
        scores=scores,
        recommendations=recommendations,
        format='json',
        output_file=Path('example_report.json')
    )
    
    print("JSON report saved to: example_report.json")


def custom_scoring_example():
    """Example with custom configuration."""
    from scorer import ScoringEngine
    
    # Load custom config
    engine = ScoringEngine(config_path=Path('config.yaml'))
    
    # Use the engine for scoring...
    print("Custom scoring engine initialized with config.yaml")


def quick_evaluation_example():
    """Quick one-liner evaluation."""
    from fetcher import GitHubFetcher
    from scanner import ProjectScanner
    from analyzer import QualityAnalyzer
    from scorer import ScoringEngine
    from recommender import RecommendationEngine
    from reporter import ReportGenerator
    
    # One-stop shop evaluation
    repo_url = "https://github.com/pallets/flask"
    
    fetcher = GitHubFetcher()
    repo_path = fetcher.fetch(repo_url)
    
    if repo_path:
        scanner = ProjectScanner()
        analyzer = QualityAnalyzer()
        scorer = ScoringEngine()
        recommender = RecommendationEngine()
        reporter = ReportGenerator()
        
        stats = scanner.scan(repo_path)
        quality = analyzer.analyze_repository(repo_path)
        scores = scorer.calculate_scores(stats, quality)
        recs = recommender.generate_recommendations(stats, quality, scores)
        
        reporter.generate_terminal_report(repo_url, stats, quality, scores, recs)


if __name__ == '__main__':
    # Run the example
    evaluate_repository_example()
    
    # Uncomment to try other examples:
    # custom_scoring_example()
    # quick_evaluation_example()
