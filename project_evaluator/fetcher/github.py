"""
GitHub repository fetcher module.

Handles cloning, caching, and validation of GitHub repositories
using GitPython with robust error handling.
"""

import re
import shutil
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime, timedelta
import logging

import git
from git.exc import GitCommandError, InvalidGitRepositoryError

from utils.logger import get_logger


class GitHubFetcher:
    """
    Fetches and caches GitHub repositories.
    
    Implements Single Responsibility Principle - only handles
    repository fetching and cache management.
    """
    
    def __init__(self, cache_dir: str = ".cache/repos", cache_expiry_days: int = 7):
        """
        Initialize the GitHub fetcher.
        
        Args:
            cache_dir: Directory to store cloned repositories
            cache_expiry_days: Number of days before cache expires
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry_days = cache_expiry_days
        self.logger = get_logger()
    
    def validate_github_url(self, url: str) -> bool:
        """
        Validate if the provided URL is a valid GitHub repository URL.
        
        Args:
            url: GitHub repository URL
        
        Returns:
            bool: True if valid, False otherwise
        
        Example:
            >>> fetcher = GitHubFetcher()
            >>> fetcher.validate_github_url("https://github.com/user/repo")
            True
        """
        patterns = [
            r"^https?://github\.com/[\w\-\.]+/[\w\-\.]+/?$",
            r"^git@github\.com:[\w\-\.]+/[\w\-\.]+\.git$",
            r"^https?://github\.com/[\w\-\.]+/[\w\-\.]+\.git$"
        ]
        
        return any(re.match(pattern, url.strip()) for pattern in patterns)
    
    def extract_repo_name(self, url: str) -> str:
        """
        Extract repository name from GitHub URL.
        
        Args:
            url: GitHub repository URL
        
        Returns:
            str: Repository name in format "owner_repo"
        
        Example:
            >>> fetcher = GitHubFetcher()
            >>> fetcher.extract_repo_name("https://github.com/user/repo")
            'user_repo'
        """
        # Remove .git suffix if present
        url = url.rstrip('/').replace('.git', '')
        
        # Extract owner and repo name
        if 'github.com/' in url:
            parts = url.split('github.com/')[-1].split('/')
            if len(parts) >= 2:
                return f"{parts[0]}_{parts[1]}"
        elif 'github.com:' in url:
            parts = url.split('github.com:')[-1].split('/')
            if len(parts) >= 2:
                return f"{parts[0]}_{parts[1]}"
        
        raise ValueError(f"Cannot extract repository name from URL: {url}")
    
    def is_cache_valid(self, repo_path: Path) -> bool:
        """
        Check if cached repository is still valid (not expired).
        
        Args:
            repo_path: Path to cached repository
        
        Returns:
            bool: True if cache is valid, False if expired or invalid
        """
        if not repo_path.exists():
            return False
        
        # Check if it's a valid git repository
        try:
            repo = git.Repo(repo_path)
            if repo.bare:
                return False
        except InvalidGitRepositoryError:
            return False
        
        # Check cache age
        mtime = datetime.fromtimestamp(repo_path.stat().st_mtime)
        age = datetime.now() - mtime
        
        return age < timedelta(days=self.cache_expiry_days)
    
    def clone_repository(self, url: str, target_path: Path) -> bool:
        """
        Clone a GitHub repository to the target path.
        
        Args:
            url: GitHub repository URL
            target_path: Destination path for cloning
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Cloning repository from {url}...")
            
            # Remove existing directory if present
            if target_path.exists():
                shutil.rmtree(target_path)
            
            # Clone the repository with depth=1 for faster cloning
            git.Repo.clone_from(
                url,
                target_path,
                depth=1,
                single_branch=True
            )
            
            self.logger.info(f"Successfully cloned to {target_path}")
            return True
            
        except GitCommandError as e:
            self.logger.error(f"Git command error while cloning: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error while cloning: {e}")
            return False
    
    def fetch(self, url: str, force_refresh: bool = False) -> Optional[Path]:
        """
        Fetch a GitHub repository (clone or use cache).
        
        This is the main public interface for the fetcher.
        
        Args:
            url: GitHub repository URL
            force_refresh: If True, ignore cache and clone fresh
        
        Returns:
            Optional[Path]: Path to repository if successful, None otherwise
        
        Example:
            >>> fetcher = GitHubFetcher()
            >>> repo_path = fetcher.fetch("https://github.com/user/repo")
            >>> if repo_path:
            ...     print(f"Repository available at: {repo_path}")
        """
        # Validate URL
        if not self.validate_github_url(url):
            self.logger.error(f"Invalid GitHub URL: {url}")
            return None
        
        # Extract repository name
        try:
            repo_name = self.extract_repo_name(url)
        except ValueError as e:
            self.logger.error(str(e))
            return None
        
        # Determine cache path
        repo_path = self.cache_dir / repo_name
        
        # Check cache
        if not force_refresh and self.is_cache_valid(repo_path):
            self.logger.info(f"Using cached repository: {repo_path}")
            return repo_path
        
        # Clone repository
        if self.clone_repository(url, repo_path):
            return repo_path
        
        return None
    
    def clear_cache(self) -> None:
        """
        Clear all cached repositories.
        
        Useful for maintenance and testing.
        """
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Cache cleared successfully")
    
    def get_cache_size(self) -> Tuple[int, int]:
        """
        Get the size and count of cached repositories.
        
        Returns:
            Tuple[int, int]: (total_size_bytes, repo_count)
        """
        if not self.cache_dir.exists():
            return 0, 0
        
        total_size = 0
        repo_count = 0
        
        for item in self.cache_dir.iterdir():
            if item.is_dir():
                repo_count += 1
                for file in item.rglob('*'):
                    if file.is_file():
                        total_size += file.stat().st_size
        
        return total_size, repo_count


# Convenience function for quick fetching
def fetch_github_repo(url: str, 
                      cache_dir: str = ".cache/repos",
                      force_refresh: bool = False) -> Optional[Path]:
    """
    Quick convenience function to fetch a GitHub repository.
    
    Args:
        url: GitHub repository URL
        cache_dir: Cache directory
        force_refresh: Force fresh clone
    
    Returns:
        Optional[Path]: Path to repository or None
    
    Example:
        >>> repo_path = fetch_github_repo("https://github.com/user/repo")
    """
    fetcher = GitHubFetcher(cache_dir=cache_dir)
    return fetcher.fetch(url, force_refresh=force_refresh)
