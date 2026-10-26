# FlightScope: Swedish Airport Flight Information Dashboard

A responsive flight information dashboard for Swedavia's ten Swedish airports, built with **Python, Flask, HTML, CSS and JavaScript**. I built it as a reverse-engineering school assignment and portfolio project. It recreates the idea of a Swedavia FlightInfo screen from a sample video and connects to the official **Swedavia FlightInfo API v2**.

> **Unofficial project.** Not affiliated with or endorsed by Swedavia. Demo mode shows generated example flights that are clearly labelled and are not real flight information.

<!-- Add screenshots after recording them (see docs/SCREENSHOT_CHECKLIST.md):
![Dashboard, dark theme](docs/screenshots/dashboard-dark.png)
![Mobile layout](docs/screenshots/mobile.png)
-->

## Features

- **All ten Swedavia airports:** Arlanda, Bromma, Landvetter, Malmö, Luleå, Umeå, Åre Östersund, Visby, Ronneby and Kiruna.
- **Departures and arrivals**, for any date from 7 days back to 90 days ahead. This is the window the API supports.
- **Instant search** by flight number (e.g. `SK123`), airline, city, gate, codeshare or status. Press `/` to jump to the search box and `Esc` to clear it.
- **Status filters** with live counts: Scheduled, Delayed, Boarding, Departed/Landed and Cancelled.
- **Summary cards:** total flights, on time, delayed, cancelled/diverted, and last update.
- **Changed times:** the old time is struck through and the new time is highlighted. The table also shows terminal, gate, check-in desks (departures) or baggage belt (arrivals), codeshares and remarks.
- **Demo mode** works offline with no API key. Generated data is fixed for each airport and date, and statuses follow the real clock.
- **Live mode** uses the official FlightInfo API v2, with a 60-second server-side cache.
- **Responsive design:** a table on desktop and cards on phones. Dark and light themes, with your choice remembered.
- **Accessibility:** skip link, labelled controls, native radio groups, `aria-pressed` filter buttons, an `aria-live` status region, a table caption, visible focus rings, and support for reduced motion.
- **Shareable URLs:** airport, date, mode, search and filter are kept in the address bar.
- **Auto-refresh** every 2 minutes while the tab is visible.

## Quick start (Windows)

**Option A: double-click.** Double-click **`run.bat`**. The first time, it creates a virtual environment and installs packages. Then open **http://127.0.0.1:5055**.

**Option B: VS Code terminal (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5055**. Stop the server with `Ctrl + C`.

> If PowerShell blocks `Activate.ps1`, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use `.venv\Scripts\activate.bat` in a Command Prompt.

Requirements: Python 3.10 or newer. Tested with Python 3.14 on Windows 11.

## Live Swedavia data (optional)

1. Create an account at <https://apideveloper.swedavia.se/> and subscribe to the **FlightInfo** product.
2. Copy `.env.example` to a new file named `.env` in the project folder.
3. Paste your subscription key after `SWEDAVIA_API_KEY=` in `.env`.
4. Restart `python app.py`. The start-up message says whether a key was found. Then choose **Live API** in the dashboard.

**Never** commit `.env`, show it on screen, or paste the key into chats. `.env` is already listed in `.gitignore`.

### How the integration works

These details are verified against Swedavia's official guide, *Using the FlightInfo API V2* (model version 2.0.0):

| Item | Value |
|---|---|
| Endpoint | `GET https://api.swedavia.se/flightinfo/v2/{airportIATA}/{arrivals or departures}/{yyyy-mm-dd}` |
| Authentication | Header `Ocp-Apim-Subscription-Key: <key>` |
| Data window | 7 days back to 90 days ahead |
| Times | Always UTC; FlightScope converts them to Europe/Stockholm |
| Status | `locationAndStatus.flightLegStatus` (SCH, ACT, LAN, CAN, DIV, …) and `flightLegStatusEnglish` |
| Gate / terminal | `locationAndStatus.gate`, `locationAndStatus.terminal` |
| Boarding | `locationAndStatus.gateAction` = `O` (gate open) |

A request without a key returns `401 Access denied due to missing subscription key`, which confirms that the endpoint exists. **Live data with a real key has not been tested yet**, because no subscription key was available during development. The parser is covered by tests that use payloads shaped like the official model.

## Running the tests

```powershell
python -m unittest discover -s tests -v
```

There are 28 tests covering pages, security headers, input validation, demo mode for all airports, API field mapping, status rules, time-zone conversion and live-mode error handling. Live mode is tested with a fake HTTP session, so no key or internet is needed. Other tests check that the key never appears in responses, and (once a real key is configured) not in any project file.

## Project structure

```
app.py                Flask routes, validation, security headers, error handling
swedavia_client.py    FlightInfo API v2 client, response normalizer, status rules, cache
demo_data.py          Generated demo flights in the official API format
templates/index.html  Dashboard markup (semantic, accessible)
static/style.css      Responsive design, dark and light themes
static/app.js         Data loading, search, filters, rendering, URL state
static/favicon.svg    App icon
tests/test_app.py     Automated tests (unittest)
run.bat               One-click start on Windows
requirements.txt      Flask, requests, python-dotenv, tzdata
.env.example          Template for your private .env (no real key)
DOCUMENTATION.md      Project report: research, implementation, testing, problems, conclusion
docs/                 GitHub guide, screenshot checklist, video script
```

## Security

- The API key is read from `.env` on the server only. It is never sent to the browser, put into HTML, returned in errors or logged.
- Every input (airport, direction, date, mode) is checked against an allow-list before it is used in the API URL.
- Upstream errors become short, safe messages. No stack traces or internal details are sent to users.
- A Content Security Policy (no inline scripts), `X-Frame-Options: DENY`, `nosniff` and `no-referrer` headers are set on every response.
- The frontend inserts API text with `textContent`, never `innerHTML`, which prevents XSS.
- The app listens on `127.0.0.1` only and runs with Flask debug mode off.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ZoneInfoNotFoundError: 'No time zone found with key Europe/Stockholm'` | Run `python -m pip install -r requirements.txt` (it installs `tzdata`, which Windows needs) |
| `Address already in use` / port 5055 busy | Another copy is running. Close it, or set `PORT=5056` in `.env` |
| Changes to HTML/CSS/JS don't appear | Restart `python app.py` (templates are cached), then press `Ctrl + F5` in the browser |
| Live API shows "API key was rejected" | Check the key in `.env` and that your portal subscription includes FlightInfo |
| `Activate.ps1 cannot be loaded` | See the note under Quick start, or just use `run.bat` |

## Limitations and next steps

- Live mode still needs to be tested with a real subscription key.
- The API expects the date in UTC. Flights just after midnight in Swedish time may appear under the previous UTC day.
- Flask's built-in server is for local use. A public deployment would need a production server such as waitress or gunicorn, plus HTTPS.
- Possible improvements: flight detail panel, Swedish language toggle, and the `/query` endpoint with continuation tokens for efficient updates.

## Credits

Flight data © Swedavia, through the public FlightInfo API. Built by Neda Babaki as part of an IT education assignment.
