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
        
        # Type Aliases
        if analysis.get('type_aliases'):
            lines.append("**Type Aliases:**")
            for alias in analysis['type_aliases']:
                type_str = f": {alias['type']}" if alias.get('type') else ""
                value_str = f" = {alias['value']}" if alias.get('value') else ""
                lines.append(f"- `{alias['name']}{type_str}{value_str}`")
            lines.append("")
        
        # Constants
        if analysis.get('constants'):
            lines.append("**Constants:**")
            for const in analysis['constants']:
                lines.append(f"- `{const['name']} = {const['value']}`")
            lines.append("")
        
        # Enums
        if analysis.get('enums'):
            lines.append("**Enums:**")
            for enum in analysis['enums']:
                lines.append(f"\n#### `enum {enum['name']}`")
                if enum.get('docstring'):
                    lines.append(f"*{enum['docstring'].split(chr(10))[0]}*")
                if enum.get('members'):
                    for member in enum['members']:
                        lines.append(f"- `{member['name']} = {member['value']}`")
            lines.append("")
        
        # Exceptions
        if analysis.get('exceptions'):
            lines.append("**Custom Exceptions:**")
            for exc in analysis['exceptions']:
                bases_str = f"({', '.join(exc['bases'])})" if exc.get('bases') else ""
                lines.append(f"- `class {exc['name']}{bases_str}`")
                if exc.get('docstring'):
                    lines.append(f"  - {exc['docstring'].split(chr(10))[0]}")
            lines.append("")
        
        # Imports (grouped)
        if analysis.get('imports'):
            lines.append("**Imports:**")
            for imp in analysis['imports']:
                lines.append(f"- `{imp}`")
            lines.append("")
        
        # Classes (public API first)
        if analysis.get('classes'):
            lines.append("**Classes:**")
            for cls in analysis['classes']:
                bases_str = f"({', '.join(cls['bases'])})" if cls.get('bases') else ""
                lines.append(f"\n#### `class {cls['name']}{bases_str}`")
                
                if cls.get('docstring'):
                    lines.append("```")
                    lines.append(cls['docstring'])
                    lines.append("```")
                
                # Class attributes
                if cls.get('attributes'):
                    public_attrs = [a for a in cls['attributes'] if a.get('is_public', True)]
                    if public_attrs:
                        lines.append("**Attributes:**")
                        for attr in public_attrs:
                            type_str = f": {attr['type']}" if attr.get('type') else ""
                            value_str = f" = {attr['value']}" if attr.get('value') else ""
                            lines.append(f"- `{attr['name']}{type_str}{value_str}`")
                        lines.append("")
                
                # Methods (public first)
                if cls.get('methods'):
                    public_methods = [m for m in cls['methods'] if m.get('is_public', True)]
                    private_methods = [m for m in cls['methods'] if not m.get('is_public', True)]
                    
                    if public_methods:
                        lines.append("**Public Methods:**")
                        for method in public_methods:
                            decorator_str = f" @{', @'.join(method.get('decorators', []))}" if method.get('decorators') else ""
                            prop_marker = " *(property)*" if method.get('is_property') else ""
                            lines.append(f"- `{method['signature']}{decorator_str}{prop_marker}`")
                            if method.get('docstring'):
                                doc_preview = method['docstring'].split('\n')[0][:150]
                                lines.append(f"  - {doc_preview}")
                        lines.append("")
                    
                    if private_methods:
                        lines.append("**Private Methods:**")
                        for method in private_methods[:5]:  # Limit private methods
                            lines.append(f"- `{method['signature']}`")
                        if len(private_methods) > 5:
                            lines.append(f"  - ... and {len(private_methods) - 5} more private methods")
                        lines.append("")
            lines.append("")
        
        # Functions (public API first)
        if analysis.get('functions'):
            public_funcs = [f for f in analysis['functions'] if f.get('is_public', True)]
            private_funcs = [f for f in analysis['functions'] if not f.get('is_public', True)]
            
            if public_funcs:
                lines.append("**Public Functions:**")
                for func in public_funcs:
                    decorator_str = f" @{', @'.join(func.get('decorators', []))}" if func.get('decorators') else ""
                    lines.append(f"\n#### `{func['signature']}{decorator_str}`")
                    if func.get('docstring'):
                        lines.append("```")
                        # Limit very long docstrings
                        docstring = func['docstring']
                        if len(docstring) > 1000:
                            docstring = docstring[:1000] + "\n... (truncated)"
                        lines.append(docstring)
                        lines.append("```")
                lines.append("")
            
            if private_funcs:
                lines.append("**Private Functions:**")
                for func in private_funcs[:3]:  # Limit private functions shown
                    lines.append(f"- `{func['signature']}`")
                if len(private_funcs) > 3:
                    lines.append(f"  - ... and {len(private_funcs) - 3} more private functions")
                lines.append("")
        
        # Main block
        if analysis.get('main_block'):
            lines.append("**Main Entry Point:**")
            lines.append("```python")
            lines.append(analysis['main_block'])
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
            # Limit example file size for readability
            content = example_file['content']
            if len(content) > 5000:
                content = content[:5000] + "\n\n... (file truncated for brevity)"
            lines.append(content)
            lines.append("```")
            lines.append("")
    
    return "\n".join(lines)


