"""
Parser factory for automatically detecting and parsing different bank statement formats.
"""

from pathlib import Path
from typing import List, Type, Union, Optional, Dict, Any

from .base import BaseBankParser, ParseResult
from .parser import BRIParser


class ParserFactory:
    """Factory class for creating appropriate bank statement parsers."""
    
    def __init__(self) -> None:
        """Initialize the factory with available parsers."""
        self._parsers: List[Type[BaseBankParser]] = [
            BRIParser,
            # Add more parsers here as they are implemented
        ]
    
    def get_parser(self, pdf_path: Union[str, Path], config: Optional[Dict[str, Any]] = None) -> BaseBankParser:
        """
        Get the appropriate parser for the given PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            config: Optional configuration dictionary
            
        Returns:
            An instance of the appropriate parser
            
        Raises:
            ValueError: If no suitable parser is found
        """
        pdf_path = Path(pdf_path)
        
        for parser_class in self._parsers:
            parser = parser_class(config)
            if parser.can_parse(pdf_path):
                return parser
        
        raise ValueError(f"No suitable parser found for PDF: {pdf_path}")
    
    def parse(self, pdf_path: Union[str, Path], config: Optional[Dict[str, Any]] = None) -> ParseResult:
        """
        Parse a bank statement PDF using the appropriate parser.
        
        Args:
            pdf_path: Path to the PDF file
            config: Optional configuration dictionary
            
        Returns:
            ParseResult containing metadata and transactions
        """
        parser = self.get_parser(pdf_path, config)
        return parser.parse(pdf_path)
    
    def list_supported_banks(self) -> List[str]:
        """
        Get a list of supported bank names.
        
        Returns:
            List of bank names that can be parsed
        """
        banks = []
        for parser_class in self._parsers:
            # Create a temporary instance to get the bank name
            temp_parser = parser_class()
            banks.append(temp_parser.bank_name)
        return banks


# Global factory instance
_factory = ParserFactory()


def parse_pdf(pdf_path: Union[str, Path], config: Optional[Dict[str, Any]] = None) -> ParseResult:
    """
    Convenience function to parse a bank statement PDF using auto-detection.
    
    Args:
        pdf_path: Path to the PDF file.
        config: Optional configuration dictionary.
        
    Returns:
        ParseResult containing metadata and transactions.
        
    Example:
        result = parse_pdf("statement.pdf")
        result.export_to_csv("metadata.csv", "transactions.csv")
    """
    return _factory.parse(pdf_path, config)


def get_supported_banks() -> List[str]:
    """
    Get a list of supported bank names.
    
    Returns:
        List of bank names that can be parsed
    """
    return _factory.list_supported_banks()


# Legacy compatibility
PDFParser = BRIParser