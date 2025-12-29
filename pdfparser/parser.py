"""
BRI Bank statement parser implementation.
"""

import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

import pdfplumber

from .base import BaseBankParser, StatementMetadata, Transaction, ParseResult


class BRIParser(BaseBankParser):
    """
    Parser for BRI (Bank Rakyat Indonesia) bank statement PDFs.
    
    Example usage:
        parser = BRIParser()
        result = parser.parse("statement.pdf")
        result.export_to_csv("metadata.csv", "transactions.csv")
    """
    
    # Column boundaries for transaction table (x coordinates)
    # Columns: Date | Description | Teller | Debit | Credit | Balance
    COLUMN_BOUNDARIES = [0, 105, 290, 360, 470, 570, 700]
    
    # Y coordinate where transaction table starts (after header row)
    TABLE_START_Y = 340
    
    @property
    def bank_name(self) -> str:
        """Return the name of the bank this parser handles."""
        return "BRI"
        
    def can_parse(self, pdf_path: Union[str, Path]) -> bool:
        """Check if this parser can handle the given PDF."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if not pdf.pages:
                    return False
                
                text = pdf.pages[0].extract_text() or ""
                # Look for BRI-specific indicators
                bri_indicators = [
                    "PT. BANK RAKYAT INDONESIA",
                    "BRI",
                    "Britama",
                    "Unit Kerja",
                    "Tanggal Laporan"
                ]
                return any(indicator in text for indicator in bri_indicators)
        except Exception:
            return False
    
    def parse(self, pdf_path: Union[str, Path]) -> ParseResult:
        """
        Parse a BRI bank statement PDF.
        
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
    
    def _extract_metadata(self, page: Any) -> StatementMetadata:
        """Extract metadata from the first page header section."""
        text = page.extract_text()
        if not text:
            return StatementMetadata()
        
        metadata = StatementMetadata()
        
        # Statement Date: Tanggal Laporan : 03/06/25
        date_match = re.search(r'Tanggal Laporan\s*:\s*(\d{2}/\d{2}/\d{2})', text)
        if date_match:
            metadata.statement_date = date_match.group(1)
        
        # Transaction Period: Periode Transaksi : 01/05/25 - 31/05/25
        period_match = re.search(
            r'Periode Transaksi\s*:\s*(\d{2}/\d{2}/\d{2})\s*-\s*(\d{2}/\d{2}/\d{2})', 
            text
        )
        if period_match:
            metadata.transaction_period_start = period_match.group(1)
            metadata.transaction_period_end = period_match.group(2)
        
        # Account Number: No. Rekening :
        # Note: Account number might be redacted in the sample
        account_match = re.search(r'No\. Rekening\s*:\s*(\S+)', text)
        if account_match:
            val = account_match.group(1)
            if val not in ["Unit", "Kerja"]:  # Skip if parsing error
                metadata.account_number = val
        
        # Product Name: Nama Produk : Britama-IDR
        product_match = re.search(r'Nama Produk\s*:\s*(\S+)', text)
        if product_match:
            metadata.product_name = product_match.group(1)
        
        # Currency: Valuta : IDR
        currency_match = re.search(r'Valuta\s*:\s*(\w+)', text)
        if currency_match:
            metadata.currency = currency_match.group(1)
        
        # Business Unit: Unit Kerja : KCP SUCI
        unit_match = re.search(r'Unit Kerja\s*:\s*(.+?)(?:\n|Alamat)', text)
        if unit_match:
            metadata.business_unit = unit_match.group(1).strip()
        
        return metadata
    
    def _extract_transactions(self, page: Any) -> List[Transaction]:
        """Extract transactions from a page using word-level parsing."""
        words = page.extract_words()
        if not words:
            return []
        
        # Dynamically find the transaction table start position
        # Look for the header row containing "Tanggal" followed by transaction data
        table_start_y = self._find_table_start_y(words)
        
        # Filter words that are below the header (in the transaction area)
        transaction_words = [w for w in words if w['top'] > table_start_y]
        
        if not transaction_words:
            return []
        
        # Group words by their y position (same line)
        lines = self._group_words_by_line(transaction_words)
        
        # Parse lines into transactions
        transactions = self._parse_transaction_lines(lines)
        
        return transactions
    
    def _find_table_start_y(self, words: List[Dict]) -> float:
        """Find the Y position where the transaction table starts."""
        # Find the header row (contains "Tanggal" at x < 100)
        header_y = None
        for word in words:
            if word['text'] == 'Tanggal' and word['x0'] < 100:
                header_y = word['top']
                break
        
        if header_y is not None:
            # Transaction data starts after the header row
            # Header row + English translation + some margin
            return header_y + 15  # Small margin to skip header rows
        
        # Fallback to default if header not found
        return self.TABLE_START_Y
    
    def _group_words_by_line(self, words: List[Dict]) -> List[List[Dict]]:
        """Group words into lines based on their y position."""
        if not words:
            return []
        
        # Sort by y position then x position
        sorted_words = sorted(words, key=lambda w: (w['top'], w['x0']))
        
        lines = []
        current_line = [sorted_words[0]]
        current_y = sorted_words[0]['top']
        
        for word in sorted_words[1:]:
            # If word is on same line (within tolerance)
            if abs(word['top'] - current_y) < 5:
                current_line.append(word)
            else:
                lines.append(current_line)
                current_line = [word]
                current_y = word['top']
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _parse_transaction_lines(self, lines: List[List[Dict]]) -> List[Transaction]:
        """Parse grouped lines into Transaction objects."""
        transactions = []
        current_transaction = None
        stop_processing = False
        last_date = None
        
        for line_words in lines:
            if stop_processing:
                break
                
            # Check if we've reached the summary section
            line_text = " ".join(w['text'] for w in line_words)
            if "Saldo Awal" in line_text or "Opening Balance" in line_text:
                stop_processing = True
                continue
            
            # Check if this line starts a new transaction (has date/time pattern)
            first_word = line_words[0]['text'] if line_words else ''
            
            # Date pattern: DD/MM/YY
            is_new_transaction = bool(re.match(r'\d{2}/\d{2}/\d{2}', first_word))
            
            # Also check for time-only pattern (H:MM or HH:MM) which indicates a
            # transaction with missing date (edge case in some statements)
            is_time_only_transaction = bool(re.match(r'^\d{1,2}:\d{2}$', first_word))
            
            if is_new_transaction or is_time_only_transaction:
                # Save previous transaction if exists and is valid
                if current_transaction and self._is_valid_transaction(current_transaction):
                    transactions.append(current_transaction)
                
                # Start new transaction
                current_transaction = self._parse_transaction_line(line_words)
                
                # For time-only transactions, use the last known date
                if is_time_only_transaction and last_date:
                    current_transaction.transaction_date = last_date
                    current_transaction.transaction_time = first_word
                elif is_new_transaction:
                    last_date = current_transaction.transaction_date
            elif current_transaction:
                # This is a continuation line - append to description
                continuation_text = self._get_description_from_line(line_words)
                if continuation_text:
                    current_transaction.description += " " + continuation_text
        
        # Don't forget the last transaction
        if current_transaction and self._is_valid_transaction(current_transaction):
            transactions.append(current_transaction)
        
        return transactions
    
    def _is_valid_transaction(self, transaction: Transaction) -> bool:
        """Check if a transaction is valid (not empty)."""
        # A valid transaction must have a date and at least some monetary value
        if not transaction.transaction_date or not transaction.transaction_date.strip():
            return False
        # Must have at least one of: debit, credit, or balance > 0
        if transaction.debit == 0.0 and transaction.credit == 0.0 and transaction.balance == 0.0:
            return False
        return True
    
    def _parse_transaction_line(self, words: List[Dict]) -> Transaction:
        """Parse a single transaction line from words."""
        # Initialize with defaults
        date = ""
        time = None
        description = ""
        teller = ""
        debit = 0.0
        credit = 0.0
        balance = 0.0
        
        # Column boundaries
        date_end = 105
        desc_end = 290
        teller_end = 360
        debit_end = 470
        credit_end = 570
        
        date_words = []
        desc_words = []
        teller_words = []
        debit_words = []
        credit_words = []
        balance_words = []
        
        for word in words:
            x = word['x0']
            text = word['text']
            
            if x < date_end:
                date_words.append(text)
            elif x < desc_end:
                desc_words.append(text)
            elif x < teller_end:
                teller_words.append(text)
            elif x < debit_end:
                debit_words.append(text)
            elif x < credit_end:
                credit_words.append(text)
            else:
                balance_words.append(text)
        
        # Parse date and time (format: DD/MM/YY HH:MM:SS)
        if date_words:
            date_parts = date_words[0].split()
            date = date_parts[0] if date_parts else ""
            if len(date_words) > 1:
                time = date_words[1]
            elif len(date_parts) > 1:
                time = date_parts[1]
        
        # Description
        description = " ".join(desc_words)
        
        # Teller/User ID
        teller = " ".join(teller_words)
        
        # Parse amounts
        debit = self._parse_amount(" ".join(debit_words))
        credit = self._parse_amount(" ".join(credit_words))
        balance = self._parse_amount(" ".join(balance_words))
        
        return Transaction(
            transaction_date=date,
            transaction_time=time,
            description=description,
            teller_user_id=teller,
            debit=debit,
            credit=credit,
            balance=balance
        )
    
    def _get_description_from_line(self, words: List[Dict]) -> str:
        """Extract description text from a continuation line."""
        desc_words = []
        for word in words:
            # Only get words in description column area
            if 0 <= word['x0'] < 360:  # Extended to include any overflow
                desc_words.append(word['text'])
        return " ".join(desc_words)
    

    
    def _extract_summary(self, page: Any) -> Dict[str, Any]:
        """Extract summary information from the last page."""
        summary = {}
        
        # Try table extraction first (more reliable)
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                if not row:
                    continue
                row_text = str(row[0]) if row[0] else ""
                
                # Opening Balance row
                if "Saldo Awal" in row_text or "Opening Balance" in row_text:
                    # Next row should have the values
                    continue
                    
                # Summary values row (4 numeric columns)
                if len(row) >= 4:
                    try:
                        # Check if this looks like a values row
                        first_val = self._parse_amount(str(row[0]))
                        if first_val > 0:
                            summary["Opening Balance"] = first_val
                            if row[1]:
                                summary["Total Debit"] = self._parse_amount(str(row[1]))
                            if row[2]:
                                summary["Total Credit"] = self._parse_amount(str(row[2]))
                            if row[3]:
                                summary["Closing Balance"] = self._parse_amount(str(row[3]))
                    except (ValueError, IndexError):
                        pass
                
                # Balance in words
                if "RUPIAH" in row_text:
                    summary["Balance In Words"] = row_text.strip()
        
        return summary


def parse_pdf(pdf_path: Union[str, Path], config: Optional[Dict[str, Any]] = None) -> ParseResult:
    """
    Convenience function to parse a bank statement PDF using the legacy BRI parser.
    
    Args:
        pdf_path: Path to the PDF file.
        config: Optional configuration dictionary.
        
    Returns:
        ParseResult containing metadata and transactions.
        
    Example:
        result = parse_pdf("statement.pdf")
        result.export_to_csv("metadata.csv", "transactions.csv")
    """
    parser = BRIParser(config)
    return parser.parse(pdf_path)
