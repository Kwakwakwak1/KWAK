# CLAUDE.md - Pocket Pick Development Guide

## Commands
```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run single test file
uv run pytest src/mcp_server_pocket_pick/tests/functionality/test_add.py -v

# Run the server
uv run mcp-server-pocket-pick

# Run with custom database location
uv run mcp-server-pocket-pick --database ./database.db
```

## Code Style
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPERCASE for constants
- **Imports**: standard library → third-party → local, prefer specific imports
- **Types**: Use type hints everywhere (Python 3.10+ syntax), leverage Pydantic models
- **Functions**: Clear names, docstrings with Google style (Args/Returns sections)
- **Error handling**: Specific try/except blocks, proper resource cleanup with finally
- **Testing**: pytest fixtures, descriptive test_* function names, test isolation

## Project Structure
- `src/mcp_server_pocket_pick/`: Main package with CLI interface
- `modules/`: Core functionality (constants, data_types, init_db)
- `modules/functionality/`: Command implementations (add, find, list, etc.)
- `tests/`: Test suite mirroring the main package structure