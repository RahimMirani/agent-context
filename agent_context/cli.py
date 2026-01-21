"""CLI interface for agent-context."""

import os
import sys
from pathlib import Path

import click
from colorama import Fore, Style, init
from git.exc import GitCommandError
from tqdm import tqdm

from .cloner import clone_repository, get_repository_info, validate_github_url
from .extractor import extract_all_content
from .markdown_generator import generate_markdown, write_markdown
from .python_analyzer import analyze_all_python_files, analyze_python_file
from .utils import find_files_by_pattern, temporary_directory

# Initialize colorama for Windows support
init(autoreset=True)


def print_success(message: str) -> None:
    """Print success message in green."""
    click.echo(f"{Fore.GREEN}✓{Style.RESET_ALL} {message}")


def print_error(message: str) -> None:
    """Print error message in red."""
    click.echo(f"{Fore.RED}✗{Style.RESET_ALL} {message}", err=True)


def print_info(message: str) -> None:
    """Print info message."""
    click.echo(f"{Fore.CYAN}ℹ{Style.RESET_ALL} {message}")


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    click.echo(f"{Fore.YELLOW}⚠{Style.RESET_ALL} {message}")


@click.command()
@click.argument('github_url', type=str)
@click.option(
    '-o', '--output',
    type=click.Path(),
    default=None,
    help='Output file path (if not provided, will prompt for filename)'
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Enable verbose output with progress indicators'
)
@click.option(
    '--token',
    type=str,
    default=None,
    help='GitHub token for private repositories (or set GITHUB_TOKEN env var)'
)
def main(github_url: str, output: str, verbose: bool, token: str) -> None:
    """
    Extract structured context from a GitHub repository.
    
    This tool clones a GitHub repository, extracts README, directory structure,
    Python code analysis, example files, and configuration files, then outputs
    everything as a well-formatted markdown file.
    
    \b
    Examples:
        agent-context https://github.com/user/repo
        agent-context https://github.com/user/repo -o output.md
        agent-context https://github.com/user/repo -v --token YOUR_TOKEN
    """
    try:
        # Validate GitHub URL
        if not validate_github_url(github_url):
            print_error(f"Invalid GitHub URL: {github_url}")
            print_info("URL should be in format: https://github.com/user/repo")
            sys.exit(1)
        
        # Get token from environment if not provided
        if not token:
            token = os.getenv('GITHUB_TOKEN')
        
        # Handle output path - always prompt for filename suffix
        if output:
            output_path = Path(output)
        else:
            # Always ask for suffix to add after "agent-context"
            suffix_input = click.prompt(
                "Enter text to add after 'agent-context' for the filename (e.g., '-v2', '-repo-name')"
            )
            output_path = Path(f"agent-context-{suffix_input}.md")
        
        # If file exists, ask for different suffix
        if output_path.exists():
            print_warning(f"File {output_path} already exists.")
            suffix_input = click.prompt(
                "Enter different text to add after 'agent-context' (e.g., '-v2', '-repo-name')"
            )
            output_path = Path(f"agent-context-{suffix_input}.md")
        
        print_info(f"Output file: {output_path}")
        
        if verbose:
            print_info(f"Starting extraction for: {github_url}")
            print_info(f"Output file: {output_path}")
        
        # Step 1: Clone repository
        if verbose:
            click.echo(f"\n{Fore.CYAN}[1/5]{Style.RESET_ALL} Cloning repository...")
        
        with temporary_directory() as temp_dir:
            try:
                repo_path = clone_repository(
                    github_url=github_url,
                    output_dir=temp_dir,
                    token=token
                )
                print_success(f"Repository cloned successfully")
            except GitCommandError as e:
                print_error(f"Failed to clone repository: {str(e)}")
                if "Authentication failed" in str(e) and not token:
                    print_info("Tip: Use --token option or set GITHUB_TOKEN environment variable for private repos")
                sys.exit(1)
            except Exception as e:
                print_error(f"Unexpected error during clone: {str(e)}")
                sys.exit(1)
            
            # Get repository info
            repo_info = get_repository_info(repo_path)
            
            # Step 2: Extract content
            if verbose:
                click.echo(f"\n{Fore.CYAN}[2/5]{Style.RESET_ALL} Extracting content...")
            
            try:
                extracted = extract_all_content(repo_path)
                print_success("Content extracted")
            except Exception as e:
                print_error(f"Failed to extract content: {str(e)}")
                sys.exit(1)
            
            # Step 3: Analyze Python files
            if verbose:
                click.echo(f"\n{Fore.CYAN}[3/5]{Style.RESET_ALL} Analyzing Python files...")
            
            try:
                python_files = find_files_by_pattern(repo_path, ['*.py'])
                if python_files:
                    python_analyses = []
                    if verbose:
                        with tqdm(total=len(python_files), desc="Analyzing", unit="file") as pbar:
                            for py_file in python_files:
                                analysis = analyze_python_file(py_file, repo_path)
                                if analysis:
                                    python_analyses.append(analysis)
                                pbar.update(1)
                    else:
                        python_analyses = analyze_all_python_files(repo_path)
                    print_success(f"Analyzed {len(python_analyses)} Python files")
                else:
                    python_analyses = []
                    print_warning("No Python files found")
            except Exception as e:
                print_error(f"Failed to analyze Python files: {str(e)}")
                python_analyses = []
            
            # Step 4: Generate markdown
            if verbose:
                click.echo(f"\n{Fore.CYAN}[4/5]{Style.RESET_ALL} Generating markdown...")
            
            try:
                markdown_content = generate_markdown(
                    repo_info=repo_info,
                    github_url=github_url,
                    readme_data=extracted['readme'],
                    directory_structure=extracted['directory_structure'],
                    config_files=extracted['config_files'],
                    python_analyses=python_analyses,
                    example_files=extracted['example_files'],
                    verbose=verbose
                )
                print_success("Markdown generated")
            except Exception as e:
                print_error(f"Failed to generate markdown: {str(e)}")
                sys.exit(1)
            
            # Step 5: Write output
            if verbose:
                click.echo(f"\n{Fore.CYAN}[5/5]{Style.RESET_ALL} Writing output file...")
            
            try:
                write_markdown(markdown_content, output_path)
                print_success(f"Output written to: {output_path}")
            except Exception as e:
                print_error(f"Failed to write output file: {str(e)}")
                sys.exit(1)
        
        # Summary
        if verbose:
            click.echo(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
            click.echo(f"{Fore.GREEN}Summary:{Style.RESET_ALL}")
            click.echo(f"  Repository: {repo_info.get('name', 'N/A')}")
            click.echo(f"  README: {'Found' if extracted['readme'] else 'Not found'}")
            click.echo(f"  Config files: {len(extracted['config_files'])}")
            click.echo(f"  Python files analyzed: {len(python_analyses)}")
            click.echo(f"  Example files: {len(extracted['example_files'])}")
            click.echo(f"  Output: {output_path.absolute()}")
            click.echo(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
        else:
            print_success(f"Context extracted successfully to {output_path}")
    
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
