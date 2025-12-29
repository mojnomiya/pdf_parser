# Indonesian Bank Statement PDF Parser

A high-performance Python module for extracting structured data from Indonesian bank statement PDFs supporting multiple bank formats.

## Features

- **Multi-bank support** - Extensible architecture for different Indonesian banks
- **Native PDF parsing** - No OCR required, works with text-based PDFs
- **Fast processing** - Under 1 second for multi-page statements
- **Structured output** - Exports to CSV files and pandas DataFrames
- **Clean Python API** - Both function-based and class-based interfaces
- **Type hints** - Full type annotation support
- **CLI tool** - Command-line interface for batch processing

## Supported Banks

- **BRI (Bank Rakyat Indonesia)** - Full support
- **Extensible** - Easy to add support for other banks

## Installation

### From PyPI (recommended)

```bash
pip install indonesian-bank-statement-parser
```

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd pdf_parser

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or .\venv\Scripts\activate on Windows

# Install in development mode
pip install -e ".[dev]"
```

## Quick Start

### Python API

**Auto-detection (recommended):**
```python
from pdfparser import parse_pdf

# Parse any supported bank statement
result = parse_pdf("statement.pdf")
result.export_to_csv("metadata.csv", "transactions.csv")
```

**Using factory for auto-detection:**
```python
from pdfparser import ParserFactory

factory = ParserFactory()
result = factory.parse("statement.pdf")
print(f"Detected bank: {result.metadata.bank_name}")
```

**Specific bank parser:**
```python
from pdfparser import BRIParser

parser = BRIParser()
result = parser.parse("bri_statement.pdf")

# Access parsed data
print(f"Bank: {result.metadata.bank_name}")
print(f"Statement Date: {result.metadata.statement_date}")
print(f"Found {len(result.transactions)} transactions")

# Export to CSV
result.export_to_csv("metadata.csv", "transactions.csv")
```

**Access data as pandas DataFrame:**
```python
result = parse_pdf("statement.pdf")

metadata_df = result.get_metadata_df()
transactions_df = result.get_transactions_df()

print(transactions_df.head())
```

**Check supported banks:**
```python
from pdfparser import get_supported_banks

print("Supported banks:", get_supported_banks())
```

### Using the Factory Pattern

```python
from pdfparser import ParserFactory

# Create factory instance
factory = ParserFactory()

# Auto-detect and parse
result = factory.parse("unknown_bank_statement.pdf")

# Get specific parser
parser = factory.get_parser("bri_statement.pdf")
result = parser.parse("bri_statement.pdf")

# List all supported banks
banks = factory.list_supported_banks()
print(f"Supported banks: {banks}")
```

### Command Line

```bash
# Basic usage
bank-statement-parser statement.pdf

# Custom output paths
bank-statement-parser statement.pdf -o my_metadata.csv my_transactions.csv

# Verbose mode (shows parsed details)
bank-statement-parser statement.pdf --verbose

# Show help
bank-statement-parser --help
```

## Output Structure

### Metadata CSV

| Field | Description |
|-------|-------------|
| Statement Date | Date when the statement was generated |
| Transaction Period Start | Start date of the transaction period |
| Transaction Period End | End date of the transaction period |
| Account Number | Bank account number |
| Product Name | Type of account (e.g., Britama-IDR) |
| Currency | Transaction currency (e.g., IDR) |
| Business Unit | Branch/unit name |
| Bank Name | Name of the bank |

### Transactions CSV

| Field | Description |
|-------|-------------|
| Transaction Date | Date of the transaction (DD/MM/YY) |
| Transaction Time | Time of the transaction (HH:MM:SS) |
| Description | Full transaction description |
| Teller/User ID | Teller or system ID |
| Debit | Amount debited (0.00 if credit) |
| Credit | Amount credited (0.00 if debit) |
| Balance | Account balance after transaction |

## Adding Support for New Banks

The parser is designed to be easily extensible. See [examples/mandiri_parser_example.py](examples/mandiri_parser_example.py) for a template on how to add support for additional banks.

### Steps to add a new bank:

1. Create a new parser class inheriting from `BaseBankParser`
2. Implement the required methods (`parse`, `can_parse`, `bank_name`)
3. Add the parser to the factory in `factory.py`
4. Write tests for the new parser

## Development

### Setup Development Environment

```bash
# Clone and install in development mode
git clone <repository-url>
cd pdf_parser
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pdfparser

# Run specific test file
pytest tests/test_parser.py
```

### Code Quality

```bash
# Format code
black pdfparser/

# Check linting
flake8 pdfparser/

# Type checking
mypy pdfparser/

# Run all pre-commit hooks
pre-commit run --all-files
```

## Requirements

- Python 3.8+
- pdfplumber >= 0.7.0
- pandas >= 1.3.0

## Documentation

- [Developer Guide](docs/DEVELOPMENT.md) - For contributors and developers
- [API Reference](docs/API.md) - Detailed API documentation

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) and submit pull requests for any improvements.

## License

MIT License - see [LICENSE](LICENSE) file for details.
