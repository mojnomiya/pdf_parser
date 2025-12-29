#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="indonesian-bank-statement-parser",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A high-performance Python module for extracting structured data from Indonesian bank statement PDFs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/indonesian-bank-statement-parser",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "bank-statement-parser=pdfparser.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pdfparser": ["py.typed"],
    },
)