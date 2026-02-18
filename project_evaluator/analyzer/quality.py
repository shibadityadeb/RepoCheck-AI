"""
Code quality analyzer module using Radon and Lizard.

Analyzes code complexity, maintainability index, and
provides quality metrics for source code evaluation.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from statistics import mean, median
import logging

from radon.complexity import cc_visit, cc_rank
from radon.metrics import mi_visit, mi_rank
from radon.raw import analyze
import lizard

from utils.logger import get_logger


@dataclass
class FileQuality:
    """Quality metrics for a single file."""
    file_path: str
    loc: int = 0
    complexity: float = 0.0
    maintainability: float = 0.0
    complexity_rank: str = 'A'
    maintainability_rank: str = 'A'
    functions_count: int = 0
    average_function_complexity: float = 0.0


@dataclass
class QualityMetrics:
    """
    Aggregate quality metrics for entire project.
    
    Provides comprehensive quality analysis results.
    """
    average_complexity: float = 0.0
    median_complexity: float = 0.0
    max_complexity: float = 0.0
    
    average_maintainability: float = 0.0
    median_maintainability: float = 0.0
    min_maintainability: float = 100.0
    
    total_functions: int = 0
    complex_functions: int = 0  # Complexity > 10
    very_complex_functions: int = 0  # Complexity > 20
    
    files_analyzed: int = 0
    problematic_files: List[str] = field(default_factory=list)
    
    quality_distribution: Dict[str, int] = field(default_factory=dict)
    
    file_metrics: List[FileQuality] = field(default_factory=list)


class QualityAnalyzer:
    """
    Analyzes code quality using multiple metrics.
    
    Implements Open/Closed Principle - extensible for new
    quality metrics without modifying existing code.
    """
    
    # Complexity thresholds
    COMPLEXITY_THRESHOLDS = {
        'simple': 5,
        'moderate': 10,
        'complex': 15,
        'very_complex': 20
    }
    
    # Maintainability thresholds
    MAINTAINABILITY_THRESHOLDS = {
        'excellent': 80,
        'good': 65,
        'moderate': 50,
        'poor': 25
    }
    
    def __init__(self):
        """Initialize the quality analyzer."""
        self.logger = get_logger()
    
    def analyze_python_file_radon(self, file_path: Path) -> Optional[FileQuality]:
        """
        Analyze a Python file using Radon.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            Optional[FileQuality]: Quality metrics or None if analysis fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Calculate cyclomatic complexity
            complexity_results = cc_visit(content)
            complexities = [func.complexity for func in complexity_results]
            
            avg_complexity = mean(complexities) if complexities else 0
            complexity_rank_val = cc_rank(avg_complexity)
            
            # Calculate maintainability index
            mi_score = mi_visit(content, multi=True)
            mi_value = mi_score if isinstance(mi_score, (int, float)) else 0
            mi_rank_val = mi_rank(mi_value)
            
            # Get LOC
            raw_metrics = analyze(content)
            loc = raw_metrics.loc
            
            return FileQuality(
                file_path=str(file_path),
                loc=loc,
                complexity=avg_complexity,
                maintainability=mi_value,
                complexity_rank=complexity_rank_val,
                maintainability_rank=mi_rank_val,
                functions_count=len(complexity_results),
                average_function_complexity=avg_complexity
            )
        
        except Exception as e:
            self.logger.debug(f"Radon analysis failed for {file_path}: {e}")
            return None
    
    def analyze_file_lizard(self, file_path: Path) -> Optional[Dict]:
        """
        Analyze a file using Lizard (supports multiple languages).
        
        Args:
            file_path: Path to source file
        
        Returns:
            Optional[Dict]: Analysis results or None if fails
        """
        try:
            analysis = lizard.analyze_file(str(file_path))
            
            if not analysis.function_list:
                return None
            
            complexities = [func.cyclomatic_complexity for func in analysis.function_list]
            
            return {
                'avg_complexity': mean(complexities) if complexities else 0,
                'max_complexity': max(complexities) if complexities else 0,
                'functions_count': len(analysis.function_list),
                'nloc': analysis.nloc
            }
        
        except Exception as e:
            self.logger.debug(f"Lizard analysis failed for {file_path}: {e}")
            return None
    
    def analyze_file(self, file_path: Path) -> Optional[FileQuality]:
        """
        Analyze a single file (routes to appropriate analyzer).
        
        Args:
            file_path: Path to source file
        
        Returns:
            Optional[FileQuality]: Quality metrics
        """
        ext = file_path.suffix.lower()
        
        # Use Radon for Python files
        if ext == '.py':
            return self.analyze_python_file_radon(file_path)
        
        # Use Lizard for other languages
        else:
            lizard_result = self.analyze_file_lizard(file_path)
            if lizard_result:
                return FileQuality(
                    file_path=str(file_path),
                    loc=lizard_result['nloc'],
                    complexity=lizard_result['avg_complexity'],
                    functions_count=lizard_result['functions_count'],
                    average_function_complexity=lizard_result['avg_complexity']
                )
        
        return None
    
    def analyze_repository(self, repo_path: Path, 
                          max_files: int = 1000) -> QualityMetrics:
        """
        Analyze code quality across an entire repository.
        
        Args:
            repo_path: Path to repository
            max_files: Maximum files to analyze (safety limit)
        
        Returns:
            QualityMetrics: Comprehensive quality analysis
        
        Example:
            >>> analyzer = QualityAnalyzer()
            >>> metrics = analyzer.analyze_repository(Path("/path/to/repo"))
            >>> print(f"Average complexity: {metrics.average_complexity}")
        """
        self.logger.info(f"Analyzing code quality in: {repo_path}")
        
        metrics = QualityMetrics()
        
        # Lists for calculating aggregate statistics
        all_complexities = []
        all_maintainability = []
        
        # Find source files
        source_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', 
                           '.go', '.rs', '.rb', '.php']
        
        files_processed = 0
        
        for ext in source_extensions:
            if files_processed >= max_files:
                break
            
            for file_path in repo_path.rglob(f'*{ext}'):
                if files_processed >= max_files:
                    break
                
                # Skip test files for quality analysis
                if 'test' in str(file_path).lower():
                    continue
                
                file_quality = self.analyze_file(file_path)
                
                if file_quality:
                    metrics.file_metrics.append(file_quality)
                    files_processed += 1
                    
                    # Collect for aggregates
                    if file_quality.complexity > 0:
                        all_complexities.append(file_quality.complexity)
                    
                    if file_quality.maintainability > 0:
                        all_maintainability.append(file_quality.maintainability)
                    
                    # Count complex functions
                    metrics.total_functions += file_quality.functions_count
                    if file_quality.complexity > self.COMPLEXITY_THRESHOLDS['moderate']:
                        metrics.complex_functions += 1
                    if file_quality.complexity > self.COMPLEXITY_THRESHOLDS['very_complex']:
                        metrics.very_complex_functions += 1
                    
                    # Track problematic files
                    if file_quality.complexity > self.COMPLEXITY_THRESHOLDS['complex'] or \
                       file_quality.maintainability < self.MAINTAINABILITY_THRESHOLDS['moderate']:
                        rel_path = Path(file_quality.file_path).relative_to(repo_path)
                        metrics.problematic_files.append(str(rel_path))
        
        # Calculate aggregate statistics
        if all_complexities:
            metrics.average_complexity = mean(all_complexities)
            metrics.median_complexity = median(all_complexities)
            metrics.max_complexity = max(all_complexities)
        
        if all_maintainability:
            metrics.average_maintainability = mean(all_maintainability)
            metrics.median_maintainability = median(all_maintainability)
            metrics.min_maintainability = min(all_maintainability)
        
        metrics.files_analyzed = len(metrics.file_metrics)
        
        # Calculate quality distribution
        metrics.quality_distribution = self._calculate_distribution(metrics.file_metrics)
        
        self.logger.info(f"Quality analysis complete: {metrics.files_analyzed} files analyzed")
        
        return metrics
    
    def _calculate_distribution(self, file_metrics: List[FileQuality]) -> Dict[str, int]:
        """
        Calculate distribution of files by complexity level.
        
        Args:
            file_metrics: List of file quality metrics
        
        Returns:
            Dict[str, int]: Distribution counts
        """
        distribution = {
            'simple': 0,
            'moderate': 0,
            'complex': 0,
            'very_complex': 0
        }
        
        for fm in file_metrics:
            if fm.complexity <= self.COMPLEXITY_THRESHOLDS['simple']:
                distribution['simple'] += 1
            elif fm.complexity <= self.COMPLEXITY_THRESHOLDS['moderate']:
                distribution['moderate'] += 1
            elif fm.complexity <= self.COMPLEXITY_THRESHOLDS['complex']:
                distribution['complex'] += 1
            else:
                distribution['very_complex'] += 1
        
        return distribution
    
    def get_quality_grade(self, metrics: QualityMetrics) -> str:
        """
        Calculate overall quality grade (A-F).
        
        Args:
            metrics: Quality metrics
        
        Returns:
            str: Grade letter
        """
        # Combined scoring based on complexity and maintainability
        complexity_score = 0
        if metrics.average_complexity <= 5:
            complexity_score = 100
        elif metrics.average_complexity <= 10:
            complexity_score = 80
        elif metrics.average_complexity <= 15:
            complexity_score = 60
        elif metrics.average_complexity <= 20:
            complexity_score = 40
        else:
            complexity_score = 20
        
        maintainability_score = metrics.average_maintainability
        
        # Weighted average
        overall_score = (complexity_score * 0.5) + (maintainability_score * 0.5)
        
        if overall_score >= 90:
            return 'A'
        elif overall_score >= 80:
            return 'B'
        elif overall_score >= 70:
            return 'C'
        elif overall_score >= 60:
            return 'D'
        else:
            return 'F'


def analyze_code_quality(repo_path: Path) -> QualityMetrics:
    """
    Convenience function to analyze code quality.
    
    Args:
        repo_path: Path to repository
    
    Returns:
        QualityMetrics: Quality analysis results
    
    Example:
        >>> metrics = analyze_code_quality(Path("/path/to/repo"))
    """
    analyzer = QualityAnalyzer()
    return analyzer.analyze_repository(repo_path)