def generate_api_summary(python_analyses: List[Dict]) -> str:
    """
    Generate a quick API summary for AI context.
    
    Args:
        python_analyses: List of Python file analysis dictionaries
        
    Returns:
        Formatted API summary section
    """
    if not python_analyses:
        return ""
    
    lines = ["## API Summary\n"]
    lines.append("*Quick reference of public API for AI context*\n")
    
    all_public_classes = []
    all_public_functions = []
    all_exceptions = []
    all_enums = []
    
    for analysis in python_analyses:
        # Collect public classes
        for cls in analysis.get('classes', []):
            public_methods = [m for m in cls.get('methods', []) if m.get('is_public', True)]
            if public_methods or cls.get('is_public', True):
                all_public_classes.append({
                    'name': cls['name'],
                    'path': analysis['path'],
                    'bases': cls.get('bases', []),
                    'method_count': len(public_methods),
                })
        
        # Collect public functions
        for func in analysis.get('functions', []):
            if func.get('is_public', True):
                all_public_functions.append({
                    'name': func['name'],
                    'path': analysis['path'],
                    'signature': func['signature'],
                })
        
        # Collect exceptions
        all_exceptions.extend(analysis.get('exceptions', []))
        
        # Collect enums
        all_enums.extend(analysis.get('enums', []))
    
    if all_public_classes:
        lines.append("### Public Classes\n")
        for cls in all_public_classes[:20]:  # Limit to top 20
            bases_str = f"({', '.join(cls['bases'])})" if cls.get('bases') else ""
            lines.append(f"- `{cls['name']}{bases_str}` - {cls['method_count']} public methods (*{cls['path']}*)")
        if len(all_public_classes) > 20:
            lines.append(f"- ... and {len(all_public_classes) - 20} more classes")
        lines.append("")
    
    if all_public_functions:
        lines.append("### Public Functions\n")
        for func in all_public_functions[:30]:  # Limit to top 30
            lines.append(f"- `{func['name']}` (*{func['path']}*)")
        if len(all_public_functions) > 30:
            lines.append(f"- ... and {len(all_public_functions) - 30} more functions")
        lines.append("")
    
    if all_exceptions:
        lines.append("### Custom Exceptions\n")
        for exc in all_exceptions[:10]:
            lines.append(f"- `{exc['name']}`")
        lines.append("")
    
    if all_enums:
        lines.append("### Enums\n")
        for enum in all_enums[:10]:
            lines.append(f"- `{enum['name']}`")
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
            "API Summary",
            "README",
            "Directory Structure",
            "Configuration Files",
            "Python Code Analysis",
            "Example Files",
        ]
        markdown_parts.append(generate_table_of_contents(all_sections))
    
    # API Summary (for quick AI reference)
    api_summary = generate_api_summary(python_analyses)
    if api_summary:
        sections.append("API Summary")
        markdown_parts.append(api_summary)
    
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
