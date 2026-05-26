"""Tests for PDF reader."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from literature_claw.pdf.reader import PDFReader, PaperData


class TestPDFReader:
    """Test PDF parsing functionality."""

    def test_extract_sections_with_headings(self):
        """Test section extraction from structured text."""
        reader = PDFReader.__new__(PDFReader)
        text = """Abstract
This is the abstract content.

Introduction
This is the introduction.

Methodology
This section describes the methods.

Results
Here are the results.

Conclusion
Final conclusions.
"""
        sections = reader.extract_sections(text)
        headings = [s["heading"] for s in sections]
        assert "Abstract" in headings
        assert "Introduction" in headings
        assert "Methodology" in headings

    def test_extract_sections_no_headings(self):
        """Test fallback when no section headings are found."""
        reader = PDFReader.__new__(PDFReader)
        text = "This is plain text without any section headings."
        sections = reader.extract_sections(text)
        assert len(sections) == 1
        assert sections[0]["heading"] == "Full Text"

    def test_extract_references(self):
        """Test reference extraction from paper text."""
        reader = PDFReader.__new__(PDFReader)
        text = """
Introduction
Some content here.

References
[1] Smith, J. (2020). A great paper. Journal of AI.
[2] Doe, A. (2021). Another paper. Nature.
[3] Brown, B. (2022). Yet another. Science.
"""
        refs = reader.extract_references(text)
        assert len(refs) == 3
        assert "Smith" in refs[0]

    def test_paper_data_creation(self):
        """Test PaperData dataclass creation."""
        paper = PaperData(
            title="Test Paper",
            authors=["Author One", "Author Two"],
            abstract="Test abstract",
        )
        assert paper.title == "Test Paper"
        assert len(paper.authors) == 2
        assert paper.sections == []
