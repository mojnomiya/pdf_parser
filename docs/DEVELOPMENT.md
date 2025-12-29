# Developer Guide

This document provides technical details for developers working on the Indonesian Bank Statement PDF Parser.

## Project Structure

```
pdf_parser/
├── pdfparser/               # Main package
│   ├── __init__.py          # Package exports
│   └── parser.py            # Core parsing logic
├── dev_scripts/             # Development/analysis scripts
│   ├── analyze_pdf.py       # Full PDF text and table extraction
│   ├── analyze_metadata.py  # First page metadata analysis
│   ├── analyze_tables.py    # Basic table extraction
│   ├── analyze_tables_settings.py  # Table extraction with strategies
│   ├── analyze_bbox.py      # Header word bounding boxes
│   ├── analyze_row_bbox.py  # Row word bounding boxes
│   ├── analyze_columns.py   # Column separator analysis
│   ├── check_transactions.py # Transaction verification
│   ├── check_y_positions.py # Y-position debugging
│   └── test_parser.py       # Parser test script
├── docs/                    # Documentation
│   └── DEVELOPMENT.md       # This file
├── cli.py                   # Command-line interface
├── requirements.txt         # Python dependencies
├── README.md                # User documentation
└── .gitignore               # Git ignore rules
```

## Architecture

### Core Components

1. **`PDFParser`** - Main parser class
   - `parse(pdf_path)` - Parses a PDF and returns `ParseResult`
   - Handles multi-page documents
   - Dynamically detects table positions

2. **`ParseResult`** - Container for parsed data
   - `metadata` - `StatementMetadata` object
   - `transactions` - List of `Transaction` objects
   - `summary` - Dictionary with totals
   - `export_to_csv()` - Export helper

3. **`StatementMetadata`** - Account/statement info
   - Statement date, transaction period
   - Account number, product name, currency
   - Business unit information

4. **`Transaction`** - Single transaction record
   - Date, time, description
   - Teller/User ID
   - Debit, credit, balance

### Parsing Strategy

The parser uses **word-level extraction** with coordinate-based column detection:

1. **Extract all words** from the page with their bounding boxes
2. **Find table header** by locating "Tanggal" in the date column area
3. **Group words by Y-position** to form logical lines
4. **Assign words to columns** based on X-coordinates:
   - Column boundaries: `[0, 105, 290, 360, 470, 570, 700]`
   - Columns: Date | Description | Teller | Debit | Credit | Balance
5. **Detect new transactions** by date pattern (`DD/MM/YY`)
6. **Handle edge cases**:
   - Multi-line descriptions (continuation lines)
   - Time-only transactions (missing date)
   - Summary section detection

## Development Scripts

Run from the `dev_scripts/` directory:

```bash
cd dev_scripts

# View raw PDF text and tables
../venv/bin/python analyze_pdf.py

# Check header positions (for column boundary tuning)
../venv/bin/python analyze_bbox.py

# Verify all transactions are being extracted
../venv/bin/python check_transactions.py

# Test the parser
../venv/bin/python test_parser.py
```

## Adding Support for New Bank Formats

1. **Analyze the PDF structure**:
   ```bash
   cd dev_scripts
   ../venv/bin/python analyze_pdf.py
   ../venv/bin/python analyze_bbox.py
   ```

2. **Identify column boundaries** using word X-coordinates

3. **Create a new parser class** or extend `PDFParser` with:
   - Custom column boundaries
   - Bank-specific metadata extraction
   - Modified transaction detection patterns

4. **Update the configuration** to select the appropriate parser

## Key Methods

### `_find_table_start_y(words)`
Dynamically finds where the transaction table begins by locating the header row.

### `_group_words_by_line(words)`
Groups words into lines based on Y-position (tolerance: 5px).

### `_parse_transaction_lines(lines)`
Converts grouped lines into `Transaction` objects. Handles:
- New transaction detection (date pattern)
- Time-only transactions (edge case)
- Continuation lines (description overflow)
- Summary section detection (stop parsing)

### `_parse_transaction_line(words)`
Extracts fields from a single transaction line by assigning words to columns based on X-coordinates.

## Testing

### Validation Checks

The parser passes these validation tests:
- ✅ Total Debit = Summary Total Debit
- ✅ Total Credit = Summary Total Credit
- ✅ Last Transaction Balance = Closing Balance

### Running Tests

```bash
cd dev_scripts
../venv/bin/python test_parser.py
```

### Manual Validation

```python
from pdfparser import parse_pdf

result = parse_pdf('Example_statement.pdf')

# Check totals
total_debit = sum(t.debit for t in result.transactions)
total_credit = sum(t.credit for t in result.transactions)

print(f"Calculated Debit: {total_debit:,.2f}")
print(f"Summary Debit: {result.summary['Total Debit']:,.2f}")
print(f"Match: {total_debit == result.summary['Total Debit']}")
```

## Performance

- **Processing time**: < 1 second for 3-page PDF
- **Memory**: Minimal, processes page-by-page
- **No OCR overhead**: Native text extraction only

## Dependencies

| Package | Purpose |
|---------|---------|
| pdfplumber | PDF text extraction with coordinates |
| pandas | DataFrame operations and CSV export |

## Known Limitations

1. **Text-based PDFs only** - Scanned documents will not work
2. **BRI format specific** - Other bank formats need new parsers
3. **Fixed column layout** - Significant layout changes require adjustment
