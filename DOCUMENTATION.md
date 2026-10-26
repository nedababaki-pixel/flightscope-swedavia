# FlightScope: Project Documentation

**Assignment:** Reverse engineering a Swedavia FlightInfo application (APL assignment)
**Author:** Neda Babaki
**Technologies:** Python 3, Flask, Requests, HTML5, CSS3, JavaScript (no frameworks), unittest, VS Code, Git/GitHub
**Language of all deliverables:** English

> **Editing note:** sections marked ✏️ contain details only you know, such as the dates you worked and what the sample video showed. Check and adjust them so the report describes your own work accurately. Do not claim anything you have not done, especially live API testing.

---

## 1. Introduction

The aim of the assignment was to rebuild a working application from a supplied demonstration of Swedavia's FlightInfo service, using reverse-engineering principles. Instead of reading the original source code, I studied the observable behaviour: what the user enters, what the application shows, and which data source it must use. I then designed and built my own application with the same purpose.

The result is **FlightScope**, a responsive web dashboard. It shows departures and arrivals for Swedavia's ten Swedish airports, with search, status filters, a summary and a clearly labelled demo mode.

## 2. Phase 1: Research

### 2.1 Analysing the sample ✏️

By watching the sample video, I identified:

| Inputs (what the user chooses) | Outputs (what the app shows) |
|---|---|
| Airport | Flight number and airline |
| Departures or arrivals | Destination or origin city |
| Date | Scheduled time and new/estimated time |
| Search text | Gate and terminal |
| | Flight status (on time, delayed, boarding, departed, landed, cancelled) |

From this, I concluded that the application must get structured flight data from an API, not from the Swedavia web page.

### 2.2 Finding the data source

- My first attempt was to request `www.swedavia.se` directly from Python with `requests`. The server answered **HTTP 403 Forbidden**. The public website is not meant to be read by scripts, and scraping it would be unreliable and against the site's intent.
- I then found Swedavia's developer portal, <https://apideveloper.swedavia.se/>. It offers a public **FlightInfo API v2** that needs a free subscription key.
- I read the official PDF guide, *Using the FlightInfo API V2*, and noted the key facts:
  - Endpoints: `GET https://api.swedavia.se/flightinfo/v2/{airportIATA}/arrivals/{date}` and `.../departures/{date}`
  - Authentication: header `Ocp-Apim-Subscription-Key`
  - Data is kept from 7 days back to 90 days ahead. All times are UTC.
  - Flight status is in `locationAndStatus.flightLegStatus`, with codes such as SCH (scheduled), ACT (active), LAN (landed), CAN (cancelled) and DIV (diverted). The gate is in `locationAndStatus.gate`.
  - Valid IATA codes for the ten airports: ARN, BMA, GOT, MMX, LLA, UME, OSD, VBY, RNB, KRN.
- A test request without a key returned `401 – Access denied due to missing subscription key`. This confirmed that the endpoint exists and that authentication is required.

### 2.3 Choice of tools

| Tool | Reason |
|---|---|
| **Python + Flask** | Small, readable backend; easy to run on Windows with `python app.py` |
| **Requests** | Simple, reliable HTTP client with timeouts |
| **python-dotenv** | Keeps the API key in a private `.env` file instead of in the code |
| **tzdata** | Gives Windows the time-zone data needed for Swedish time |
| **HTML/CSS/JavaScript** | No build step, so the whole project runs without Node.js |
| **unittest** | Built into Python, so no extra test dependency is needed |
| **VS Code, Git, GitHub** | Editing, version control and publishing |
| **Claude (AI assistant)** | Code review, refactoring suggestions and documentation drafts. I reviewed, ran and tested all generated code myself. |

## 3. Phase 2: Implementation

### 3.1 Architecture

```
Browser (index.html + app.js + style.css)
      │  fetch('/api/flights?airport=ARN&direction=departures&date=…&mode=demo|live')
      ▼
Flask backend (app.py)  ── validates input, adds security headers, handles errors
      │
      ├── demo_data.py        → generates example flights in the official API format
      └── swedavia_client.py  → calls the FlightInfo API v2 with the secret key (server-side only),
                                 normalizes the response, caches it for 60 seconds
```

The browser never talks to Swedavia directly. This keeps the API key secret, because only the Flask server knows it.

