"""Utility functions for agent-context."""

import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List, Optional


@contextmanager
def temporary_directory(prefix: str = "agent_context_") -> Iterator[Path]:
    """
    Create a temporary directory and ensure it's cleaned up.
    
    Args:
        prefix: Prefix for the temporary directory name
        
    Yields:
        Path to the temporary directory
        
    Example:
        >>> with temporary_directory() as temp_dir:
        ...     # Use temp_dir
        ...     pass
        # Directory is automatically cleaned up
    """
    temp_dir = None
    try:
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
        yield temp_dir
    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def get_directory_tree(root_path: Path, max_depth: Optional[int] = None) -> List[str]:
    """
    Generate a directory tree structure.
    
    Args:
        root_path: Root directory path
        max_depth: Maximum depth to traverse (None for unlimited)
        
    Returns:
        List of strings representing the directory tree
    """
    # Exclude test directories and other non-essential dirs
    exclude_dirs = {'test', 'tests', '__tests__', '.pytest_cache', '__pycache__', '.git', '.venv', 'venv', 'env', 'node_modules', 'tutorial', 'tutorials'}
    
    tree_lines = []
    
    def _build_tree(path: Path, prefix: str = "", is_last: bool = True, depth: int = 0):
        if max_depth is not None and depth > max_depth:
            return
        
        # Skip excluded directories
        if path.is_dir() and path.name in exclude_dirs:
            return
            
        # Add current directory/file
        connector = "└── " if is_last else "├── "
        tree_lines.append(f"{prefix}{connector}{path.name}")
        
        # Update prefix for children
        extension = "    " if is_last else "│   "
        new_prefix = prefix + extension
        
        # Process children if it's a directory
        if path.is_dir():
            children = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
            # Filter out excluded directories
            children = [c for c in children if not (c.is_dir() and c.name in exclude_dirs)]
            for i, child in enumerate(children):
                is_last_child = i == len(children) - 1
                _build_tree(child, new_prefix, is_last_child, depth + 1)
    
    _build_tree(root_path)
    return tree_lines


def find_files_by_pattern(
    root_path: Path,
    patterns: List[str],
    exclude_dirs: Optional[List[str]] = None
) -> List[Path]:
    """
    Find files matching given patterns.
    
    Args:
        root_path: Root directory to search
        patterns: List of filename patterns to match (e.g., ['README.md', '*.txt'])
        exclude_dirs: List of directory names to exclude from search
        
    Returns:
        List of matching file paths
    """
    if exclude_dirs is None:
        exclude_dirs = ['__pycache__', '.git', '.venv', 'venv', 'env', 'node_modules', '.pytest_cache', 'test', 'tests', '__tests__', '.pytest_cache']
    
    matching_files = []
    
    for root, dirs, files in os.walk(root_path):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        root_path_obj = Path(root)
        for file in files:
            file_path = root_path_obj / file
            for pattern in patterns:
                if file_path.match(pattern) or file == pattern:
                    matching_files.append(file_path)
                    break
    
    return sorted(matching_files)


def find_directories(
    root_path: Path,
    dir_names: List[str],
    exclude_dirs: Optional[List[str]] = None
) -> List[Path]:
    """
    Find directories with specific names.
    
    Args:
        root_path: Root directory to search
        dir_names: List of directory names to find (e.g., ['examples', 'demo'])
        exclude_dirs: List of directory names to exclude from search
        
    Returns:
        List of matching directory paths
    """
    if exclude_dirs is None:
        exclude_dirs = ['__pycache__', '.git', '.venv', 'venv', 'env', 'node_modules', 'test', 'tests', '__tests__']
    
    matching_dirs = []
    
    for root, dirs, _ in os.walk(root_path):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        root_path_obj = Path(root)
        for dir_name in dir_names:
            if dir_name in dirs:
                matching_dirs.append(root_path_obj / dir_name)
    
    return sorted(matching_dirs)


def get_files_in_directories(directories: List[Path]) -> List[Path]:
    """
    Get all files in the given directories recursively.
    
    Args:
        directories: List of directory paths
        
    Returns:
        List of all file paths found in the directories
    """
    all_files = []
    
    for directory in directories:
        if directory.exists() and directory.is_dir():
            for root, _, files in os.walk(directory):
                root_path = Path(root)
                for file in files:
                    file_path = root_path / file
                    if file_path.is_file():
                        all_files.append(file_path)
    
    return sorted(all_files)


def get_relative_path(file_path: Path, root_path: Path) -> str:
    """
    Get relative path from root path.
    
    Args:
        file_path: File path
        root_path: Root directory path
        
    Returns:
        Relative path string
    """
    try:
        return str(file_path.relative_to(root_path))
    except ValueError:
        return str(file_path)


def is_binary_file(file_path: Path) -> bool:
    """
    Check if a file is likely binary.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file appears to be binary
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            return b'\x00' in chunk
    except Exception:
        return True


def read_file_safe(file_path: Path, max_size: int = 10 * 1024 * 1024) -> Optional[str]:
    """
    Safely read a text file with size limit.
    
    Args:
        file_path: Path to the file
        max_size: Maximum file size in bytes (default: 10MB)
        
    Returns:
        File contents as string, or None if file is too large or binary
    """
    try:
        if not file_path.exists() or not file_path.is_file():
            return None
            
        if file_path.stat().st_size > max_size:
            return None
            
        if is_binary_file(file_path):
            return None
            
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return None
