#!/usr/bin/env python3
"""Simple test to check mypy compliance."""

from pdfparser import BRIParser, parse_pdf, get_supported_banks

def test_basic_functionality():
    """Test basic functionality without actual PDF."""
    # Test parser creation
    parser = BRIParser()
    assert parser.bank_name == "BRI"
    
    # Test supported banks
    banks = get_supported_banks()
    assert "BRI" in banks
    
    print("Basic functionality test passed!")

if __name__ == "__main__":
    test_basic_functionality()