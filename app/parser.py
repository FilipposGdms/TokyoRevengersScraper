from __future__ import annotations

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag


class SummaryParseError(ValueError):
    """Raised when the chapter summary cannot be extracted from the wiki HTML."""


@dataclass(slots=True)
class ParsedChapter:
    title: str
    paragraphs: list[str]


def _heading_text(tag: Tag) -> str:
    return " ".join(tag.stripped_strings).strip()


def _clean_text(tag: Tag) -> str:
    text = " ".join(tag.stripped_strings)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_chapter_title(soup: BeautifulSoup, chapter_number: int) -> str:
    """Best-effort extraction of the chapter subtitle that appears before Summary."""
    ignored = {
        "information",
        "guide",
        "summary",
        "characters in order of appearance",
        "references",
        "navigation",
    }

    for heading in soup.find_all(["h2", "h3"]):
        text = _heading_text(heading)
        normalized = text.strip('[]\"“”').strip().lower()
        if normalized == "summary":
            break
        if not normalized or normalized in ignored:
            continue
        if normalized.startswith("chapter "):
            continue
        if len(text) <= 120:
            return text.strip('[]\"“”').strip()

    return f"Chapter {chapter_number}"


def parse_summary(html: str, chapter_number: int) -> ParsedChapter:
    """Extract only the Summary section and stop at the next heading."""
    soup = BeautifulSoup(html, "html.parser")
    summary_marker = soup.find(id="Summary")
    if summary_marker is None:
        summary_marker = soup.find(
            lambda tag: isinstance(tag, Tag)
            and tag.name in {"h2", "h3", "h4"}
            and _heading_text(tag).strip('[]').strip().lower() == "summary"
        )

    if summary_marker is None:
        raise SummaryParseError("Summary section was not found on the wiki page.")

    summary_heading = (
        summary_marker
        if summary_marker.name in {"h2", "h3", "h4", "h5", "h6"}
        else summary_marker.find_parent(["h2", "h3", "h4", "h5", "h6"])
    )
    if summary_heading is None:
        raise SummaryParseError("Summary heading could not be resolved.")

    paragraphs: list[str] = []
    for sibling in summary_heading.next_siblings:
        if isinstance(sibling, Tag) and sibling.name in {"h2", "h3", "h4", "h5", "h6"}:
            break
        if not isinstance(sibling, Tag):
            continue

        candidates = [sibling] if sibling.name == "p" else sibling.find_all("p")
        for paragraph in candidates:
            text = _clean_text(paragraph)
            if text:
                paragraphs.append(text)

    if not paragraphs:
        raise SummaryParseError("Summary section was found, but it contained no readable text.")

    return ParsedChapter(
        title=extract_chapter_title(soup, chapter_number),
        paragraphs=paragraphs,
    )
