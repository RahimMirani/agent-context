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
    
    # Skip empty or very small files (likely empty __init__.py)
    if len(content.strip()) < 10:
        return None
    
    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        # Skip files with syntax errors
        return None
    
    # Skip __init__.py files that only have imports or are empty
    if file_path.name == '__init__.py':
        has_content = False
        for node in tree.body:
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                has_content = True
                break
        if not has_content:
            return None
    
    analysis = {
        'path': get_relative_path(file_path, repo_path),
        'imports': [],
        'classes': [],
        'functions': [],
        'constants': [],
        'enums': [],
        'exceptions': [],
        'type_aliases': [],
        'module_docstring': extract_docstring(tree),
        'main_block': None,
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
            try:
                class_info = {
                    'name': node.name,
                    'docstring': extract_docstring(node),
                    'methods': [],
                    'bases': [ast.unparse(base) for base in node.bases] if node.bases else [],
                }
                
                # Extract methods and class attributes
                class_info['attributes'] = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        try:
                            # Skip empty methods (just pass)
                            if len(item.body) == 1 and isinstance(item.body[0], ast.Pass):
                                continue
                            
                            method_info = {
                                'name': item.name,
                                'signature': format_function_signature(item),
                                'docstring': extract_docstring(item),
                                'is_public': not item.name.startswith('_'),
                                'is_property': any('property' in ast.unparse(d).lower() for d in item.decorator_list),
                                'decorators': [ast.unparse(d) for d in item.decorator_list] if item.decorator_list else [],
                            }
                            class_info['methods'].append(method_info)
                        except Exception:
                            # Skip methods that can't be parsed
                            continue
                    elif isinstance(item, ast.Assign):
                        # Extract class-level attributes
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                try:
                                    attr_info = {
                                        'name': target.id,
                                        'value': ast.unparse(item.value)[:100] if item.value else None,
                                        'is_public': not target.id.startswith('_'),
                                    }
                                    class_info['attributes'].append(attr_info)
                                except Exception:
                                    pass
                    elif isinstance(item, ast.AnnAssign):
                        # Extract typed class attributes
                        if isinstance(item.target, ast.Name):
                            try:
                                attr_info = {
                                    'name': item.target.id,
                                    'type': ast.unparse(item.annotation) if item.annotation else None,
                                    'value': ast.unparse(item.value)[:100] if item.value else None,
                                    'is_public': not item.target.id.startswith('_'),
                                }
                                class_info['attributes'].append(attr_info)
                            except Exception:
                                pass
                
                # Sort methods by public first
                class_info['methods'].sort(key=lambda x: (x['is_public'] == False, x['name']))
                
                analysis['classes'].append(class_info)
            except Exception:
                # Skip classes that can't be parsed
                continue
    
    # Extract top-level functions, constants, enums, exceptions, and main block
    for node in tree.body:
        try:
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'signature': format_function_signature(node),
                    'docstring': extract_docstring(node),
                    'is_public': not node.name.startswith('_'),
                    'decorators': [ast.unparse(d) for d in node.decorator_list] if node.decorator_list else [],
                }
                analysis['functions'].append(func_info)
            elif isinstance(node, ast.AsyncFunctionDef):
                func_info = {
                    'name': node.name,
                    'signature': format_function_signature(node),
                    'docstring': extract_docstring(node),
                    'is_public': not node.name.startswith('_'),
                    'decorators': [ast.unparse(d) for d in node.decorator_list] if node.decorator_list else [],
                }
                analysis['functions'].append(func_info)
            elif isinstance(node, ast.Assign):
                # Extract module-level constants (UPPER_CASE)
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id.isupper() or '_' in target.id.upper():
                            try:
                                value_str = ast.unparse(node.value)
                                # Limit very long values
                                if len(value_str) > 200:
                                    value_str = value_str[:200] + "..."
                                analysis['constants'].append({
                                    'name': target.id,
                                    'value': value_str,
                                })
                            except Exception:
                                pass
            elif isinstance(node, ast.ClassDef):
                # Check if it's an Enum or Exception
                class_name = node.name
                bases = [ast.unparse(b) for b in node.bases]
                
                # Check for Enum
                if any('Enum' in b for b in bases):
                    enum_info = {
                        'name': class_name,
                        'docstring': extract_docstring(node),
                        'members': [],
                    }
                    # Extract enum members
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    try:
                                        value = ast.unparse(item.value)
                                        enum_info['members'].append({
                                            'name': target.id,
                                            'value': value,
                                        })
                                    except Exception:
                                        pass
                    analysis['enums'].append(enum_info)
                
                # Check for Exception
                elif any('Exception' in b or 'Error' in b for b in bases) or 'Error' in class_name or 'Exception' in class_name:
                    exc_info = {
                        'name': class_name,
                        'docstring': extract_docstring(node),
                        'bases': bases,
                    }
                    analysis['exceptions'].append(exc_info)
            elif isinstance(node, ast.AnnAssign):
                # Type aliases (e.g., MyType = SomeClass)
                if isinstance(node.target, ast.Name):
                    try:
                        type_alias = {
                            'name': node.target.id,
                            'type': ast.unparse(node.annotation) if node.annotation else None,
                            'value': ast.unparse(node.value) if node.value else None,
                        }
                        analysis['type_aliases'].append(type_alias)
                    except Exception:
                        pass
            elif isinstance(node, ast.If):
                # Check for main block
                if isinstance(node.test, ast.Compare):
                    try:
                        test_str = ast.unparse(node.test)
                        if "__name__" in test_str and "__main__" in test_str:
                            # Extract main block code (simplified)
                            main_code = []
                            for stmt in node.body[:5]:  # Limit to first 5 statements
                                try:
                                    code_line = ast.unparse(stmt)
                                    if len(code_line) < 500:  # Skip very long lines
                                        main_code.append(code_line)
                                except Exception:
                                    pass
                            if main_code:
                                analysis['main_block'] = '\n'.join(main_code)
                    except Exception:
                        pass
        except Exception:
            # Skip nodes that can't be parsed
            continue
    
    # Remove duplicates from imports
    analysis['imports'] = list(dict.fromkeys(analysis['imports']))
    
    # Sort functions by public first, then private
    analysis['functions'].sort(key=lambda x: (x['is_public'] == False, x['name']))
    
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
