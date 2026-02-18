"""
Project scanner module for code statistics and structure analysis.

Analyzes repository structure, counts files, lines of code,
and detects programming languages and project patterns.
"""

import os
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict
from dataclasses import dataclass, field
import logging

import pathspec

from utils.logger import get_logger


@dataclass
class ProjectStats:
    """
    Data class to hold project statistics.
    
    Uses dataclass for clean, immutable data structure.
    """
    total_files: int = 0
    total_lines: int = 0
    total_code_lines: int = 0
    total_blank_lines: int = 0
    total_comment_lines: int = 0
    
    files_by_extension: Dict[str, int] = field(default_factory=dict)
    lines_by_extension: Dict[str, int] = field(default_factory=dict)
    
    languages: Set[str] = field(default_factory=set)
    
    has_tests: bool = False
    has_docs: bool = False
    has_config: bool = False
    has_requirements: bool = False
    has_dockerfile: bool = False
    has_ci_cd: bool = False
    
    folders_by_type: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    
    average_file_size: float = 0.0
    largest_file: Optional[str] = None
    largest_file_lines: int = 0


class ProjectScanner:
    """
    Scans and analyzes project structure and statistics.
    
    Implements separation of concerns - focused solely on
    gathering project metrics and structure information.
    """
    
    # Language detection based on file extensions
    LANGUAGE_MAP = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.r': 'R',
        '.m': 'MATLAB',
        '.sh': 'Shell',
        '.sql': 'SQL',
        '.html': 'HTML',
        '.css': 'CSS',
        '.jsx': 'React',
        '.tsx': 'React TypeScript',
        '.vue': 'Vue',
    }
    
    # Comment patterns for different languages
    COMMENT_PATTERNS = {
        'Python': ['#', '"""', "'''"],
        'JavaScript': ['//', '/*', '*/'],
        'TypeScript': ['//', '/*', '*/'],
        'Java': ['//', '/*', '*/'],
        'C++': ['//', '/*', '*/'],
        'C': ['//', '/*', '*/'],
        'Go': ['//', '/*', '*/'],
        'Rust': ['//', '/*', '*/'],
    }
    
    def __init__(self, ignore_patterns: Optional[List[str]] = None):
        """
        Initialize the project scanner.
        
        Args:
            ignore_patterns: List of gitignore-style patterns to ignore
        """
        self.logger = get_logger()
        
        # Default ignore patterns
        default_ignores = [
            '__pycache__',
            '*.pyc',
            '.git',
            '.venv',
            'venv',
            'env',
            'node_modules',
            '.pytest_cache',
            '.mypy_cache',
            '*.egg-info',
            'dist',
            'build',
            '.DS_Store',
            '*.min.js',
            '*.min.css',
        ]
        
        patterns = ignore_patterns or default_ignores
        self.spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    
    def should_ignore(self, path: Path, base_path: Path) -> bool:
        """
        Check if a path should be ignored based on patterns.
        
        Args:
            path: Path to check
            base_path: Base directory path
        
        Returns:
            bool: True if should be ignored
        """
        try:
            relative_path = path.relative_to(base_path)
            return self.spec.match_file(str(relative_path))
        except ValueError:
            return False
    
    def count_lines(self, file_path: Path) -> Dict[str, int]:
        """
        Count different types of lines in a file.
        
        Args:
            file_path: Path to file
        
        Returns:
            Dict with counts for total, code, blank, and comment lines
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            total = len(lines)
            blank = sum(1 for line in lines if not line.strip())
            
            # Simple comment detection (can be enhanced)
            comment = 0
            in_multiline = False
            
            for line in lines:
                stripped = line.strip()
                
                # Check for common comment patterns
                if stripped.startswith('#') or \
                   stripped.startswith('//') or \
                   stripped.startswith('/*') or \
                   stripped.startswith('*') or \
                   stripped.startswith('"""') or \
                   stripped.startswith("'''"):
                    comment += 1
                elif '"""' in stripped or "'''" in stripped or '/*' in stripped:
                    in_multiline = not in_multiline
                    comment += 1
                elif in_multiline:
                    comment += 1
            
            code = total - blank - comment
            
            return {
                'total': total,
                'code': max(0, code),
                'blank': blank,
                'comment': comment
            }
        
        except Exception as e:
            self.logger.debug(f"Error counting lines in {file_path}: {e}")
            return {'total': 0, 'code': 0, 'blank': 0, 'comment': 0}
    
    def detect_project_features(self, repo_path: Path, stats: ProjectStats) -> None:
        """
        Detect common project features (tests, docs, configs, etc.).
        
        Args:
            repo_path: Repository path
            stats: ProjectStats object to update
        """
        # Check for test directories/files
        test_indicators = ['test', 'tests', 'spec', '__tests__']
        for item in repo_path.rglob('*'):
            if item.is_dir() and any(ind in item.name.lower() for ind in test_indicators):
                stats.has_tests = True
                stats.folders_by_type['tests'].append(str(item.relative_to(repo_path)))
        
        # Check for common test files
        for pattern in ['test_*.py', '*_test.py', '*.test.js', '*.spec.js']:
            if list(repo_path.rglob(pattern)):
                stats.has_tests = True
                break
        
        # Check for documentation
        doc_indicators = ['readme.md', 'readme.rst', 'docs', 'documentation']
        for indicator in doc_indicators:
            if list(repo_path.rglob(indicator)):
                stats.has_docs = True
                break
        
        # Check for configuration files
        config_files = ['config.yaml', 'config.yml', 'config.json', 'setup.py', 
                       'pyproject.toml', 'package.json']
        for config_file in config_files:
            if (repo_path / config_file).exists():
                stats.has_config = True
                break
        
        # Check for requirements files
        req_files = ['requirements.txt', 'requirements.in', 'Pipfile', 
                    'environment.yml', 'package.json']
        for req_file in req_files:
            if (repo_path / req_file).exists():
                stats.has_requirements = True
                break
        
        # Check for Docker
        if (repo_path / 'Dockerfile').exists() or (repo_path / 'docker-compose.yml').exists():
            stats.has_dockerfile = True
        
        # Check for CI/CD
        ci_indicators = ['.github/workflows', '.gitlab-ci.yml', '.travis.yml', 
                        'Jenkinsfile', '.circleci']
        for indicator in ci_indicators:
            if (repo_path / indicator).exists():
                stats.has_ci_cd = True
                break
    
    def scan(self, repo_path: Path) -> ProjectStats:
        """
        Scan a repository and gather comprehensive statistics.
        
        Args:
            repo_path: Path to repository
        
        Returns:
            ProjectStats: Complete project statistics
        
        Example:
            >>> scanner = ProjectScanner()
            >>> stats = scanner.scan(Path("/path/to/repo"))
            >>> print(f"Total files: {stats.total_files}")
        """
        self.logger.info(f"Scanning repository: {repo_path}")
        
        stats = ProjectStats()
        
        # Track largest file
        max_lines = 0
        largest_file = None
        
        # Scan all files
        for root, dirs, files in os.walk(repo_path):
            root_path = Path(root)
            
            # Remove ignored directories from the walk
            dirs[:] = [d for d in dirs if not self.should_ignore(root_path / d, repo_path)]
            
            for file in files:
                file_path = root_path / file
                
                # Skip if should be ignored
                if self.should_ignore(file_path, repo_path):
                    continue
                
                # Get file extension
                ext = file_path.suffix.lower()
                
                try:
                    # Count lines
                    line_counts = self.count_lines(file_path)
                    
                    # Update statistics
                    stats.total_files += 1
                    stats.total_lines += line_counts['total']
                    stats.total_code_lines += line_counts['code']
                    stats.total_blank_lines += line_counts['blank']
                    stats.total_comment_lines += line_counts['comment']
                    
                    # Track by extension
                    stats.files_by_extension[ext] = stats.files_by_extension.get(ext, 0) + 1
                    stats.lines_by_extension[ext] = stats.lines_by_extension.get(ext, 0) + line_counts['total']
                    
                    # Detect language
                    if ext in self.LANGUAGE_MAP:
                        stats.languages.add(self.LANGUAGE_MAP[ext])
                    
                    # Track largest file
                    if line_counts['total'] > max_lines:
                        max_lines = line_counts['total']
                        largest_file = str(file_path.relative_to(repo_path))
                
                except Exception as e:
                    self.logger.debug(f"Error processing {file_path}: {e}")
        
        # Calculate derived statistics
        if stats.total_files > 0:
            stats.average_file_size = stats.total_lines / stats.total_files
        
        stats.largest_file = largest_file
        stats.largest_file_lines = max_lines
        
        # Detect project features
        self.detect_project_features(repo_path, stats)
        
        self.logger.info(f"Scan complete: {stats.total_files} files, {stats.total_lines} lines")
        
        return stats


def scan_project(repo_path: Path, ignore_patterns: Optional[List[str]] = None) -> ProjectStats:
    """
    Convenience function to scan a project.
    
    Args:
        repo_path: Path to repository
        ignore_patterns: Optional ignore patterns
    
    Returns:
        ProjectStats: Project statistics
    
    Example:
        >>> stats = scan_project(Path("/path/to/repo"))
    """
    scanner = ProjectScanner(ignore_patterns=ignore_patterns)
    return scanner.scan(repo_path)
