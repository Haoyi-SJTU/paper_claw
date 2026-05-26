"""Paper summarizer: generate structured summaries using LLM."""

from dataclasses import dataclass, field
from literature_claw.llm.client import get_client
from literature_claw.pdf.reader import PaperData


@dataclass
class PaperSummary:
    """Structured summary of an academic paper."""

    title: str = ""
    research_question: str = ""
    methodology: str = ""
    key_findings: list[str] = field(default_factory=list)
    conclusions: str = ""
    limitations: str = ""
    key_terms: list[str] = field(default_factory=list)
    relevance: str = ""


SUMMARIZE_PROMPT = """You are an expert academic researcher. Analyze the following paper and provide a structured summary.

Paper text:
{text}

Please respond in the following format (use these exact headings):

## Research Question
What is the main research question or objective?

## Methodology
What methods/approaches were used?

## Key Findings
List the main findings as bullet points (one per line, starting with -).

## Conclusions
What are the main conclusions?

## Limitations
What limitations did the authors acknowledge or that you identified?

## Key Terms
List important technical terms or concepts (one per line, starting with -).

## Relevance
Who would benefit from reading this paper and why?
"""


def parse_summary(response: str, title: str = "") -> PaperSummary:
    """Parse LLM response into a PaperSummary object."""
    import re

    def extract_section(heading: str) -> str:
        pattern = rf"##\s*{heading}\s*\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    findings_text = extract_section("Key Findings")
    findings = [
        line.lstrip("- ").strip()
        for line in findings_text.split("\n")
        if line.strip().startswith("-")
    ]

    terms_text = extract_section("Key Terms")
    terms = [
        line.lstrip("- ").strip()
        for line in terms_text.split("\n")
        if line.strip().startswith("-")
    ]

    return PaperSummary(
        title=title,
        research_question=extract_section("Research Question"),
        methodology=extract_section("Methodology"),
        key_findings=findings,
        conclusions=extract_section("Conclusions"),
        limitations=extract_section("Limitations"),
        key_terms=terms,
        relevance=extract_section("Relevance"),
    )


def summarize_paper(paper: PaperData, model: str | None = None) -> PaperSummary:
    """Generate a structured summary for a parsed paper."""
    client = get_client(model)

    # Truncate very long papers to fit context window
    text = paper.full_text
    if len(text) > 30000:
        text = text[:30000] + "\n\n[... text truncated for summarization ...]"

    prompt = SUMMARIZE_PROMPT.format(text=text)
    response = client.chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048,
    )

    return parse_summary(response, title=paper.title)


def summarize_multiple(papers: list[PaperData], model: str | None = None) -> list[PaperSummary]:
    """Summarize multiple papers."""
    return [summarize_paper(p, model) for p in papers]
