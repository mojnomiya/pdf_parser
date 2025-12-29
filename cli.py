#!/usr/bin/env python3
"""
Command-line interface for the Indonesian Bank Statement PDF Parser.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from pdfparser import parse_pdf, __version__


def main():
    parser = argparse.ArgumentParser(
        description="Parse Indonesian bank statement PDFs and export to CSV.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py statement.pdf
  python cli.py statement.pdf -o metadata.csv transactions.csv
  python cli.py statement.pdf --verbose
        """
    )
    
    parser.add_argument(
        "pdf_file",
        help="Path to the bank statement PDF file"
    )
    
    parser.add_argument(
        "-o", "--output",
        nargs=2,
        metavar=("METADATA_CSV", "TRANSACTIONS_CSV"),
        default=["metadata.csv", "transactions.csv"],
        help="Output CSV file paths (default: metadata.csv transactions.csv)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed parsing results"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    
    if not pdf_path.suffix.lower() == ".pdf":
        print(f"Warning: File may not be a PDF: {pdf_path}", file=sys.stderr)
    
    try:
        # Parse the PDF
        if args.verbose:
            print(f"Parsing: {pdf_path}")
        
        result = parse_pdf(str(pdf_path))
        
        # Display results if verbose
        if args.verbose:
            print(f"\nMetadata:")
            for key, value in result.metadata.to_dict().items():
                if value:
                    print(f"  {key}: {value}")
            
            print(f"\nTransactions: {len(result.transactions)} found")
            
            print(f"\nSummary:")
            for key, value in result.summary.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:,.2f}")
                else:
                    print(f"  {key}: {value}")
        
        # Export to CSV
        metadata_path, transactions_path = args.output
        result.export_to_csv(metadata_path, transactions_path)
        
        print(f"Exported metadata to: {metadata_path}")
        print(f"Exported transactions to: {transactions_path}")
        
    except Exception as e:
        print(f"Error parsing PDF: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
