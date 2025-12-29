"""
Base classes and interfaces for bank statement parsers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

import pandas as pd


@dataclass
class StatementMetadata:
    """Parsed metadata from the bank statement header."""
    statement_date: Optional[str] = None
    transaction_period_start: Optional[str] = None
    transaction_period_end: Optional[str] = None
    account_number: Optional[str] = None
    product_name: Optional[str] = None
    currency: Optional[str] = None
    business_unit: Optional[str] = None
    business_unit_address: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_address: Optional[str] = None
    bank_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "Statement Date": self.statement_date,
            "Transaction Period Start": self.transaction_period_start,
            "Transaction Period End": self.transaction_period_end,
            "Account Number": self.account_number,
            "Product Name": self.product_name,
            "Currency": self.currency,
            "Business Unit": self.business_unit,
            "Business Unit Address": self.business_unit_address,
            "Recipient Name": self.recipient_name,
            "Recipient Address": self.recipient_address,
            "Bank Name": self.bank_name,
        }


@dataclass
class Transaction:
    """A single transaction from the statement."""
    transaction_date: str
    transaction_time: Optional[str]
    description: str
    teller_user_id: str
    debit: float
    credit: float
    balance: float


@dataclass
class ParseResult:
    """Result of parsing a bank statement PDF."""
    metadata: StatementMetadata
    transactions: List[Transaction]
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def get_metadata_df(self) -> pd.DataFrame:
        """Get metadata as a pandas DataFrame (single row)."""
        return pd.DataFrame([self.metadata.to_dict()])
    
    def get_transactions_df(self) -> pd.DataFrame:
        """Get transactions as a pandas DataFrame."""
        data = []
        for t in self.transactions:
            data.append({
                "Transaction Date": t.transaction_date,
                "Transaction Time": t.transaction_time,
                "Description": t.description,
                "Teller/User ID": t.teller_user_id,
                "Debit": t.debit,
                "Credit": t.credit,
                "Balance": t.balance,
            })
        return pd.DataFrame(data)
    
    def export_to_csv(self, metadata_path: str, transactions_path: str) -> None:
        """Export parsed data to CSV files."""
        self.get_metadata_df().to_csv(metadata_path, index=False)
        self.get_transactions_df().to_csv(transactions_path, index=False)


class BaseBankParser(ABC):
    """Abstract base class for bank statement parsers."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the parser with optional configuration."""
        self.config = config or {}
    
    @abstractmethod
    def parse(self, pdf_path: Union[str, Path]) -> ParseResult:
        """Parse a bank statement PDF and return structured data."""
        pass
    
    @abstractmethod
    def can_parse(self, pdf_path: Union[str, Path]) -> bool:
        """Check if this parser can handle the given PDF."""
        pass
    
    @property
    @abstractmethod
    def bank_name(self) -> str:
        """Return the name of the bank this parser handles."""
        pass
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float (handles Indonesian format)."""
        if not amount_str or amount_str.strip() == "":
            return 0.0
        
        # Remove thousand separators (commas) and keep decimal point
        cleaned = amount_str.replace(",", "").strip()
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0