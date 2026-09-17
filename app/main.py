from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.fandom import (
    MAX_CHAPTER,
    MIN_CHAPTER,
    ChapterFetchError,
    ChapterNotFoundError,
    fetch_chapter,
)

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Tokyo Revengers Reader",
    description="Read Tokyo Revengers Wiki chapter summaries in a simple book-like format.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", include_in_schema=False)
async def home() -> RedirectResponse:
    return RedirectResponse(url="/chapter/1", status_code=302)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/chapters/{chapter_number}")
async def chapter_api(chapter_number: int) -> dict[str, object]:
    try:
        chapter = await fetch_chapter(chapter_number)
    except ChapterNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ChapterFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "chapter": chapter.number,
        "title": chapter.title,
        "paragraphs": chapter.paragraphs,
        "text": "\n\n".join(chapter.paragraphs),
        "source": chapter.source_url,
    }


@app.get("/chapter/{chapter_number}", response_class=HTMLResponse)
async def chapter_reader(request: Request, chapter_number: int) -> HTMLResponse:
    try:
        chapter = await fetch_chapter(chapter_number)
    except ChapterNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ChapterFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return templates.TemplateResponse(
        request=request,
        name="reader.html",
        context={
            "chapter": chapter,
            "min_chapter": MIN_CHAPTER,
            "max_chapter": MAX_CHAPTER,
            "previous_chapter": chapter.number - 1 if chapter.number > MIN_CHAPTER else None,
            "next_chapter": chapter.number + 1 if chapter.number < MAX_CHAPTER else None,
        },
    )
