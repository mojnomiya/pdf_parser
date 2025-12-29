"""Tests for BRI parser functionality."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from pdfparser import BRIParser, parse_pdf, get_supported_banks
from pdfparser.base import StatementMetadata, Transaction, ParseResult


class TestBRIParser:
    """Test cases for BRIParser class."""
    
    def test_bank_name(self):
        """Test that parser returns correct bank name."""
        parser = BRIParser()
        assert parser.bank_name == "BRI"
    
    def test_parse_amount_valid(self):
        """Test amount parsing with valid inputs."""
        parser = BRIParser()
        assert parser._parse_amount("1,234.56") == 1234.56
        assert parser._parse_amount("1234") == 1234.0
        assert parser._parse_amount("0.00") == 0.0
    
    def test_parse_amount_invalid(self):
        """Test amount parsing with invalid inputs."""
        parser = BRIParser()
        assert parser._parse_amount("") == 0.0
        assert parser._parse_amount("invalid") == 0.0
        assert parser._parse_amount(None) == 0.0
    
    @patch('pdfplumber.open')
    def test_can_parse_bri_pdf(self, mock_open):
        """Test that parser can identify BRI PDFs."""
        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "PT. BANK RAKYAT INDONESIA Tanggal Laporan"
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        parser = BRIParser()
        assert parser.can_parse("dummy.pdf") is True
    
    @patch('pdfplumber.open')
    def test_cannot_parse_non_bri_pdf(self, mock_open):
        """Test that parser rejects non-BRI PDFs."""
        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Some other bank statement"
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        parser = BRIParser()
        assert parser.can_parse("dummy.pdf") is False


class TestFactoryFunctions:
    """Test cases for factory functions."""
    
    def test_get_supported_banks(self):
        """Test that supported banks list includes BRI."""
        banks = get_supported_banks()
        assert "BRI" in banks
        assert isinstance(banks, list)
    
    def test_parse_pdf_function_exists(self):
        """Test that parse_pdf function is available."""
        assert callable(parse_pdf)


class TestDataClasses:
    """Test cases for data classes."""
    
    def test_statement_metadata_to_dict(self):
        """Test StatementMetadata to_dict conversion."""
        metadata = StatementMetadata(
            statement_date="01/01/25",
            bank_name="BRI"
        )
        result = metadata.to_dict()
        assert result["Statement Date"] == "01/01/25"
        assert result["Bank Name"] == "BRI"
    
    def test_transaction_creation(self):
        """Test Transaction object creation."""
        transaction = Transaction(
            transaction_date="01/01/25",
            transaction_time="10:30:00",
            description="Test transaction",
            teller_user_id="ATM001",
            debit=0.0,
            credit=100.0,
            balance=1000.0
        )
        assert transaction.credit == 100.0
        assert transaction.balance == 1000.0
    
    def test_parse_result_dataframes(self):
        """Test ParseResult DataFrame generation."""
        metadata = StatementMetadata(statement_date="01/01/25")
        transactions = [
            Transaction(
                transaction_date="01/01/25",
                transaction_time="10:30:00", 
                description="Test",
                teller_user_id="ATM001",
                debit=0.0,
                credit=100.0,
                balance=1000.0
            )
        ]
        result = ParseResult(metadata=metadata, transactions=transactions)
        
        metadata_df = result.get_metadata_df()
        transactions_df = result.get_transactions_df()
        
        assert len(metadata_df) == 1
        assert len(transactions_df) == 1
        assert transactions_df.iloc[0]["Credit"] == 100.0