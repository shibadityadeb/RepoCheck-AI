"""
Scoring engine module for project evaluation.

Combines metrics from scanner and analyzer to produce
weighted scores based on configurable rules.
"""

from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
import yaml

from scanner.stats import ProjectStats
from analyzer.quality import QualityMetrics
from utils.logger import get_logger


@dataclass
class EvaluationScores:
    """
    Complete evaluation scores for a project.
    
    All scores are on a 0-100 scale.
    """
    code_quality_score: float = 0.0
    architecture_score: float = 0.0
    maintainability_score: float = 0.0
    test_coverage_score: float = 0.0
    ml_ai_readiness_score: float = 0.0
    
    overall_score: float = 0.0
    grade: str = 'F'
    
    # Sub-scores for detailed breakdown
    complexity_score: float = 0.0
    documentation_score: float = 0.0
    structure_score: float = 0.0


class ScoringEngine:
    """
    Calculates weighted scores based on project metrics.
    
    Implements Strategy Pattern - scoring rules can be
    configured externally via YAML configuration.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the scoring engine.
        
        Args:
            config_path: Path to config.yaml file
        """
        self.logger = get_logger()
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """
        Load scoring configuration from YAML.
        
        Args:
            config_path: Path to config file
        
        Returns:
            Dict: Configuration dictionary
        """
        if config_path is None:
            # Use default config path
            config_path = Path(__file__).parent.parent / "config.yaml"
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            self.logger.warning(f"Failed to load config: {e}. Using defaults.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """
        Get default configuration if config file is not available.
        
        Returns:
            Dict: Default configuration
        """
        return {
            'scoring': {
                'weights': {
                    'code_quality': 0.30,
                    'architecture': 0.25,
                    'maintainability': 0.20,
                    'test_coverage': 0.15,
                    'ml_ai_readiness': 0.10
                },
                'thresholds': {
                    'complexity': {
                        'excellent': 5,
                        'good': 10,
                        'moderate': 15,
                        'poor': 20
                    },
                    'maintainability': {
                        'excellent': 80,
                        'good': 65,
                        'moderate': 50,
                        'poor': 25
                    }
                },
                'ml_ai_indicators': {
                    'frameworks': [
                        'tensorflow', 'pytorch', 'scikit-learn', 
                        'keras', 'numpy', 'pandas'
                    ]
                }
            }
        }
    
    def calculate_code_quality_score(self, quality_metrics: QualityMetrics) -> float:
        """
        Calculate code quality score (0-100).
        
        Based on cyclomatic complexity and other quality metrics.
        
        Args:
            quality_metrics: Quality analysis results
        
        Returns:
            float: Code quality score
        """
        if quality_metrics.files_analyzed == 0:
            return 50.0  # Neutral score if no files analyzed
        
        # Score based on average complexity
        complexity = quality_metrics.average_complexity
        thresholds = self.config['scoring']['thresholds']['complexity']
        
        if complexity <= thresholds['excellent']:
            complexity_score = 100
        elif complexity <= thresholds['good']:
            complexity_score = 85
        elif complexity <= thresholds['moderate']:
            complexity_score = 70
        elif complexity <= thresholds['poor']:
            complexity_score = 50
        else:
            complexity_score = max(20, 100 - (complexity * 2))
        
        # Penalize for very complex functions
        complexity_penalty = min(30, quality_metrics.very_complex_functions * 5)
        
        final_score = max(0, complexity_score - complexity_penalty)
        
        return round(final_score, 2)
    
    def calculate_architecture_score(self, project_stats: ProjectStats) -> float:
        """
        Calculate architecture score (0-100).
        
        Based on project structure, modularity, and organization.
        
        Args:
            project_stats: Project statistics
        
        Returns:
            float: Architecture score
        """
        score = 50.0  # Base score
        
        # Has modular structure (multiple folders)
        if len(project_stats.folders_by_type) > 0:
            score += 10
        
        # Has configuration files
        if project_stats.has_config:
            score += 10
        
        # Has proper requirements/dependencies
        if project_stats.has_requirements:
            score += 10
        
        # Has CI/CD setup
        if project_stats.has_ci_cd:
            score += 10
        
        # Has Docker setup
        if project_stats.has_dockerfile:
            score += 5
        
        # Average file size is reasonable (not too large)
        if project_stats.average_file_size < 300:
            score += 5
        elif project_stats.average_file_size > 1000:
            score -= 10
        
        return round(min(100, max(0, score)), 2)
    
    def calculate_maintainability_score(self, 
                                        quality_metrics: QualityMetrics,
                                        project_stats: ProjectStats) -> float:
        """
        Calculate maintainability score (0-100).
        
        Based on maintainability index, documentation, and code organization.
        
        Args:
            quality_metrics: Quality analysis results
            project_stats: Project statistics
        
        Returns:
            float: Maintainability score
        """
        score = 0.0
        
        # Base score from maintainability index
        if quality_metrics.average_maintainability > 0:
            score = quality_metrics.average_maintainability * 0.7
        else:
            score = 40  # Neutral if no data
        
        # Bonus for documentation
        if project_stats.has_docs:
            score += 15
        
        # Bonus for reasonable file sizes
        if project_stats.largest_file_lines < 500:
            score += 10
        elif project_stats.largest_file_lines > 2000:
            score -= 15
        
        # Penalty for too many problematic files
        if quality_metrics.files_analyzed > 0:
            problematic_ratio = len(quality_metrics.problematic_files) / quality_metrics.files_analyzed
            if problematic_ratio > 0.3:
                score -= 20
        
        return round(min(100, max(0, score)), 2)
    
    def calculate_test_coverage_score(self, project_stats: ProjectStats) -> float:
        """
        Estimate test coverage score (0-100).
        
        Based on presence of tests and test file ratio.
        
        Args:
            project_stats: Project statistics
        
        Returns:
            float: Test coverage score (estimated)
        """
        if not project_stats.has_tests:
            return 0.0
        
        score = 40.0  # Base score for having tests
        
        # Count test files
        test_files = sum(1 for ext in project_stats.files_by_extension.keys()
                        if 'test' in ext or ext in ['.test.py', '.spec.js'])
        
        if project_stats.total_files > 0:
            test_ratio = test_files / project_stats.total_files
            
            # Score based on test ratio
            if test_ratio >= 0.3:
                score = 90
            elif test_ratio >= 0.2:
                score = 75
            elif test_ratio >= 0.1:
                score = 60
        
        return round(score, 2)
    
    def calculate_ml_ai_readiness_score(self, project_stats: ProjectStats) -> float:
        """
        Calculate ML/AI readiness score (0-100).
        
        Based on ML frameworks, data handling, and ML-specific patterns.
        
        Args:
            project_stats: Project statistics
        
        Returns:
            float: ML/AI readiness score
        """
        score = 0.0
        
        ml_indicators = self.config['scoring']['ml_ai_indicators']['frameworks']
        
        # Check for Python (primary ML language)
        if 'Python' in project_stats.languages:
            score += 20
        
        # Check for requirements file (might contain ML frameworks)
        if project_stats.has_requirements:
            score += 20
        
        # Check for typical ML folder patterns
        ml_folders = ['model', 'models', 'data', 'dataset', 'train', 'inference']
        for folder_list in project_stats.folders_by_type.values():
            for folder in folder_list:
                if any(ml_folder in folder.lower() for ml_folder in ml_folders):
                    score += 15
                    break
        
        # Check for data files
        data_extensions = ['.csv', '.json', '.pkl', '.h5', '.npy']
        has_data = any(ext in project_stats.files_by_extension for ext in data_extensions)
        if has_data:
            score += 15
        
        # Check for Jupyter notebooks
        if '.ipynb' in project_stats.files_by_extension:
            score += 10
        
        return round(min(100, score), 2)
    
    def calculate_scores(self,
                        project_stats: ProjectStats,
                        quality_metrics: QualityMetrics) -> EvaluationScores:
        """
        Calculate all evaluation scores.
        
        Main scoring function that combines all metrics.
        
        Args:
            project_stats: Project statistics
            quality_metrics: Quality metrics
        
        Returns:
            EvaluationScores: Complete evaluation scores
        
        Example:
            >>> engine = ScoringEngine()
            >>> scores = engine.calculate_scores(stats, quality)
            >>> print(f"Overall Score: {scores.overall_score}")
        """
        self.logger.info("Calculating evaluation scores...")
        
        scores = EvaluationScores()
        
        # Calculate individual scores
        scores.code_quality_score = self.calculate_code_quality_score(quality_metrics)
        scores.architecture_score = self.calculate_architecture_score(project_stats)
        scores.maintainability_score = self.calculate_maintainability_score(
            quality_metrics, project_stats
        )
        scores.test_coverage_score = self.calculate_test_coverage_score(project_stats)
        scores.ml_ai_readiness_score = self.calculate_ml_ai_readiness_score(project_stats)
        
        # Calculate sub-scores
        scores.complexity_score = scores.code_quality_score
        scores.documentation_score = 100.0 if project_stats.has_docs else 30.0
        scores.structure_score = scores.architecture_score
        
        # Calculate weighted overall score
        weights = self.config['scoring']['weights']
        
        scores.overall_score = (
            scores.code_quality_score * weights['code_quality'] +
            scores.architecture_score * weights['architecture'] +
            scores.maintainability_score * weights['maintainability'] +
            scores.test_coverage_score * weights['test_coverage'] +
            scores.ml_ai_readiness_score * weights['ml_ai_readiness']
        )
        
        scores.overall_score = round(scores.overall_score, 2)
        
        # Assign grade
        scores.grade = self._calculate_grade(scores.overall_score)
        
        self.logger.info(f"Scoring complete. Overall: {scores.overall_score}/100 (Grade: {scores.grade})")
        
        return scores
    
    def _calculate_grade(self, score: float) -> str:
        """
        Convert numeric score to letter grade.
        
        Args:
            score: Numeric score (0-100)
        
        Returns:
            str: Letter grade (A-F)
        """
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'


def calculate_project_scores(project_stats: ProjectStats,
                            quality_metrics: QualityMetrics,
                            config_path: Optional[Path] = None) -> EvaluationScores:
    """
    Convenience function to calculate project scores.
    
    Args:
        project_stats: Project statistics
        quality_metrics: Quality metrics
        config_path: Optional config file path
    
    Returns:
        EvaluationScores: Complete evaluation scores
    
    Example:
        >>> scores = calculate_project_scores(stats, quality)
    """
    engine = ScoringEngine(config_path=config_path)
    return engine.calculate_scores(project_stats, quality_metrics)
