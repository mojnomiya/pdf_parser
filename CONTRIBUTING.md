# Contributing Guidelines

Thank you for your interest in contributing to the Indonesian Bank Statement PDF Parser! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of PDF parsing and Indonesian banking formats

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/indonesian-bank-statement-parser.git
   cd indonesian-bank-statement-parser
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```

4. **Verify setup**
   ```bash
   make test
   ```

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker
- Include Python version, OS, and error messages
- Provide sample PDF files (with sensitive data removed)
- Describe expected vs actual behavior

### Adding Support for New Banks

1. **Create a new parser class**
   ```python
   # pdfparser/parsers/new_bank.py
   from pdfparser.base import BaseBankParser
   
   class NewBankParser(BaseBankParser):
       @property
       def bank_name(self) -> str:
           return "NewBank"
       
       def can_parse(self, pdf_path) -> bool:
           # Implementation
           pass
       
       def parse(self, pdf_path) -> ParseResult:
           # Implementation
           pass
   ```

2. **Add to factory**
   ```python
   # pdfparser/factory.py
   from .parsers.new_bank import NewBankParser
   
   # Add to _parsers list
   ```

3. **Write tests**
   ```python
   # tests/test_new_bank.py
   def test_new_bank_parser():
       # Test implementation
       pass
   ```

4. **Update documentation**
   - Add bank to README.md supported banks list
   - Document any specific requirements

### Code Style

- **Black** for code formatting: `black pdfparser/`
- **flake8** for linting: `flake8 pdfparser/`
- **mypy** for type checking: `mypy pdfparser/`
- **isort** for import sorting: `isort pdfparser/`

Run all checks: `make check`

### Testing

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use pytest fixtures for common test data
- Test with real PDF samples (anonymized)

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=pdfparser --cov-report=html
```

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/add-mandiri-support
   ```

2. **Make your changes**
   - Follow coding standards
   - Add tests
   - Update documentation

3. **Run quality checks**
   ```bash
   make check
   ```

4. **Commit with clear messages**
   ```bash
   git commit -m "feat: add Mandiri bank parser support"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/add-mandiri-support
   ```

6. **PR Requirements**
   - Clear description of changes
   - Link to related issues
   - All CI checks passing
   - Code review approval

## Commit Message Format

Use conventional commits:

- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `test:` adding tests
- `refactor:` code refactoring
- `style:` formatting changes
- `chore:` maintenance tasks

## Code Review Guidelines

### For Contributors
- Keep PRs focused and small
- Write clear commit messages
- Add tests for new functionality
- Update documentation as needed

### For Reviewers
- Be constructive and respectful
- Focus on code quality and maintainability
- Check for proper testing
- Verify documentation updates

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release PR
4. Tag release after merge
5. GitHub Actions handles PyPI publishing

## Getting Help

- **GitHub Discussions** for questions
- **GitHub Issues** for bugs
- **Email** maintainers for security issues

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

Thank you for contributing to make Indonesian bank statement parsing better for everyone!