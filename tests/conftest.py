"""Test configuration and fixtures."""

import pytest
from pathlib import Path

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"

@pytest.fixture
def sample_bri_pdf():
    """Path to sample BRI PDF for testing."""
    return TEST_DATA_DIR / "sample_bri_statement.pdf"

@pytest.fixture
def expected_metadata():
    """Expected metadata for sample BRI PDF."""
    return {
        "Statement Date": "03/06/25",
        "Transaction Period Start": "01/05/25", 
        "Transaction Period End": "31/05/25",
        "Product Name": "Britama-IDR",
        "Currency": "IDR",
        "Bank Name": "BRI"
    }