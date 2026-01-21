"""Repository cloning functionality for agent-context."""

import os
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import git
from git.exc import GitCommandError, InvalidGitRepositoryError

from .utils import temporary_directory


def validate_github_url(url: str) -> bool:
    """
    Validate if the URL is a valid GitHub repository URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid GitHub URL, False otherwise
    """
    github_patterns = [
        r'^https://github\.com/[\w\.-]+/[\w\.-]+(?:\.git)?/?$',
        r'^git@github\.com:[\w\.-]+/[\w\.-]+(?:\.git)?/?$',
        r'^github\.com/[\w\.-]+/[\w\.-]+/?$',
    ]
    
    for pattern in github_patterns:
        if re.match(pattern, url):
            return True
    
    return False


def normalize_github_url(url: str) -> str:
    """
    Normalize GitHub URL to HTTPS format.
    
    Args:
        url: GitHub URL in various formats
        
    Returns:
        Normalized HTTPS GitHub URL
    """
    # Remove .git suffix if present
    url = url.rstrip('/').rstrip('.git')
    
    # Handle git@github.com:user/repo format
    if url.startswith('git@github.com:'):
        url = url.replace('git@github.com:', 'https://github.com/')
    
    # Handle github.com/user/repo format
    if url.startswith('github.com/'):
        url = 'https://' + url
    
    # Ensure it starts with https://
    if not url.startswith('https://'):
        url = 'https://' + url
    
    return url


def clone_repository(
    github_url: str,
    output_dir: Path,
    token: Optional[str] = None,
    depth: Optional[int] = None
) -> Path:
    """
    Clone a GitHub repository to the specified directory.
    
    Args:
        github_url: GitHub repository URL
        output_dir: Directory to clone into
        token: Optional GitHub token for private repos
        depth: Optional shallow clone depth (1 for latest commit only)
        
    Returns:
        Path to the cloned repository
        
    Raises:
        ValueError: If URL is invalid
        GitCommandError: If clone fails
    """
    if not validate_github_url(github_url):
        raise ValueError(f"Invalid GitHub URL: {github_url}")
    
    # Normalize URL
    normalized_url = normalize_github_url(github_url)
    
    # Add token to URL if provided
    if token:
        parsed = urlparse(normalized_url)
        # Format: https://token@github.com/user/repo
        normalized_url = f"{parsed.scheme}://{token}@{parsed.netloc}{parsed.path}"
    
    # Extract repo name from URL
    repo_name = normalized_url.rstrip('/').split('/')[-1]
    clone_path = output_dir / repo_name
    
    # Prepare clone arguments
    clone_kwargs = {
        'url': normalized_url,
        'to_path': str(clone_path),
    }
    
    # Add depth for shallow clone if specified
    if depth:
        clone_kwargs['depth'] = depth
    
    try:
        # Clone the repository
        git.Repo.clone_from(**clone_kwargs)
        return clone_path
    except GitCommandError as e:
        error_msg = str(e)
        if 'Authentication failed' in error_msg or 'Permission denied' in error_msg:
            raise GitCommandError(
                "Authentication failed. Please check your GitHub token or repository permissions."
            ) from e
        elif 'Repository not found' in error_msg:
            raise GitCommandError(
                "Repository not found. Please check the URL and ensure the repository exists."
            ) from e
        else:
            raise GitCommandError(f"Failed to clone repository: {error_msg}") from e


def get_repository_info(repo_path: Path) -> dict:
    """
    Get information about a cloned repository.
    
    Args:
        repo_path: Path to the cloned repository
        
    Returns:
        Dictionary with repository information
    """
    info = {
        'path': str(repo_path),
        'name': repo_path.name,
    }
    
    try:
        repo = git.Repo(repo_path)
        info['remote_url'] = repo.remotes.origin.url if repo.remotes else None
        info['branch'] = repo.active_branch.name if not repo.head.is_detached else None
        info['commit'] = repo.head.commit.hexsha[:7]
        info['commit_message'] = repo.head.commit.message.split('\n')[0]
    except (InvalidGitRepositoryError, AttributeError):
        pass
    
    return info
