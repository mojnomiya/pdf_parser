"""
Example implementation of a new bank parser.

This shows how to extend the parser to support additional Indonesian banks.
"""

import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

import pdfplumber

from pdfparser.base import BaseBankParser, StatementMetadata, Transaction, ParseResult


class MandiriParser(BaseBankParser):
    """
    Example parser for Bank Mandiri statements.
    
    This is a template showing how to implement support for additional banks.
    """
    
    @property
    def bank_name(self) -> str:
        """Return the name of the bank this parser handles."""
        return "Mandiri"
    
    def can_parse(self, pdf_path: Union[str, Path]) -> bool:
        """Check if this parser can handle the given PDF."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if not pdf.pages:
                    return False
                
                text = pdf.pages[0].extract_text() or ""
                # Look for Mandiri-specific indicators
                mandiri_indicators = [
                    "PT BANK MANDIRI",
                    "BANK MANDIRI",
                    "Mandiri",
                    # Add more specific patterns here
                ]
                return any(indicator in text for indicator in mandiri_indicators)
        except Exception:
            return False
    
    def parse(self, pdf_path: Union[str, Path]) -> ParseResult:
        """
        Parse a Mandiri bank statement PDF.
        
        Args:
            pdf_path: Path to the PDF file.
            
        Returns:
            ParseResult containing metadata and transactions.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        with pdfplumber.open(pdf_path) as pdf:
            # Extract metadata from first page header
            metadata = self._extract_metadata(pdf.pages[0])
            metadata.bank_name = self.bank_name
            
            # Extract transactions from all pages
            transactions = []
            for page in pdf.pages:
                page_transactions = self._extract_transactions(page)
                transactions.extend(page_transactions)
            
            # Extract summary from last page
            summary = self._extract_summary(pdf.pages[-1])
            
        return ParseResult(
            metadata=metadata,
            transactions=transactions,
            summary=summary
        )
    
    def _extract_metadata(self, page) -> StatementMetadata:
        """Extract metadata from the first page header section."""
        text = page.extract_text()
        if not text:
            return StatementMetadata()
        
        metadata = StatementMetadata()
        
        # Implement Mandiri-specific metadata extraction
        # This would need to be customized based on Mandiri's PDF format
        
        # Example patterns (adjust based on actual Mandiri format):
        # Statement Date
        date_match = re.search(r'Tanggal Cetak\s*:\s*(\d{2}/\d{2}/\d{4})', text)
        if date_match:
            metadata.statement_date = date_match.group(1)
        
        # Account Number
        account_match = re.search(r'No\. Rekening\s*:\s*(\S+)', text)
        if account_match:
            metadata.account_number = account_match.group(1)
        
        # Add more Mandiri-specific parsing here...
        
        return metadata
    
    def _extract_transactions(self, page) -> List[Transaction]:
        """Extract transactions from a page."""
        # Implement Mandiri-specific transaction extraction
        # This would need to be customized based on Mandiri's table format
        
        transactions = []
        
        # Example implementation - adjust based on actual format
        tables = page.extract_tables()
        for table in tables:
            for row in table[1:]:  # Skip header
                if len(row) >= 6:  # Ensure enough columns
                    try:
                        transaction = Transaction(
                            transaction_date=row[0] or "",
                            transaction_time=None,  # If Mandiri doesn't have time
                            description=row[1] or "",
                            teller_user_id=row[2] or "",
                            debit=self._parse_amount(row[3] or "0"),
                            credit=self._parse_amount(row[4] or "0"),
                            balance=self._parse_amount(row[5] or "0")
                        )
                        transactions.append(transaction)
                    except (ValueError, IndexError):
                        continue
        
        return transactions
    
    def _extract_summary(self, page) -> Dict[str, Any]:
        """Extract summary information from the last page."""
        # Implement Mandiri-specific summary extraction
        return {}


# To use this new parser, you would:
# 1. Add it to the ParserFactory in factory.py
# 2. Import it in __init__.py
# 3. Test it with actual Mandiri PDFs

if __name__ == "__main__":
    # Example usage
    parser = MandiriParser()
    # result = parser.parse("mandiri_statement.pdf")
    # result.export_to_csv("mandiri_metadata.csv", "mandiri_transactions.csv")