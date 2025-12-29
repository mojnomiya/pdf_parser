"""
Indonesian Bank Statement PDF Parser

A high-performance Python module for extracting structured data 
from Indonesian bank statement PDFs supporting multiple bank formats.
"""

from .base import StatementMetadata, Transaction, ParseResult, BaseBankParser
from .parser import BRIParser
from .factory import parse_pdf, get_supported_banks, PDFParser, ParserFactory

__version__ = "1.0.0"
__all__ = [
    "PDFParser", 
    "BRIParser",
    "ParserFactory",
    "parse_pdf", 
    "get_supported_banks",
    "StatementMetadata", 
    "Transaction", 
    "ParseResult",
    "BaseBankParser"
]