### 3.2 Steps taken

1. **Project setup.** Created the folder in VS Code, checked Python with `python --version`, and installed packages from `requirements.txt`.
2. **Backend.** Created `app.py` with two routes: `/` (the page) and `/api/flights` (JSON data). Every parameter is checked against an allow-list. For example, the airport must be one of the ten official codes.
3. **API client.** `swedavia_client.py` builds the official URL, sends the subscription-key header, sets a 15-second timeout, and turns every possible failure (401/403, 404, 429, 5xx, timeout, invalid JSON) into a clear, safe message.
4. **Normalization.** The raw API objects are converted into one simple format for the frontend: flight, airline, city, scheduled time, new time, terminal, gate, status, category, codeshares and remarks. Times are converted from UTC to Europe/Stockholm. Field names are read case-insensitively, because the documentation uses `PascalCase` while JSON normally uses `camelCase`.
5. **Status rules.** Each flight gets one category that drives the colours and filters:
   cancelled (CAN/FLS) → diverted (DIV/RER) → landed (LAN) → departed (ACT or actual time) → delayed (15+ min late) → boarding (gate open) → on time.
6. **Demo mode.** `demo_data.py` generates example flights in exactly the same JSON shape as the real API. Because demo data goes through the same parser, demo mode also tests the live-data code path. The data is fixed for each airport, direction and date, and statuses change during the day.
7. **Frontend.** I wrote a semantic HTML page with a filter form, summary cards, status filter buttons and a flight table that turns into cards on phones. `app.js` loads data with `fetch`, and searches and filters in the browser without reloading. It keeps the current view in the URL and refreshes automatically every two minutes.
8. **Design.** A dark aviation theme with a light theme option, a consistent colour system for statuses, readable tabular numbers and a mobile-first responsive layout.
9. **Security and accessibility.** Covered in sections 4.3 and 4.4.

## 4. Phase 3: Completion and testing

### 4.1 Automated tests

Run with:

```powershell
python -m unittest discover -s tests -v
```

**Result on 2026-10-26 (Windows 11, Python 3.14.3), run both with the system Python and in the fresh `.venv` created by `run.bat`: 28 tests ran; 27 passed and 1 was skipped.** The skipped test only runs when a real API key is configured. It checks that the key does not appear in any project file.

| Test group | What it checks |
|---|---|
| Page & security | Page loads with all ten airports; CSP and other security headers; static files; JSON 404 for unknown API routes; key never exposed |
| Validation | Unknown airport, invalid direction or mode, malformed date, impossible date (Feb 30), dates outside the API window → HTTP 400 |
| Demo mode | Works for all 10 airports × 2 directions; same input gives the same data; sorted by time; different airports give different flights; statuses follow the clock |
| Normalization | UTC→Swedish time in winter and summer; departure and arrival field mapping; PascalCase payloads; every status category; deleted or broken flights skipped |
| Live mode (fake HTTP) | Missing key → 503; correct official URL and header; caching; 401/403/404/429/500; timeout; connection error; invalid JSON |
| Repository hygiene | `.env` is git-ignored; `.env.example` contains no key |

### 4.2 Manual tests

**Tested by me on my Windows laptop:**

- [x] The application starts and runs successfully
- [x] Airport selection loads the flights for the chosen airport
- [x] Arrivals view works (heading, "From" column and baggage belt update)
- [x] Dark mode
- [x] Searching for flight **SK123** returned exactly one result (Demo mode, Kiruna arrivals, 26 October 2026). Demo flights are generated per date, so the same flight number may not exist on other days.

**Also checked during development, in the browser and the terminal:**

- [x] The app starts with `python app.py` and with `run.bat` (which also creates the virtual environment on a fresh install)
- [x] Departures/arrivals switching for several airports
- [x] Searching for a city ("copen" shows only Copenhagen)
- [x] Status filter buttons show correct counts and filter the table
- [x] Live mode without a key shows a clear setup message and a "Try again" button, not a crash
- [x] Light theme
- [x] Phone width (375 px): table becomes cards, no horizontal scrolling

**Not yet tested:**

- [ ] Keyboard only: Tab through all controls, `/` focuses search, `Esc` clears it
- [ ] Live mode with a real subscription key *(no key available yet)*

