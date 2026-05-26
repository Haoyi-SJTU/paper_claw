"""Tests for document exporter."""

import pytest
import tempfile
from pathlib import Path

from literature_claw.export.exporter import Exporter
from literature_claw.writing.assistant import PaperOutline


@pytest.fixture
def sample_outline():
    """Create a sample paper outline for testing."""
    return PaperOutline(
        title="Test Paper on AI",
        sections=[
            {
                "heading": "Abstract",
                "description": "Brief summary of the paper",
                "content": "This paper explores the applications of AI in healthcare.",
            },
            {
                "heading": "Introduction",
                "description": "Introduction to the topic",
                "content": "Artificial intelligence has transformed many fields.\n\nHealthcare is one of the most promising areas.",
            },
            {
                "heading": "Conclusion",
                "description": "Final thoughts",
                "content": "AI shows great promise in healthcare applications.",
            },
        ],
    )


class TestExporter:
    """Test document export functionality."""

    def test_export_markdown(self, sample_outline):
        """Test Markdown export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = Exporter(tmpdir)
            path = exporter.export_markdown(sample_outline)
            assert path.exists()
            content = path.read_text(encoding="utf-8")
            assert "# Test Paper on AI" in content
            assert "## Abstract" in content
            assert "AI in healthcare" in content

    def test_export_word(self, sample_outline):
        """Test Word export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = Exporter(tmpdir)
            path = exporter.export_word(sample_outline)
            assert path.exists()
            assert path.suffix == ".docx"
            assert path.stat().st_size > 0

    def test_export_both(self, sample_outline):
        """Test exporting both formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = Exporter(tmpdir)
            paths = exporter.export_both(sample_outline, base_name="test")
            assert paths["markdown"].exists()
            assert paths["word"].exists()
            assert paths["markdown"].suffix == ".md"
            assert paths["word"].suffix == ".docx"

    def test_export_empty_outline(self):
        """Test exporting an empty outline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = Exporter(tmpdir)
            outline = PaperOutline(title="Empty", sections=[])
            path = exporter.export_markdown(outline)
            assert path.exists()
