"""Markdown generation for agent-context."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def generate_table_of_contents(sections: List[str]) -> str:
    """
    Generate a table of contents from section names.
    
    Args:
        sections: List of section names
        
    Returns:
        Markdown table of contents
    """
    toc_lines = ["## Table of Contents\n"]
    for i, section in enumerate(sections, 1):
        anchor = section.lower().replace(' ', '-').replace('_', '-')
        toc_lines.append(f"{i}. [{section}](#{anchor})")
    return "\n".join(toc_lines) + "\n"


def format_repository_info(repo_info: Dict, github_url: str) -> str:
    """
    Format repository information section.
    
    Args:
        repo_info: Repository information dictionary
        github_url: Original GitHub URL
        
    Returns:
        Formatted markdown section
    """
    lines = ["## Repository Information\n"]
    lines.append(f"- **URL**: {github_url}")
    lines.append(f"- **Name**: {repo_info.get('name', 'N/A')}")
    
    if repo_info.get('branch'):
        lines.append(f"- **Branch**: {repo_info.get('branch')}")
    if repo_info.get('commit'):
        lines.append(f"- **Commit**: {repo_info.get('commit')}")
    if repo_info.get('commit_message'):
        lines.append(f"- **Latest Commit**: {repo_info.get('commit_message')}")
    
    lines.append(f"- **Extracted**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    return "\n".join(lines)


def format_readme(readme_data: Optional[Dict]) -> str:
    """
    Format README section.
    
    Args:
        readme_data: README data dictionary or None
        
    Returns:
        Formatted markdown section
    """
    if not readme_data:
        return "## README\n\n*No README file found.*\n\n"
    
    lines = ["## README\n"]
    lines.append(f"*Source: `{readme_data['path']}`*\n")
    lines.append("```markdown")
    lines.append(readme_data['content'])
    lines.append("```")
    lines.append("")
    
    return "\n".join(lines)


def format_directory_structure(structure_lines: List[str]) -> str:
    """
    Format directory structure section.
    
    Args:
        structure_lines: List of directory tree lines
        
    Returns:
        Formatted markdown section
    """
    lines = ["## Directory Structure\n"]
    lines.append("```")
    lines.extend(structure_lines)
    lines.append("```")
    lines.append("")
    
    return "\n".join(lines)


def format_config_files(config_files: List[Dict]) -> str:
    """
    Format configuration files section.
    
    Args:
        config_files: List of config file dictionaries
        
    Returns:
        Formatted markdown section
    """
    if not config_files:
        return "## Configuration Files\n\n*No configuration files found.*\n\n"
    
    lines = ["## Configuration Files\n"]
    
    for config_file in config_files:
        lines.append(f"### {config_file['path']}\n")
        lines.append("```")
        lines.append(config_file['content'])
        lines.append("```")
        lines.append("")
    
    return "\n".join(lines)


def format_python_analysis(analyses: List[Dict]) -> str:
    """
    Format Python code analysis section.
    
    Args:
        analyses: List of Python file analysis dictionaries
        
    Returns:
        Formatted markdown section
    """
    if not analyses:
        return "## Python Code Analysis\n\n*No Python files found.*\n\n"
    
    lines = ["## Python Code Analysis\n"]
    
    for analysis in analyses:
        lines.append(f"### {analysis['path']}\n")
        
        # Module docstring
        if analysis.get('module_docstring'):
            lines.append("**Module Docstring:**")
            lines.append("```")
            lines.append(analysis['module_docstring'])
            lines.append("```")
            lines.append("")
        
        # Imports
        if analysis.get('imports'):
            lines.append("**Imports:**")
            for imp in analysis['imports']:
                lines.append(f"- `{imp}`")
            lines.append("")
        
        # Classes
        if analysis.get('classes'):
            lines.append("**Classes:**")
            for cls in analysis['classes']:
                bases_str = f"({', '.join(cls['bases'])})" if cls.get('bases') else ""
                lines.append(f"\n#### `class {cls['name']}{bases_str}`")
                
                if cls.get('docstring'):
                    lines.append("```")
                    lines.append(cls['docstring'])
                    lines.append("```")
                
                if cls.get('methods'):
                    lines.append("**Methods:**")
                    for method in cls['methods']:
                        lines.append(f"- `{method['signature']}`")
                        if method.get('docstring'):
                            lines.append(f"  - {method['docstring'].split(chr(10))[0]}")
                    lines.append("")
            lines.append("")
        
        # Functions
        if analysis.get('functions'):
            lines.append("**Functions:**")
            for func in analysis['functions']:
                lines.append(f"\n#### `{func['signature']}`")
                if func.get('docstring'):
                    lines.append("```")
                    lines.append(func['docstring'])
                    lines.append("```")
            lines.append("")
        
        lines.append("---\n")
    
    return "\n".join(lines)


def format_example_files(example_files: List[Dict]) -> str:
    """
    Format example files section.
    
    Args:
        example_files: List of example file dictionaries
        
    Returns:
        Formatted markdown section
    """
    if not example_files:
        return "## Example Files\n\n*No example files found.*\n\n"
    
    lines = ["## Example Files\n"]
    
    # Group by directory
    by_directory: Dict[str, List[Dict]] = {}
    for example_file in example_files:
        dir_path = str(Path(example_file['path']).parent)
        if dir_path not in by_directory:
            by_directory[dir_path] = []
        by_directory[dir_path].append(example_file)
    
    for dir_path, files in sorted(by_directory.items()):
        lines.append(f"### {dir_path}/\n")
        for example_file in files:
            file_name = Path(example_file['path']).name
            lines.append(f"#### {file_name}\n")
            lines.append(f"*Source: `{example_file['path']}`*\n")
            
            # Determine file extension for syntax highlighting
            ext = Path(example_file['path']).suffix.lstrip('.')
            lang = ext if ext else 'text'
            
            lines.append(f"```{lang}")
            lines.append(example_file['content'])
            lines.append("```")
            lines.append("")
    
    return "\n".join(lines)


def generate_markdown(
    repo_info: Dict,
    github_url: str,
    readme_data: Optional[Dict],
    directory_structure: List[str],
    config_files: List[Dict],
    python_analyses: List[Dict],
    example_files: List[Dict],
    verbose: bool = False
) -> str:
    """
    Generate complete markdown document from all extracted content.
    
    Args:
        repo_info: Repository information dictionary
        github_url: Original GitHub URL
        readme_data: README data dictionary or None
        directory_structure: Directory tree lines
        config_files: List of config file dictionaries
        python_analyses: List of Python file analysis dictionaries
        example_files: List of example file dictionaries
        verbose: Whether to include table of contents
        
    Returns:
        Complete markdown document as string
    """
    sections = []
    markdown_parts = []
    
    # Title
    markdown_parts.append(f"# {repo_info.get('name', 'Repository')} - Context Documentation\n")
    markdown_parts.append(f"*Generated by agent-context*\n")
    markdown_parts.append("")
    
    # Repository Information
    sections.append("Repository Information")
    markdown_parts.append(format_repository_info(repo_info, github_url))
    
    # Table of Contents (if verbose)
    if verbose:
        all_sections = [
            "Repository Information",
            "README",
            "Directory Structure",
            "Configuration Files",
            "Python Code Analysis",
            "Example Files",
        ]
        markdown_parts.append(generate_table_of_contents(all_sections))
    
    # README
    sections.append("README")
    markdown_parts.append(format_readme(readme_data))
    
    # Directory Structure
    sections.append("Directory Structure")
    markdown_parts.append(format_directory_structure(directory_structure))
    
    # Configuration Files
    sections.append("Configuration Files")
    markdown_parts.append(format_config_files(config_files))
    
    # Python Code Analysis
    sections.append("Python Code Analysis")
    markdown_parts.append(format_python_analysis(python_analyses))
    
    # Example Files
    sections.append("Example Files")
    markdown_parts.append(format_example_files(example_files))
    
    return "\n".join(markdown_parts)


def write_markdown(content: str, output_path: Path) -> None:
    """
    Write markdown content to file.
    
    Args:
        content: Markdown content string
        output_path: Path to output file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