### 4.3 Security measures

- The API key is stored only in `.env`, which is excluded by `.gitignore`. The key is used only on the server: it is never sent to the browser, logged, or included in error messages. Tests check this.
- Input allow-lists stop path manipulation of the upstream URL.
- A Content Security Policy blocks inline and third-party scripts. Clickjacking and MIME-sniffing protection headers are set.
- All API text is inserted with `textContent`, which prevents cross-site scripting.
- The server binds to `127.0.0.1` with debug mode off.

### 4.4 Accessibility measures

A skip link; labels for every control; native radio buttons for the flight type and data source, so arrow keys work; `aria-pressed` on filter buttons; an `aria-live` region that announces loading, errors and empty results; a table caption and column headers; visible focus outlines; colour combined with text for every status; and `prefers-reduced-motion` support.

## 5. Phase 4: Problems and solutions

These are real problems I met during the project:

| # | Problem | Cause | Solution |
|---|---|---|---|
| 1 | Requesting `www.swedavia.se` from Python returned **HTTP 403** | The public website blocks automated requests; it is not an API | Stopped scraping and switched to the official FlightInfo API v2 from the developer portal |
| 2 | No API key available during development | Live access needs a personal subscription | Built a clearly labelled **demo mode** in the official API format, and tested live mode with fake HTTP responses |
| 3 | When I checked the first version against the official PDF, **status and gate were read from the wrong fields** (`flightStatus`, `gate` at the top level) | The parser was based on assumptions, not on the documentation | Rewrote the parser to use `locationAndStatus.flightLegStatus`, `flightLegStatusEnglish`, `gate`, `terminal` and `gateAction`, and added tests with payloads shaped like the official model |
| 4 | On Windows the app crashed at start-up with `ZoneInfoNotFoundError: 'No time zone found with key Europe/Stockholm'` | Windows has no built-in IANA time-zone database, which Python's `zoneinfo` needs | Added the `tzdata` package to `requirements.txt` |
| 5 | Demo mode showed the same six flights for every airport and date | Demo data ignored the user's choices | Demo flights are now generated per airport, direction and date, with realistic domestic and international routes |
| 6 | Changes to the HTML did not show up while the server was running | With debug off, Flask caches templates | Restart the server after editing templates (see Troubleshooting in the README) |
| 7 | Changing filters quickly could show results from an older, slower request | Requests can finish out of order | Each request gets an ID; responses from outdated requests are ignored |
| 8 | Live API times are in UTC, but users think in Swedish time | API design | All times are converted to Europe/Stockholm, including summer/winter time; covered by tests |

## 6. Conclusion

I built a working flight information dashboard by reverse engineering the sample. I identified its inputs, outputs and data source, then implemented my own solution with Python and Flask. The project taught me:

- how to find and read **official API documentation**, and why scraping a website is the wrong approach;
- how to keep **secrets out of code and out of the browser**, using environment variables and a backend proxy;
- the value of **checking assumptions against documentation**, which revealed real mapping bugs;
- how to make software **robust** with input validation, timeouts and user-friendly error messages;
- how **automated tests** with fake HTTP responses let me test API code without network access;
- **responsive and accessible** frontend design with plain HTML, CSS and JavaScript.

**Next steps:** test live mode with my own subscription key and adjust the parser if real responses differ; add a flight-details view; add a Swedish language option; and deploy with a production WSGI server and HTTPS if it ever goes online.

## 7. References

- Swedavia API developer portal: <https://apideveloper.swedavia.se/>
- Swedavia, *Using the FlightInfo API V2* (PDF, model version 2.0.0): <https://apideveloper.swedavia.se/content/Using_the_FlightInfo_API.pdf>
- Flask documentation: <https://flask.palletsprojects.com/>
- Requests documentation: <https://requests.readthedocs.io/>
- MDN Web Docs, ARIA and accessible tables: <https://developer.mozilla.org/>

## Appendix: related documents

- `README.md`: setup and overview
- `docs/GITHUB_GUIDE.md`: how to publish safely to GitHub
- `docs/SCREENSHOT_CHECKLIST.md`: evidence screenshots to take
- `docs/VIDEO_SCRIPT.md`: narration for the 4–5 minute demonstration video
