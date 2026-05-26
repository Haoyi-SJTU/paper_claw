"""PDF reader: extract text, metadata, and structure from academic papers."""

from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF


@dataclass
class PaperData:
    """Structured representation of a parsed academic paper."""

    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    sections: list[dict[str, str]] = field(default_factory=list)
    full_text: str = ""
    references: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    file_path: str = ""


class PDFReader:
    """Parse PDF academic papers into structured data."""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.doc = fitz.open(str(self.file_path))

    def extract_text(self) -> str:
        """Extract full text from all pages."""
        pages = []
        for page in self.doc:
            pages.append(page.get_text())
        return "\n".join(pages)

    def extract_metadata(self) -> dict:
        """Extract PDF metadata (title, author, etc.)."""
        meta = self.doc.metadata or {}
        return {
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": meta.get("subject", ""),
            "keywords": meta.get("keywords", ""),
            "page_count": len(self.doc),
        }

    def extract_sections(self, text: str) -> list[dict[str, str]]:
        """Identify paper sections from text using common heading patterns."""
        import re

        # Common academic paper section headings
        section_pattern = re.compile(
            r"^(?:\d+\.?\s*)?("
            r"Abstract|Introduction|Background|Related Work|"
            r"Methodology|Methods|Materials and Methods|"
            r"Results|Findings|Experiments|"
            r"Discussion|Analysis|"
            r"Conclusion|Conclusions|Future Work|"
            r"Acknowledgments|References|Bibliography"
            r")\s*$",
            re.MULTILINE | re.IGNORECASE,
        )

        sections = []
        matches = list(section_pattern.finditer(text))

        if not matches:
            return [{"heading": "Full Text", "content": text}]

        # Text before first heading
        if matches[0].start() > 0:
            preamble = text[: matches[0].start()].strip()
            if preamble:
                sections.append({"heading": "Preamble", "content": preamble})

        for i, match in enumerate(matches):
            heading = match.group(0).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()
            sections.append({"heading": heading, "content": content})

        return sections

    def extract_references(self, text: str) -> list[str]:
        """Extract reference list from the paper."""
        import re

        # Find the References/Bibliography section
        ref_pattern = re.compile(
            r"(?:References|Bibliography)\s*\n(.*?)(?:\Z|Appendix)",
            re.DOTALL | re.IGNORECASE,
        )
        match = ref_pattern.search(text)
        if not match:
            return []

        ref_text = match.group(1).strip()
        # Split by numbered references like [1], (1), or 1.
        refs = re.split(r"(?:\[\d+\]|\(\d+\)|\d+\.)\s*", ref_text)
        return [r.strip() for r in refs if r.strip()]

    def parse(self) -> PaperData:
        """Parse the PDF into a structured PaperData object."""
        text = self.extract_text()
        meta = self.extract_metadata()
        sections = self.extract_sections(text)

        # Try to extract abstract from sections
        abstract = ""
        for sec in sections:
            if sec["heading"].lower() == "abstract":
                abstract = sec["content"]
                break

        return PaperData(
            title=meta.get("title", ""),
            authors=[a.strip() for a in meta.get("author", "").split(",") if a.strip()],
            abstract=abstract,
            sections=sections,
            full_text=text,
            references=self.extract_references(text),
            metadata=meta,
            file_path=str(self.file_path),
        )

    def close(self):
        """Close the PDF document."""
        self.doc.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
