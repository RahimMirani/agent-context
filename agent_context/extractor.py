"""Content extraction functionality for agent-context."""

from pathlib import Path
from typing import Dict, List, Optional

from .utils import (
    find_directories,
    find_files_by_pattern,
    get_files_in_directories,
    get_relative_path,
    read_file_safe,
)


# Common config file patterns
CONFIG_FILE_PATTERNS = [
    'requirements.txt',
    'package.json',
    'pyproject.toml',
    'setup.py',
    'Pipfile',
    'Pipfile.lock',
    'environment.yml',
    'Dockerfile',
    '.dockerignore',
    '.env.example',
    '.env.template',
    'docker-compose.yml',
    'docker-compose.yaml',
    'Makefile',
    'CMakeLists.txt',
    'Cargo.toml',
    'go.mod',
    'go.sum',
    'Gemfile',
    'composer.json',
    'tsconfig.json',
    'webpack.config.js',
    'jest.config.js',
    '.prettierrc',
    '.eslintrc',
    'package-lock.json',
    'yarn.lock',
    'poetry.lock',
    'setup.cfg',
    'MANIFEST.in',
    '.gitignore',
    '.gitattributes',
]

# README file patterns (in priority order)
README_PATTERNS = [
    'README.md',
    'README.txt',
    'README.rst',
    'README',
    'readme.md',
    'readme.txt',
]

# Example directory names
EXAMPLE_DIR_NAMES = [
    'examples',
    'example',
    'demo',
    'demos',
    'samples',
    'sample',
    'test',
    'tests',
    'tutorial',
    'tutorials',
]


def extract_readme(repo_path: Path) -> Optional[Dict[str, str]]:
    """
    Extract README file from repository.
    
    Args:
        repo_path: Path to the repository root
        
    Returns:
        Dictionary with 'path' and 'content' keys, or None if not found
    """
    for pattern in README_PATTERNS:
        readme_files = find_files_by_pattern(repo_path, [pattern])
        if readme_files:
            readme_path = readme_files[0]
            content = read_file_safe(readme_path)
            if content:
                return {
                    'path': get_relative_path(readme_path, repo_path),
                    'content': content,
                }
    
    return None


def extract_config_files(repo_path: Path) -> List[Dict[str, str]]:
    """
    Extract configuration files from repository.
    
    Args:
        repo_path: Path to the repository root
        
    Returns:
        List of dictionaries with 'path' and 'content' keys
    """
    config_files = []
    
    # Find all config files
    found_files = find_files_by_pattern(repo_path, CONFIG_FILE_PATTERNS)
    
    for config_file in found_files:
        content = read_file_safe(config_file)
        if content is not None:
            config_files.append({
                'path': get_relative_path(config_file, repo_path),
                'content': content,
            })
    
    return config_files


def extract_example_files(repo_path: Path) -> List[Dict[str, str]]:
    """
    Extract example files from example directories.
    
    Args:
        repo_path: Path to the repository root
        
    Returns:
        List of dictionaries with 'path' and 'content' keys, grouped by directory
    """
    example_files = []
    
    # Find example directories
    example_dirs = find_directories(repo_path, EXAMPLE_DIR_NAMES)
    
    # Get all files in example directories
    all_example_files = get_files_in_directories(example_dirs)
    
    for example_file in all_example_files:
        content = read_file_safe(example_file)
        if content is not None:
            example_files.append({
                'path': get_relative_path(example_file, repo_path),
                'content': content,
            })
    
    return example_files


def extract_directory_structure(repo_path: Path) -> List[str]:
    """
    Extract directory structure tree.
    
    Args:
        repo_path: Path to the repository root
        
    Returns:
        List of strings representing the directory tree
    """
    return get_directory_tree(repo_path)


def extract_all_content(repo_path: Path) -> Dict:
    """
    Extract all content from the repository.
    
    Args:
        repo_path: Path to the repository root
        
    Returns:
        Dictionary containing all extracted content:
        - readme: README content (if found)
        - config_files: List of config file contents
        - example_files: List of example file contents
        - directory_structure: Directory tree structure
    """
    return {
        'readme': extract_readme(repo_path),
        'config_files': extract_config_files(repo_path),
        'example_files': extract_example_files(repo_path),
        'directory_structure': extract_directory_structure(repo_path),
    }
