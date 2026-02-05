"""
Setup configuration for Technical Debt Analyzer.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="technical-debt-analyzer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Rule-based technical debt analysis from code reviews",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/technical-debt-analyzer",
    py_modules=[
        "cli_rules",
        "rule_based_extractor",
        "models",
        "parser",
        "scoring",
        "report"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "td-analyze=cli_rules:main",
        ],
    },
)
