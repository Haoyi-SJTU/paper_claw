"""Writing assistant: generate paper outlines and draft sections using LLM."""

from dataclasses import dataclass, field
from literature_claw.llm.client import get_client
from literature_claw.summary.summarizer import PaperSummary


@dataclass
class PaperOutline:
    """Structure of a paper to be written."""

    title: str = ""
    sections: list[dict[str, str]] = field(default_factory=list)
    # Each section: {"heading": "...", "description": "...", "content": "..."}


OUTLINE_PROMPT = """You are an expert academic writing assistant. Based on the following information, generate a detailed paper outline.

**Paper Topic:** {topic}

**User Notes / Requirements:**
{notes}

**Available Reference Summaries:**
{reference_summaries}

Please generate an outline with the following sections. For each section, provide a heading and a brief description of what should be covered (2-3 sentences).

Use this format:
## [Section Heading]
[Description of content for this section]

Include standard academic sections: Title, Abstract, Introduction, Related Work/Background, Methodology, Results/Discussion, Conclusion, and any others that are relevant.
"""

SECTION_PROMPT = """You are an expert academic writing assistant. Write the following section of an academic paper.

**Paper Title:** {title}

**Section:** {heading}
**Section Description:** {description}

**Context from other sections:**
{context}

**Relevant reference summaries:**
{references}

**User notes for this section:**
{notes}

Write a complete, well-structured academic section (aim for 500-1000 words). Use formal academic language. Include citations where appropriate using [Author, Year] format. Do not include the section heading in your response.
"""


def generate_outline(
    topic: str,
    notes: str = "",
    reference_summaries: list[PaperSummary] | None = None,
    model: str | None = None,
) -> PaperOutline:
    """Generate a paper outline based on topic, notes, and reference summaries."""
    client = get_client(model)

    # Format reference summaries for the prompt
    ref_text = ""
    if reference_summaries:
        for i, s in enumerate(reference_summaries, 1):
            ref_text += f"\n### Reference {i}: {s.title}\n"
            ref_text += f"- Research Question: {s.research_question}\n"
            ref_text += f"- Key Findings: {', '.join(s.key_findings[:3])}\n"
            ref_text += f"- Conclusions: {s.conclusions}\n"

    prompt = OUTLINE_PROMPT.format(
        topic=topic,
        notes=notes or "None provided.",
        reference_summaries=ref_text or "No references provided.",
    )

    response = client.chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2048,
    )

    # Parse outline from response
    import re
    sections = []
    matches = re.findall(r"##\s*(.+?)\n(.*?)(?=\n##|\Z)", response, re.DOTALL)
    for heading, description in matches:
        sections.append({
            "heading": heading.strip(),
            "description": description.strip(),
            "content": "",
        })

    return PaperOutline(title=topic, sections=sections)


def draft_section(
    outline: PaperOutline,
    section_index: int,
    reference_summaries: list[PaperSummary] | None = None,
    notes: str = "",
    model: str | None = None,
) -> str:
    """Generate a draft for a specific section of the paper."""
    client = get_client(model)
    section = outline.sections[section_index]

    # Build context from other sections
    context_parts = []
    for i, s in enumerate(outline.sections):
        if i != section_index and s.get("content"):
            context_parts.append(f"- {s['heading']}: {s['content'][:200]}...")
    context = "\n".join(context_parts) if context_parts else "No other sections written yet."

    # Relevant references
    ref_text = ""
    if reference_summaries:
        for i, s in enumerate(reference_summaries, 1):
            ref_text += f"\n- {s.title}: {s.conclusions[:200]}\n"

    prompt = SECTION_PROMPT.format(
        title=outline.title,
        heading=section["heading"],
        description=section["description"],
        context=context,
        references=ref_text or "No references provided.",
        notes=notes or "None.",
    )

    content = client.chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=4096,
    )

    outline.sections[section_index]["content"] = content
    return content


def draft_full_paper(
    outline: PaperOutline,
    reference_summaries: list[PaperSummary] | None = None,
    notes_per_section: dict[int, str] | None = None,
    model: str | None = None,
) -> PaperOutline:
    """Draft all sections of the paper sequentially."""
    notes_per_section = notes_per_section or {}

    for i in range(len(outline.sections)):
        section_notes = notes_per_section.get(i, "")
        draft_section(
            outline=outline,
            section_index=i,
            reference_summaries=reference_summaries,
            notes=section_notes,
            model=model,
        )

    return outline
