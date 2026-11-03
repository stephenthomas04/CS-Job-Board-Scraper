# CS / Quant Job Dashboard

A local dashboard for browsing software, data, and quantitative job listings. The frontend uses React, TypeScript, Vite, and Tailwind CSS. A Python scraper collects listings from public Greenhouse and Lever job boards.

## Features

- Search listings by job title or company name.
- View locations, work arrangement, and season or posting date.
- Open job postings and company websites.
- Save bookmarks in your browser's local storage.
- Display up to 100 matching listings at a time to keep rendering responsive. Search narrows the full set of visible listings.

## Run the dashboard

Install Node.js with npm, then run these commands from the repository root:

```sh
cd ui
npm ci
npm run dev
```

Open the local URL printed by Vite, usually http://localhost:5173. Press `Ctrl+C` in the terminal to stop the server.

The repository includes a saved dataset at `ui/public/listings.json`, so running the dashboard does not require Python or a fresh scrape. The frontend fetches this file when the page loads; it does not refresh job boards automatically.

## Refresh job listings

Use Python 3.10 or later. From the repository root, create a virtual environment:

```sh
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```sh
source .venv/bin/activate
```

Install the scraper dependency and run it:

```sh
python -m pip install -r scraper/requirements.txt
python scraper/scrape.py
```

The scraper fetches configured boards, filters titles by keyword, validates listings, removes duplicates by source and ID, and sorts newest postings first. It replaces both `listings.json` in the repository root and `ui/public/listings.json` with the results of that run. Reload the dashboard afterward to load the updated data.

Edit `scraper/config.py` to change companies, board tokens, title keywords, request settings, or sponsorship phrases. Public board requests require internet access but no API keys. Unavailable boards are skipped, so review the scraper's summary before relying on the resulting dataset.

Season and sponsorship values are inferred from posting text and may be incomplete or inaccurate. Check the original posting for details.

## Build and preview

From the `ui` directory:

```sh
npm run build
npm run preview
```

The build command runs TypeScript checks and generates the static site in `ui/dist`. The preview command serves that build locally at the URL printed in the terminal. Refresh listings before building if you want the build to include new data.

## Project layout

| Path | Purpose |
| --- | --- |
| `ui/src/` | Dashboard components and TypeScript types |
| `ui/public/listings.json` | Dataset served to the dashboard |
| `scraper/scrape.py` | Greenhouse and Lever scraper |
| `scraper/config.py` | Board metadata, filters, and request settings |
| `scraper/requirements.txt` | Python dependency |
| `current_processor.py` | Shared listing schema, validation, and sorting |
| `listings.json` | Root copy of the generated dataset |
| `scraper/convert_legacy.py` | Utility for converting an older dataset to the current schema |

## Troubleshooting

- **Listings fail to load:** Make sure `ui/public/listings.json` exists and run the dashboard through Vite instead of opening `index.html` directly.
- **Search returns no results:** Try a shorter title or company name. Only listings marked `is_visible` are displayed.
- **A company is missing after a refresh:** Check the scraper output and the company's board token in `scraper/config.py`. A board may be unavailable or have no titles matching the configured keywords.
- **Bookmarks disappear:** Bookmarks belong to the browser and site origin where you saved them. Clearing site data or switching browsers, hostnames, or ports uses a different bookmark store.
