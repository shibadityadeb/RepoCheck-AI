"""
Recommendation engine module for improvement suggestions.

Generates actionable, prioritized recommendations based on
project analysis results to improve code quality and architecture.
"""

from typing import List, Dict
from dataclasses import dataclass
from enum import Enum

from scanner.stats import ProjectStats
from analyzer.quality import QualityMetrics
from scorer.score import EvaluationScores
from utils.logger import get_logger


class Priority(Enum):
    """Recommendation priority levels."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class Recommendation:
    """
    Single improvement recommendation.
    
    Clear, actionable suggestion with priority and rationale.
    """
    title: str
    description: str
    priority: Priority
    category: str
    impact: str
    effort: str
    action_steps: List[str]


class RecommendationEngine:
    """
    Generates prioritized improvement recommendations.
    
    Implements Builder Pattern - constructs recommendations
    based on multiple analysis inputs.
    """
    
    def __init__(self):
        """Initialize the recommendation engine."""
        self.logger = get_logger()
    
    def generate_recommendations(self,
                                project_stats: ProjectStats,
                                quality_metrics: QualityMetrics,
                                scores: EvaluationScores) -> List[Recommendation]:
        """
        Generate comprehensive improvement recommendations.
        
        Args:
            project_stats: Project statistics
            quality_metrics: Quality analysis results
            scores: Evaluation scores
        
        Returns:
            List[Recommendation]: Prioritized recommendations
        
        Example:
            >>> engine = RecommendationEngine()
            >>> recommendations = engine.generate_recommendations(stats, quality, scores)
            >>> for rec in recommendations:
            ...     print(f"{rec.priority.value}: {rec.title}")
        """
        self.logger.info("Generating improvement recommendations...")
        
        recommendations = []
        
        # Code Quality Recommendations
        recommendations.extend(
            self._generate_code_quality_recommendations(quality_metrics, scores)
        )
        
        # Architecture Recommendations
        recommendations.extend(
            self._generate_architecture_recommendations(project_stats, scores)
        )
        
        # Maintainability Recommendations
        recommendations.extend(
            self._generate_maintainability_recommendations(
                project_stats, quality_metrics, scores
            )
        )
        
        # Testing Recommendations
        recommendations.extend(
            self._generate_testing_recommendations(project_stats, scores)
        )
        
        # ML/AI Recommendations
        recommendations.extend(
            self._generate_ml_ai_recommendations(project_stats, scores)
        )
        
        # Documentation Recommendations
        recommendations.extend(
            self._generate_documentation_recommendations(project_stats, scores)
        )
        
        # Sort by priority
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3
        }
        recommendations.sort(key=lambda r: priority_order[r.priority])
        
        self.logger.info(f"Generated {len(recommendations)} recommendations")
        
        return recommendations
    
    def _generate_code_quality_recommendations(self,
                                              quality_metrics: QualityMetrics,
                                              scores: EvaluationScores) -> List[Recommendation]:
        """Generate code quality improvement recommendations."""
        recommendations = []
        
        # High complexity
        if quality_metrics.average_complexity > 15:
            recommendations.append(Recommendation(
                title="Reduce Code Complexity",
                description=f"Average cyclomatic complexity is {quality_metrics.average_complexity:.1f}, "
                           "which is high. Complex code is harder to understand and maintain.",
                priority=Priority.CRITICAL,
                category="Code Quality",
                impact="High - improves maintainability and reduces bugs",
                effort="Medium - requires refactoring",
                action_steps=[
                    "Identify functions with complexity > 15",
                    "Break down complex functions into smaller ones",
                    "Use early returns to reduce nesting",
                    "Extract conditional logic into separate functions",
                    "Run complexity analysis: radon cc -a ."
                ]
            ))
        
        elif quality_metrics.average_complexity > 10:
            recommendations.append(Recommendation(
                title="Optimize Complex Functions",
                description=f"Average complexity is {quality_metrics.average_complexity:.1f}. "
                           "Consider simplifying the most complex functions.",
                priority=Priority.HIGH,
                category="Code Quality",
                impact="Medium - improves code readability",
                effort="Low to Medium",
                action_steps=[
                    "Review functions with complexity > 10",
                    "Refactor complex conditional statements",
                    "Consider using design patterns (Strategy, State)",
                    "Add inline comments for complex logic"
                ]
            ))
        
        # Many problematic files
        if len(quality_metrics.problematic_files) > 5:
            recommendations.append(Recommendation(
                title="Address Problematic Files",
                description=f"Found {len(quality_metrics.problematic_files)} files with quality issues. "
                           "These files need refactoring.",
                priority=Priority.HIGH,
                category="Code Quality",
                impact="High - prevents technical debt accumulation",
                effort="Medium to High",
                action_steps=[
                    "Review files flagged with quality issues",
                    "Prioritize files by complexity score",
                    "Refactor or split large files",
                    "Add unit tests before refactoring",
                    f"Focus on: {', '.join(quality_metrics.problematic_files[:3])}"
                ]
            ))
        
        # Low maintainability
        if scores.maintainability_score < 50:
            recommendations.append(Recommendation(
                title="Improve Code Maintainability",
                description="Maintainability index is low. Code may be difficult to update and extend.",
                priority=Priority.CRITICAL,
                category="Maintainability",
                impact="High - reduces long-term maintenance costs",
                effort="High - requires systematic refactoring",
                action_steps=[
                    "Add comprehensive docstrings and comments",
                    "Reduce code duplication (DRY principle)",
                    "Improve naming conventions",
                    "Simplify complex expressions",
                    "Run: radon mi -s ."
                ]
            ))
        
        return recommendations
    
    def _generate_architecture_recommendations(self,
                                              project_stats: ProjectStats,
                                              scores: EvaluationScores) -> List[Recommendation]:
        """Generate architecture improvement recommendations."""
        recommendations = []
        
        # Missing configuration
        if not project_stats.has_config:
            recommendations.append(Recommendation(
                title="Add Configuration Management",
                description="No configuration files detected. Externalize settings for flexibility.",
                priority=Priority.MEDIUM,
                category="Architecture",
                impact="Medium - improves deployment flexibility",
                effort="Low",
                action_steps=[
                    "Create config.yaml or .env file",
                    "Move hardcoded values to config",
                    "Use environment variables for secrets",
                    "Document configuration options"
                ]
            ))
        
        # No Docker
        if not project_stats.has_dockerfile:
            recommendations.append(Recommendation(
                title="Containerize Application",
                description="Add Docker support for consistent deployment environments.",
                priority=Priority.MEDIUM,
                category="Architecture",
                impact="High - improves deployment consistency",
                effort="Low to Medium",
                action_steps=[
                    "Create Dockerfile",
                    "Add docker-compose.yml for local development",
                    "Define environment variables",
                    "Document Docker commands in README"
                ]
            ))
        
        # No CI/CD
        if not project_stats.has_ci_cd:
            recommendations.append(Recommendation(
                title="Set Up CI/CD Pipeline",
                description="Automate testing and deployment with CI/CD.",
                priority=Priority.HIGH,
                category="Architecture",
                impact="High - improves code quality and deployment speed",
                effort="Medium",
                action_steps=[
                    "Set up GitHub Actions or GitLab CI",
                    "Add automated testing on pull requests",
                    "Configure linting and type checking",
                    "Add deployment automation",
                    "Example: .github/workflows/ci.yml"
                ]
            ))
        
        # Large file sizes
        if project_stats.average_file_size > 500:
            recommendations.append(Recommendation(
                title="Refactor Large Files",
                description=f"Average file size is {project_stats.average_file_size:.0f} lines. "
                           "Consider breaking down large modules.",
                priority=Priority.MEDIUM,
                category="Architecture",
                impact="Medium - improves code organization",
                effort="Medium",
                action_steps=[
                    "Identify files > 500 lines",
                    "Split into logical modules",
                    "Use clear module boundaries",
                    "Apply Single Responsibility Principle"
                ]
            ))
        
        return recommendations
    
    def _generate_maintainability_recommendations(self,
                                                 project_stats: ProjectStats,
                                                 quality_metrics: QualityMetrics,
                                                 scores: EvaluationScores) -> List[Recommendation]:
        """Generate maintainability recommendations."""
        recommendations = []
        
        # Large files
        if project_stats.largest_file_lines > 1000:
            recommendations.append(Recommendation(
                title="Break Down Large Files",
                description=f"Largest file has {project_stats.largest_file_lines} lines. "
                           "Large files are harder to maintain.",
                priority=Priority.HIGH,
                category="Maintainability",
                impact="High - improves code navigability",
                effort="Medium",
                action_steps=[
                    f"Refactor: {project_stats.largest_file}",
                    "Extract related functions into modules",
                    "Consider using classes for grouping",
                    "Maintain clear file boundaries"
                ]
            ))
        
        return recommendations
    
    def _generate_testing_recommendations(self,
                                        project_stats: ProjectStats,
                                        scores: EvaluationScores) -> List[Recommendation]:
        """Generate testing recommendations."""
        recommendations = []
        
        if not project_stats.has_tests:
            recommendations.append(Recommendation(
                title="Add Unit Tests",
                description="No tests detected. Testing is critical for code reliability.",
                priority=Priority.CRITICAL,
                category="Testing",
                impact="Very High - prevents bugs and regressions",
                effort="High - requires test implementation",
                action_steps=[
                    "Set up testing framework (pytest, unittest, jest)",
                    "Start with critical business logic",
                    "Aim for 70%+ code coverage",
                    "Add tests for edge cases",
                    "Integrate tests into CI pipeline"
                ]
            ))
        elif scores.test_coverage_score < 60:
            recommendations.append(Recommendation(
                title="Improve Test Coverage",
                description=f"Estimated test coverage is {scores.test_coverage_score:.0f}%. "
                           "Increase coverage for better reliability.",
                priority=Priority.HIGH,
                category="Testing",
                impact="High - improves code confidence",
                effort="Medium to High",
                action_steps=[
                    "Measure actual coverage: pytest --cov",
                    "Identify untested modules",
                    "Add tests for critical paths",
                    "Target 80%+ coverage",
                    "Add integration tests"
                ]
            ))
        
        return recommendations
    
    def _generate_ml_ai_recommendations(self,
                                       project_stats: ProjectStats,
                                       scores: EvaluationScores) -> List[Recommendation]:
        """Generate ML/AI specific recommendations."""
        recommendations = []
        
        if scores.ml_ai_readiness_score < 50 and 'Python' in project_stats.languages:
            recommendations.append(Recommendation(
                title="Enhance ML/AI Capabilities",
                description="Project shows potential for ML/AI but lacks standard ML infrastructure.",
                priority=Priority.LOW,
                category="ML/AI",
                impact="Variable - depends on project goals",
                effort="Medium to High",
                action_steps=[
                    "Add ML framework dependencies (if needed)",
                    "Create data/ and models/ directories",
                    "Add experiment tracking (MLflow, Weights & Biases)",
                    "Document model architecture and training",
                    "Version control datasets and models"
                ]
            ))
        
        return recommendations
    
    def _generate_documentation_recommendations(self,
                                               project_stats: ProjectStats,
                                               scores: EvaluationScores) -> List[Recommendation]:
        """Generate documentation recommendations."""
        recommendations = []
        
        if not project_stats.has_docs:
            recommendations.append(Recommendation(
                title="Add Project Documentation",
                description="No documentation found. Documentation is essential for collaboration.",
                priority=Priority.HIGH,
                category="Documentation",
                impact="High - improves onboarding and collaboration",
                effort="Low to Medium",
                action_steps=[
                    "Create comprehensive README.md",
                    "Document installation steps",
                    "Add usage examples",
                    "Document API/module interfaces",
                    "Add contributing guidelines",
                    "Consider adding docs/ folder with detailed docs"
                ]
            ))
        elif scores.documentation_score < 70:
            recommendations.append(Recommendation(
                title="Enhance Documentation",
                description="Documentation exists but could be improved.",
                priority=Priority.MEDIUM,
                category="Documentation",
                impact="Medium - improves code understanding",
                effort="Low",
                action_steps=[
                    "Add inline code comments for complex logic",
                    "Write docstrings for all public functions",
                    "Add architecture diagrams",
                    "Document design decisions",
                    "Keep README up to date"
                ]
            ))
        
        return recommendations


def generate_improvement_roadmap(project_stats: ProjectStats,
                                 quality_metrics: QualityMetrics,
                                 scores: EvaluationScores) -> List[Recommendation]:
    """
    Convenience function to generate improvement roadmap.
    
    Args:
        project_stats: Project statistics
        quality_metrics: Quality metrics
        scores: Evaluation scores
    
    Returns:
        List[Recommendation]: Prioritized recommendations
    
    Example:
        >>> recommendations = generate_improvement_roadmap(stats, quality, scores)
    """
    engine = RecommendationEngine()
    return engine.generate_recommendations(project_stats, quality_metrics, scores)
