"""Python code analysis using AST for agent-context."""

import ast
from pathlib import Path
from typing import Dict, List, Optional

from .utils import find_files_by_pattern, get_relative_path, read_file_safe


def format_function_signature(func_node: ast.FunctionDef) -> str:
    """
    Format a function signature from AST node.
    
    Args:
        func_node: AST function definition node
        
    Returns:
        Formatted function signature string
    """
    args = []
    
    # Process arguments
    for arg in func_node.args.args:
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"
        args.append(arg_str)
    
    # Process default values
    defaults = func_node.args.defaults
    num_defaults = len(defaults)
    num_args = len(func_node.args.args)
    
    if num_defaults > 0:
        # Adjust for *args and **kwargs
        start_idx = num_args - num_defaults
        for i, default in enumerate(defaults):
            idx = start_idx + i
            if idx < len(args):
                default_str = ast.unparse(default)
                args[idx] = f"{args[idx]}={default_str}"
    
    # Handle *args
    if func_node.args.vararg:
        vararg_name = func_node.args.vararg.arg
        if func_node.args.vararg.annotation:
            vararg_name += f": {ast.unparse(func_node.args.vararg.annotation)}"
        args.append(f"*{vararg_name}")
    
    # Handle **kwargs
    if func_node.args.kwarg:
        kwarg_name = func_node.args.kwarg.arg
        if func_node.args.kwarg.annotation:
            kwarg_name += f": {ast.unparse(func_node.args.kwarg.annotation)}"
        args.append(f"**{kwarg_name}")
    
    # Build signature
    sig = f"def {func_node.name}({', '.join(args)})"
    
    # Add return type annotation
    if func_node.returns:
        sig += f" -> {ast.unparse(func_node.returns)}"
    
    return sig


def extract_docstring(node: ast.AST) -> Optional[str]:
    """
    Extract docstring from an AST node.
    
    Args:
        node: AST node (function, class, or module)
        
    Returns:
        Docstring string or None
    """
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
        if ast.get_docstring(node):
            return ast.get_docstring(node)
    return None


def analyze_python_file(file_path: Path, repo_path: Path) -> Optional[Dict]:
    """
    Analyze a Python file and extract code structure.
    
    Args:
        file_path: Path to the Python file
        repo_path: Root path of the repository
        
    Returns:
        Dictionary with analysis results or None if analysis fails
    """
    content = read_file_safe(file_path)
    if content is None:
        return None
    
    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        # Skip files with syntax errors
        return None
    
    analysis = {
        'path': get_relative_path(file_path, repo_path),
        'imports': [],
        'classes': [],
        'functions': [],
        'module_docstring': extract_docstring(tree),
    }
    
    # Extract imports
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    analysis['imports'].append(f"import {alias.name}")
            else:
                module = node.module or ""
                names = ", ".join([alias.name for alias in node.names])
                analysis['imports'].append(f"from {module} import {names}")
    
    # Extract classes and their methods
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info = {
                'name': node.name,
                'docstring': extract_docstring(node),
                'methods': [],
                'bases': [ast.unparse(base) for base in node.bases],
            }
            
            # Extract methods
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_info = {
                        'name': item.name,
                        'signature': format_function_signature(item),
                        'docstring': extract_docstring(item),
                    }
                    class_info['methods'].append(method_info)
            
            analysis['classes'].append(class_info)
    
    # Extract top-level functions
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            func_info = {
                'name': node.name,
                'signature': format_function_signature(node),
                'docstring': extract_docstring(node),
            }
            analysis['functions'].append(func_info)
        elif isinstance(node, ast.AsyncFunctionDef):
            func_info = {
                'name': node.name,
                'signature': format_function_signature(node),
                'docstring': extract_docstring(node),
            }
            analysis['functions'].append(func_info)
    
    # Remove duplicates from imports
    analysis['imports'] = list(dict.fromkeys(analysis['imports']))
    
    return analysis


def analyze_all_python_files(repo_path: Path) -> List[Dict]:
    """
    Analyze all Python files in the repository.
    
    Args:
        repo_path: Root path of the repository
        
    Returns:
        List of analysis dictionaries for each Python file
    """
    python_files = find_files_by_pattern(repo_path, ['*.py'])
    
    analyses = []
    for py_file in python_files:
        analysis = analyze_python_file(py_file, repo_path)
        if analysis:
            analyses.append(analysis)
    
    return analyses
