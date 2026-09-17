from __future__ import annotations

import time
from dataclasses import dataclass

import httpx

from app.parser import ParsedChapter, SummaryParseError, parse_summary

FANDOM_API_URL = "https://tokyorevengers.fandom.com/api.php"
CHAPTER_SOURCE_URL = "https://tokyorevengers.fandom.com/wiki/Chapter_{chapter_number}"
MIN_CHAPTER = 1
MAX_CHAPTER = 278
CACHE_TTL_SECONDS = 60 * 60


class ChapterNotFoundError(LookupError):
    pass


class ChapterFetchError(RuntimeError):
    pass


@dataclass(slots=True)
class Chapter:
    number: int
    title: str
    paragraphs: list[str]
    source_url: str


_cache: dict[int, tuple[float, Chapter]] = {}


def _get_cached(chapter_number: int) -> Chapter | None:
    cached = _cache.get(chapter_number)
    if cached is None:
        return None

    cached_at, chapter = cached
    if time.monotonic() - cached_at > CACHE_TTL_SECONDS:
        _cache.pop(chapter_number, None)
        return None
    return chapter


async def fetch_chapter(chapter_number: int) -> Chapter:
    if not MIN_CHAPTER <= chapter_number <= MAX_CHAPTER:
        raise ChapterNotFoundError(
            f"Chapter must be between {MIN_CHAPTER} and {MAX_CHAPTER}."
        )

    cached = _get_cached(chapter_number)
    if cached is not None:
        return cached

    params = {
        "action": "parse",
        "page": f"Chapter_{chapter_number}",
        "prop": "text|displaytitle",
        "format": "json",
        "formatversion": "2",
        "redirects": "1",
    }
    headers = {
        "User-Agent": (
            "TokyoRevengersReader/1.0 "
            "(personal educational project; GitHub: FilipposGdms/TokyoRevengersScraper)"
        )
    }

    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            response = await client.get(FANDOM_API_URL, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise ChapterFetchError("Could not retrieve the chapter from Fandom.") from exc

    if "error" in payload:
        code = payload["error"].get("code", "")
        if code in {"missingtitle", "nosuchsection"}:
            raise ChapterNotFoundError(f"Chapter {chapter_number} was not found.")
        raise ChapterFetchError(payload["error"].get("info", "Fandom returned an error."))

    try:
        html = payload["parse"]["text"]
        parsed: ParsedChapter = parse_summary(html, chapter_number)
    except (KeyError, TypeError, SummaryParseError) as exc:
        raise ChapterFetchError(
            "The chapter was retrieved, but its Summary section could not be parsed."
        ) from exc

    chapter = Chapter(
        number=chapter_number,
        title=parsed.title,
        paragraphs=parsed.paragraphs,
        source_url=CHAPTER_SOURCE_URL.format(chapter_number=chapter_number),
    )
    _cache[chapter_number] = (time.monotonic(), chapter)
    return chapter
