"""literature_claw - Streamlit UI for academic paper reading, summarization, and writing."""

import streamlit as st
import json
from pathlib import Path

from literature_claw.config import (
    PAPERS_DIR, SUMMARIES_DIR, OUTPUT_DIR,
    AVAILABLE_MODELS, DEFAULT_MODEL,
)
from literature_claw.pdf.reader import PDFReader
from literature_claw.summary.summarizer import summarize_paper, PaperSummary
from literature_claw.writing.assistant import (
    generate_outline, draft_section, draft_full_paper, PaperOutline,
)
from literature_claw.references.manager import ReferenceManager
from literature_claw.export.exporter import Exporter
from literature_claw.llm.client import get_client

# Page config
st.set_page_config(
    page_title="Literature Claw",
    page_icon="📚",
    layout="wide",
)


def page_library():
    """Paper library: upload, parse, and view summaries."""
    st.header("📚 Paper Library")

    # Upload section
    st.subheader("Upload PDF")
    uploaded = st.file_uploader(
        "Upload a PDF paper",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded:
        for f in uploaded:
            save_path = PAPERS_DIR / f.name
            save_path.write_bytes(f.read())
            st.success(f"Saved: {f.name}")

    # List existing papers
    st.subheader("Papers")
    pdf_files = sorted(PAPERS_DIR.glob("*.pdf"))

    if not pdf_files:
        st.info("No papers uploaded yet. Upload a PDF above to get started.")
        return

    for pdf_path in pdf_files:
        with st.expander(f"📄 {pdf_path.name}"):
            col1, col2 = st.columns([1, 3])

            with col1:
                if st.button("Parse & Summarize", key=f"parse_{pdf_path.name}"):
                    with st.spinner("Parsing PDF..."):
                        with PDFReader(pdf_path) as reader:
                            paper = reader.parse()

                    with st.spinner("Generating summary (this may take a moment)..."):
                        summary = summarize_paper(paper)

                    # Save summary
                    summary_path = SUMMARIES_DIR / f"{pdf_path.stem}.json"
                    summary_path.write_text(
                        json.dumps({
                            "title": summary.title,
                            "research_question": summary.research_question,
                            "methodology": summary.methodology,
                            "key_findings": summary.key_findings,
                            "conclusions": summary.conclusions,
                            "limitations": summary.limitations,
                            "key_terms": summary.key_terms,
                            "relevance": summary.relevance,
                        }, indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    st.rerun()

            with col2:
                # Show summary if exists
                summary_path = SUMMARIES_DIR / f"{pdf_path.stem}.json"
                if summary_path.exists():
                    data = json.loads(summary_path.read_text(encoding="utf-8"))
                    st.markdown(f"**Research Question:** {data.get('research_question', 'N/A')}")
                    st.markdown(f"**Methodology:** {data.get('methodology', 'N/A')}")
                    findings = data.get("key_findings", [])
                    if findings:
                        st.markdown("**Key Findings:**")
                        for f in findings:
                            st.markdown(f"- {f}")
                    st.markdown(f"**Conclusions:** {data.get('conclusions', 'N/A')}")
                    terms = data.get("key_terms", [])
                    if terms:
                        st.markdown(f"**Key Terms:** {', '.join(terms)}")


def page_writing():
    """Writing assistant: generate outlines and draft papers."""
    st.header("✍️ Writing Assistant")

    # Topic input
    col1, col2 = st.columns([2, 1])
    with col1:
        topic = st.text_input("Paper Topic", placeholder="e.g., Deep Learning for Medical Image Analysis")
    with col2:
        ref_manager = ReferenceManager()
        bib_files = list(Path(".").glob("*.bib")) + list(Path("./data").glob("*.bib"))
        if bib_files:
            bib_path = st.selectbox("BibTeX file", [str(f) for f in bib_files])
            ref_manager.load_bibtex(bib_path)
            st.info(f"Loaded {len(ref_manager.references)} references")

    notes = st.text_area(
        "Notes / Requirements",
        placeholder="Describe what you want in this paper, specific requirements, data to include, etc.",
        height=150,
    )

    # Load available summaries for reference context
    available_summaries = []
    summary_files = sorted(SUMMARIES_DIR.glob("*.json"))
    if summary_files:
        st.subheader("Reference Papers")
        selected_refs = st.multiselect(
            "Select papers to use as references",
            options=[f.stem for f in summary_files],
        )
        for name in selected_refs:
            path = SUMMARIES_DIR / f"{name}.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            available_summaries.append(PaperSummary(**data))

    # Generate outline
    if st.button("Generate Outline", type="primary") and topic:
        with st.spinner("Generating outline..."):
            outline = generate_outline(
                topic=topic,
                notes=notes,
                reference_summaries=available_summaries or None,
            )
            st.session_state["outline"] = outline
            st.success("Outline generated!")

    # Display and edit outline
    if "outline" in st.session_state:
        outline = st.session_state["outline"]
        st.subheader("Paper Outline")

        for i, section in enumerate(outline.sections):
            with st.expander(f"📝 {section['heading']}", expanded=False):
                st.markdown(f"**Description:** {section['description']}")
                section_notes = st.text_input(
                    "Notes for this section",
                    key=f"notes_{i}",
                )
                if st.button(f"Draft Section", key=f"draft_{i}"):
                    with st.spinner(f"Drafting {section['heading']}..."):
                        content = draft_section(
                            outline=outline,
                            section_index=i,
                            reference_summaries=available_summaries or None,
                            notes=section_notes,
                        )
                        st.session_state["outline"] = outline
                        st.rerun()

                if section.get("content"):
                    st.markdown("---")
                    st.markdown(section["content"])

        # Export
        st.subheader("Export")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Draft All Sections"):
                with st.spinner("Drafting full paper..."):
                    draft_full_paper(
                        outline,
                        reference_summaries=available_summaries or None,
                    )
                    st.session_state["outline"] = outline
                    st.success("Full paper drafted!")
                    st.rerun()

        with col2:
            if st.button("Export to Word & Markdown"):
                exporter = Exporter()
                paths = exporter.export_both(outline, base_name=topic[:30].replace(" ", "_"))
                st.success(f"Exported!")
                st.write(f"📄 Word: `{paths['word']}`")
                st.write(f"📝 Markdown: `{paths['markdown']}`")


def page_settings():
    """Settings: configure LLM model and API keys."""
    st.header("⚙️ Settings")

    st.subheader("LLM Model")
    model_names = list(AVAILABLE_MODELS.keys())
    current = st.session_state.get("model", DEFAULT_MODEL)
    idx = model_names.index(current) if current in model_names else 0
    selected = st.selectbox("Select Model", model_names, index=idx)
    if selected != current:
        st.session_state["model"] = selected
        get_client(selected)
        st.success(f"Switched to {selected}")

    st.subheader("API Keys")
    st.info("Configure API keys in the `.env` file in the project root.")
    st.code("# .env\nOPENAI_API_KEY=sk-...\nANTHROPIC_API_KEY=sk-ant-...", language="bash")

    st.subheader("Data Directories")
    st.write(f"📄 Papers: `{PAPERS_DIR}`")
    st.write(f"📋 Summaries: `{SUMMARIES_DIR}`")
    st.write(f"📤 Output: `{OUTPUT_DIR}`")


# Navigation
page = st.sidebar.radio("Navigation", ["📚 Paper Library", "✍️ Writing Assistant", "⚙️ Settings"])

if page == "📚 Paper Library":
    page_library()
elif page == "✍️ Writing Assistant":
    page_writing()
elif page == "⚙️ Settings":
    page_settings()
