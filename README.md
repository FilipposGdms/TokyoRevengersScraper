# Tokyo Revengers Reader

A small FastAPI application that retrieves the **Summary** section of Tokyo Revengers chapter pages from the Tokyo Revengers Wiki on Fandom and presents it in a simple book-like reader.

The application fetches chapters on demand instead of pre-scraping the entire wiki. The main manga contains chapters **1–278**.

## Features

- Book-like chapter reader at `/chapter/{number}`
- Previous/next chapter navigation
- Chapter number picker
- JSON API at `/api/chapters/{number}`
- One-hour in-memory cache for fetched chapters
- Parser that stops at the end of the Summary section
- FastAPI automatic docs at `/docs`
- Docker / Docker Compose support
- Optional Windows `run.bat` startup
- Render deployment configuration

## Run with Docker Compose

After cloning the repository:

```bash
docker compose up --build
```

Then open:

```text
http://127.0.0.1:8001
```

FastAPI docs:

```text
http://127.0.0.1:8001/docs
```

The container runs the application internally on port `8000`; Docker Compose maps it to port `8001` on your computer so it can run alongside the One Piece reader.

To stop the app, press `CTRL+C`. To stop and remove the container cleanly:

```bash
docker compose down
```

## Run locally without Docker

### Windows — one command

```bat
run.bat
```

The script automatically creates `.venv` if needed, installs/updates the dependencies, and starts the FastAPI application on port `8001`.

### Manual Python setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Open <http://127.0.0.1:8001>.

## API

```text
GET /api/chapters/1
GET /api/chapters/100
GET /api/chapters/278
```

Example response shape:

```json
{
  "chapter": 1,
  "title": "Reborn",
  "paragraphs": ["..."],
  "text": "...",
  "source": "https://tokyorevengers.fandom.com/wiki/Chapter_1"
}
```

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Deploy on Render

The repository includes `render.yaml`. In Render, create a new Blueprint/Web Service from this GitHub repository. Render will install the dependencies and start the app with Uvicorn.

The free Render tier may sleep when unused, so the first request after inactivity can take longer.

## How chapter extraction works

The app calls the Fandom/MediaWiki API for `Chapter_N`, receives the rendered article HTML, locates the `Summary` heading, collects paragraphs from that section, and stops at the next heading. This avoids the old behavior of collecting every paragraph appearing later on the page.

## Attribution

Summary text is retrieved from the [Tokyo Revengers Wiki on Fandom](https://tokyorevengers.fandom.com/). The reader links each chapter back to its source article. Wiki text remains subject to the applicable Fandom community licensing and attribution requirements.
