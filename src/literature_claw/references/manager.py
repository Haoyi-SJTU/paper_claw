"""Reference manager: parse BibTeX and format citations."""

from dataclasses import dataclass, field
from pathlib import Path

from pybtex.database import BibliographyData, Entry
from pybtex.database.input import bibtex
from pybtex.style.formatting.plain import Style as PlainStyle


@dataclass
class Reference:
    """A single bibliographic reference."""

    key: str = ""
    type: str = ""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: str = ""
    journal: str = ""
    doi: str = ""
    formatted: str = ""


class ReferenceManager:
    """Manage BibTeX references and format citations."""

    def __init__(self):
        self.references: dict[str, Reference] = {}
        self._bib_data: BibliographyData | None = None

    def load_bibtex(self, file_path: str | Path) -> int:
        """Load references from a .bib file. Returns count of entries loaded."""
        parser = bibtex.Parser()
        self._bib_data = parser.parse_file(str(file_path))

        formatter = PlainStyle()
        count = 0

        for key, entry in self._bib_data.entries.items():
            ref = self._entry_to_reference(key, entry, formatter)
            self.references[key] = ref
            count += 1

        return count

    def _entry_to_reference(
        self, key: str, entry: Entry, formatter: PlainStyle
    ) -> Reference:
        """Convert a pybtex Entry to a Reference."""
        authors = []
        for person in entry.persons.get("author", []):
            name = " ".join(filter(None, [
                " ".join(person.first_names),
                " ".join(person.last_names),
            ]))
            if name:
                authors.append(name)

        fields = entry.fields
        formatted = ""
        try:
            formatted_entries = formatter.format_entries([entry])
            formatted = next(iter(formatted_entries)).text.render_as("text")
        except Exception:
            formatted = f"{', '.join(authors)}. {fields.get('title', '')}. {fields.get('journal', '')}, {fields.get('year', '')}."

        return Reference(
            key=key,
            type=entry.type,
            title=fields.get("title", ""),
            authors=authors,
            year=fields.get("year", ""),
            journal=fields.get("journal", ""),
            doi=fields.get("doi", ""),
            formatted=formatted,
        )

    def get_reference(self, key: str) -> Reference | None:
        """Get a reference by its citation key."""
        return self.references.get(key)

    def format_citation(self, key: str, style: str = "apa") -> str:
        """Format an in-text citation for the given key."""
        ref = self.references.get(key)
        if not ref:
            return f"[{key}]"

        if style == "apa":
            if len(ref.authors) == 1:
                author = ref.authors[0].split()[-1]
            elif len(ref.authors) == 2:
                author = f"{ref.authors[0].split()[-1]} & {ref.authors[1].split()[-1]}"
            else:
                author = f"{ref.authors[0].split()[-1]} et al."
            return f"({author}, {ref.year})"

        elif style == "ieee":
            idx = list(self.references.keys()).index(key) + 1 if key in self.references else 0
            return f"[{idx}]"

        return f"[{key}]"

    def format_reference_list(self, style: str = "apa") -> list[str]:
        """Generate a formatted reference list."""
        if style == "apa":
            return [ref.formatted for ref in self.references.values()]
        elif style == "ieee":
            return [
                f"[{i+1}] {ref.formatted}"
                for i, ref in enumerate(self.references.values())
            ]
        return [ref.formatted for ref in self.references.values()]

    def add_reference(self, ref: Reference) -> None:
        """Manually add a reference."""
        self.references[ref.key] = ref

    def search(self, query: str) -> list[Reference]:
        """Search references by title or author."""
        query_lower = query.lower()
        results = []
        for ref in self.references.values():
            if (
                query_lower in ref.title.lower()
                or any(query_lower in a.lower() for a in ref.authors)
                or query_lower in ref.key.lower()
            ):
                results.append(ref)
        return results
