"""Tests for paper summarizer."""

import pytest
from literature_claw.summary.summarizer import parse_summary, PaperSummary


SAMPLE_RESPONSE = """## Research Question
How does deep learning improve medical image analysis?

## Methodology
We conducted a systematic review of 50 recent studies using CNNs for medical imaging.

## Key Findings
- CNNs outperform traditional methods by 15% on average
- Transfer learning significantly reduces data requirements
- Attention mechanisms improve interpretability

## Conclusions
Deep learning shows strong potential for medical image analysis tasks.

## Limitations
Most studies used small datasets and lacked clinical validation.

## Key Terms
- Convolutional Neural Networks
- Medical Imaging
- Transfer Learning
- Attention Mechanisms

## Relevance
Medical researchers and AI practitioners working on healthcare applications.
"""


class TestSummarizer:
    """Test summary parsing logic."""

    def test_parse_summary_basic(self):
        """Test basic summary parsing."""
        summary = parse_summary(SAMPLE_RESPONSE, title="Test Paper")
        assert summary.title == "Test Paper"
        assert "deep learning" in summary.research_question.lower()

    def test_parse_summary_findings(self):
        """Test key findings extraction."""
        summary = parse_summary(SAMPLE_RESPONSE)
        assert len(summary.key_findings) == 3
        assert "CNNs" in summary.key_findings[0]

    def test_parse_summary_key_terms(self):
        """Test key terms extraction."""
        summary = parse_summary(SAMPLE_RESPONSE)
        assert len(summary.key_terms) == 4
        assert "Transfer Learning" in summary.key_terms

    def test_parse_summary_all_sections(self):
        """Test all sections are populated."""
        summary = parse_summary(SAMPLE_RESPONSE)
        assert summary.methodology != ""
        assert summary.conclusions != ""
        assert summary.limitations != ""
        assert summary.relevance != ""

    def test_parse_empty_response(self):
        """Test graceful handling of empty response."""
        summary = parse_summary("")
        assert summary.research_question == ""
        assert summary.key_findings == []
