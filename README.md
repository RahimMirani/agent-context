# agent-context

A powerful Python CLI tool that extracts structured context from GitHub repositories, generating comprehensive markdown documentation perfect for AI codebase integration and analysis.

## Features

- 🔍 **Comprehensive Extraction**: Extracts README, directory structure, Python code analysis, example files, and configuration files
- 🐍 **Python Code Analysis**: Uses AST to extract function signatures, class definitions, docstrings, and imports
- 📝 **Well-Formatted Output**: Generates beautifully structured markdown files with organized sections
- 🔐 **Private Repo Support**: Supports private repositories with GitHub token authentication
- ⚡ **Fast & Efficient**: Uses temporary directories with automatic cleanup
- 🎨 **Enhanced CLI**: Beautiful colored output, progress indicators, and verbose mode

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/agent-context.git
cd agent-context

# Install in development mode
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Using pip (when published)

```bash
pip install agent-context
```

## Requirements

- Python 3.8 or higher
- Git (must be installed and available in PATH)

## Usage

### Basic Usage

```bash
# Extract context from a public repository
agent-context https://github.com/user/repo

# Specify output file
agent-context https://github.com/user/repo -o output.md

# Enable verbose mode with progress indicators
agent-context https://github.com/user/repo -v

# Use with private repository (token via CLI)
agent-context https://github.com/user/private-repo --token YOUR_GITHUB_TOKEN

# Use with private repository (token via environment variable)
export GITHUB_TOKEN=your_token_here
agent-context https://github.com/user/private-repo
```

### Command Options

```
Usage: agent-context [OPTIONS] GITHUB_URL

Arguments:
  GITHUB_URL    GitHub repository URL (required)

Options:
  -o, --output TEXT    Output file path (default: agent-context.md)
  -v, --verbose        Enable verbose output with progress indicators
  --token TEXT         GitHub token for private repositories
  --help               Show this message and exit
```

## Supported URL Formats

The tool accepts GitHub URLs in various formats:

- `https://github.com/user/repo`
- `https://github.com/user/repo.git`
- `git@github.com:user/repo.git`
- `github.com/user/repo`

## What Gets Extracted

### 1. Repository Information
- Repository URL and name
- Active branch
- Latest commit hash and message
- Extraction timestamp

### 2. README
- Full README content (prioritizes `.md`, `.txt`, `.rst` formats)
- Preserves original formatting

### 3. Directory Structure
- Complete directory tree visualization
- Shows all files and folders

### 4. Configuration Files
Extracts common configuration files including:
- `requirements.txt`, `package.json`, `pyproject.toml`
- `setup.py`, `Pipfile`, `environment.yml`
- `Dockerfile`, `docker-compose.yml`
- `Makefile`, `CMakeLists.txt`
- `Cargo.toml`, `go.mod`, `Gemfile`
- `tsconfig.json`, `webpack.config.js`
- And many more...

### 5. Python Code Analysis
For each Python file, extracts:
- Module docstrings
- Import statements
- Class definitions with:
  - Class docstrings
  - Inheritance information
  - Method signatures and docstrings
- Function definitions with:
  - Function signatures (including type hints)
  - Function docstrings
  - Parameter information

### 6. Example Files
Finds and extracts files from:
- `examples/`, `example/`
- `demo/`, `demos/`
- `samples/`, `sample/`
- `test/`, `tests/`
- `tutorial/`, `tutorials/`

## Output Format

The generated markdown file includes:

1. **Repository Information** - Metadata about the repository
2. **Table of Contents** - (in verbose mode) Quick navigation
3. **README** - Full README content
4. **Directory Structure** - Visual tree representation
5. **Configuration Files** - All config files with their contents
6. **Python Code Analysis** - Detailed code structure analysis
7. **Example Files** - Grouped by directory with syntax highlighting

## Examples

### Example 1: Basic Extraction

```bash
agent-context https://github.com/python/cpython
```

This creates `agent-context.md` with all extracted content from the CPython repository.

### Example 2: Custom Output with Verbose Mode

```bash
agent-context https://github.com/user/repo -o my-context.md -v
```

Extracts context and saves to `my-context.md` with detailed progress indicators.

### Example 3: Private Repository

```bash
# Method 1: Using CLI flag
agent-context https://github.com/user/private-repo --token ghp_xxxxxxxxxxxx

# Method 2: Using environment variable
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
agent-context https://github.com/user/private-repo
```

## Use Cases

- **AI Codebase Integration**: Provide comprehensive context to AI assistants about external repositories
- **Documentation Generation**: Quickly generate documentation for repositories
- **Code Analysis**: Understand repository structure and Python code organization
- **Onboarding**: Get familiar with new codebases quickly
- **Research**: Extract and analyze code patterns from multiple repositories

## Error Handling

The tool handles various error scenarios gracefully:

- **Invalid URLs**: Validates GitHub URL format before cloning
- **Network Errors**: Clear error messages for connection issues
- **Authentication Failures**: Helpful tips for private repository access
- **Missing Files**: Continues processing even if README or Python files are missing
- **Syntax Errors**: Skips Python files with syntax errors
- **Large Files**: Safely handles large files with size limits

## Limitations

- Currently supports GitHub repositories only
- Python code analysis only (other languages' files are extracted but not analyzed)
- Large repositories may take longer to process
- Binary files are automatically skipped

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Troubleshooting

### Common Issues

**Issue**: `GitCommandError: Authentication failed`
- **Solution**: Ensure you're using a valid GitHub token for private repositories

**Issue**: `Repository not found`
- **Solution**: Check the repository URL and ensure it exists and is accessible

**Issue**: `No module named 'git'`
- **Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: Progress bar not showing
- **Solution**: Use `-v` flag for verbose mode with progress indicators

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

Built with:
- [GitPython](https://github.com/gitpython-developers/GitPython) - Git repository interaction
- [Click](https://click.palletsprojects.com/) - Beautiful command-line interfaces
- [tqdm](https://github.com/tqdm/tqdm) - Progress bars
- [colorama](https://github.com/tartley/colorama) - Cross-platform colored terminal text
