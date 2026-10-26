# Screenshot & evidence checklist

Save the screenshots in `docs/screenshots/` with the suggested file names. On Windows, use **Win + Shift + S** to capture an area.

**Before every screenshot:** make sure `.env`, API keys, personal e-mails, other browser tabs and notifications are **not visible**.

## Phase 1: Research

| ✓ | File name | What to capture |
|---|---|---|
| ☐ | `01-sample-video.png` | A frame of the supplied sample video (only if you are allowed to share it) |
| ☐ | `02-swedavia-403.png` | Terminal showing the HTTP 403 response from `www.swedavia.se` |
| ☐ | `03-developer-portal.png` | The Swedavia API developer portal / FlightInfo documentation page |
| ☐ | `04-api-401-no-key.png` | Browser or terminal showing the `401 missing subscription key` response from `api.swedavia.se/flightinfo/v2/ARN/departures/<date>` |

## Phase 2: Implementation

| ✓ | File name | What to capture |
|---|---|---|
| ☐ | `05-vscode-structure.png` | VS Code Explorer showing the project folders and files |
| ☐ | `06-backend-code.png` | `app.py` showing the `/api/flights` route and its validation |
| ☐ | `07-api-client-code.png` | `swedavia_client.py` showing `normalize_flight` (the `locationAndStatus` mapping) |
| ☐ | `08-server-running.png` | Terminal after `python app.py`, showing "FlightScope running at http://127.0.0.1:5055" |

## Phase 3: Completion & testing

| ✓ | File name | What to capture |
|---|---|---|
| ☐ | `dashboard-dark.png` | Full dashboard, Arlanda departures, dark theme (use this in the README) |
| ☐ | `dashboard-light.png` | The same view in the light theme |
| ☐ | `09-arrivals.png` | Arrivals for another airport (e.g. Göteborg Landvetter) showing "From" and "Baggage" |
| ☐ | `10-search.png` | Search for a city, e.g. "copen", with the filtered result |
| ☐ | `11-filter-delayed.png` | The **Delayed** filter selected, showing struck-through old times and new times |
| ☐ | `12-live-no-key.png` | Live API selected without a key, showing the friendly error message |
| ☐ | `13-invalid-input.png` | Browser at `http://127.0.0.1:5055/api/flights?airport=XXX`, showing the JSON 400 error |
| ☐ | `mobile.png` | Phone layout: browser DevTools (F12 → device toolbar → iPhone), cards instead of table |
| ☐ | `14-tests-passing.png` | Terminal: `python -m unittest discover -s tests -v` ending in `OK` |
| ☐ | `15-live-data.png` | **Only if you have a real key:** live data for an airport. Hide the key! |

## Phase 4–5: Problems, solutions & GitHub

| ✓ | File name | What to capture |
|---|---|---|
| ☐ | `16-tzdata-error.png` | Optional: the `ZoneInfoNotFoundError` (temporarily uninstall `tzdata` in a test venv to reproduce it) |
| ☐ | `17-gitignore.png` | `.gitignore` showing `.env`, and `git status` without `.env` |
| ☐ | `18-github-repo.png` | The published GitHub repository page with the README |
