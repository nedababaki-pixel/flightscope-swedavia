# FlightScope: Project Documentation

**Assignment:** Reverse engineering a Swedavia FlightInfo application (APL / IT internship)
**Author:** Neda Babaki
**Date:** October 2026
**GitHub:** <https://github.com/nedababaki-pixel/flightscope-swedavia>
**Technologies:** Python 3, Flask, Requests, HTML, CSS, JavaScript, unittest, VS Code, Git and GitHub

---

## 1. Introduction

The goal of this assignment was to look at a demonstration of Swedavia's FlightInfo service and rebuild a working application with the same purpose. This is called reverse engineering. I did not have the original source code, so I studied what the application does from the outside: what the user can choose, what information is shown, and where the data must come from. Then I designed and built my own version.

The result is **FlightScope**, a web dashboard that shows departures and arrivals for Swedavia's ten Swedish airports. You can search for flights and filter them by status. Because I do not have an API key yet, the application has a **Demo mode** with clearly labelled example flights.

## 2. Phase 1: Research

### 2.1 Analysing the sample

From the sample video I identified the inputs and outputs of the application:

| Inputs (what the user chooses) | Outputs (what the application shows) |
|---|---|
| Airport | Flight number and airline |
| Departures or arrivals | Destination or origin |
| Date | Scheduled time and new time |
| | Gate and terminal |
| | Flight status |

I concluded that the application needs structured flight data from an API.

### 2.2 Finding the data source

- First I tried to download `www.swedavia.se` with Python and the `requests` library. The server answered **HTTP 403 Forbidden**. The website does not allow scripts to read it, so it cannot be used as a data source.

<img src="docs/screenshots/02-website-403.png" alt="My first test script in VS Code. Requesting www.swedavia.se returned 'Website status: 403'." width="760">

*Figure 1: My first test script in VS Code. Requesting www.swedavia.se returned "Website status: 403". Screenshot taken by me.*

- Then I found Swedavia's developer portal (<https://apideveloper.swedavia.se/>). It offers a public **FlightInfo API v2**. To use it, you need a free subscription key.
- I read the official guide *Using the FlightInfo API V2* and wrote down the most important facts:
  - Address: `https://api.swedavia.se/flightinfo/v2/{airport}/{arrivals or departures}/{date}`
  - The key is sent in a header called `Ocp-Apim-Subscription-Key`
  - Data exists from 7 days back to 90 days ahead
  - All times are in UTC (not Swedish time)
  - Flight status and gate are inside a section called `locationAndStatus`
  - The ten airport codes are ARN, BMA, GOT, MMX, LLA, UME, OSD, VBY, RNB and KRN

<img src="docs/screenshots/01-api-docs.jpg" alt="The Swedavia developer portal. The FlightInfo API section links to 'Using the FlightInfo v2.0'." width="760">

*Figure 2: The Swedavia developer portal. The FlightInfo API section links to "Using the FlightInfo v2.0". Captured with the AI assistant's built-in browser.*

- When I called the API without a key, it answered **401: "Access denied due to missing subscription key"**. This shows that the address is correct and that a key is required.

<img src="docs/screenshots/03-api-401.jpg" alt="The FlightInfo API called without a key answers 401 'Access denied due to missing subscription key'." width="760">

*Figure 3: The FlightInfo API called without a key answers 401 "Access denied due to missing subscription key". Captured with the AI assistant's built-in browser.*

### 2.3 Choice of tools

| Tool | Why I chose it |
|---|---|
| Python and Flask | Simple backend that is easy to start on Windows with `python app.py` |
| Requests | Easy way to call an API, with a timeout |
| python-dotenv | Keeps the API key in a private `.env` file instead of in the code |
| tzdata | Gives Windows the time-zone data needed for Swedish time |
| HTML, CSS, JavaScript | Runs directly in the browser, no extra build tools needed |
| unittest | Built into Python, so no extra installation is needed |
| VS Code, Git, GitHub | Writing code, version control and publishing |
| Claude (AI assistant) | Code review, suggestions for improvements, and help with the documentation. I ran and tested the application myself. |

## 3. Phase 2: Implementation

### 3.1 How the application is built

```
Browser (index.html, app.js, style.css)
     |   asks for flights: /api/flights?airport=ARN&direction=departures&date=...&mode=demo
     v
Flask server (app.py)            checks the input, adds security headers, handles errors
     |-- demo_data.py            creates example flights (Demo mode)
     |-- swedavia_client.py      calls the real Swedavia API with the secret key (Live mode)
```

The browser never talks to Swedavia directly. Only the Flask server knows the API key, so the key stays secret.

### 3.2 Steps

1. **Project setup.** I created the project folder in VS Code, checked that Python works, and installed the packages from `requirements.txt`.

   <img src="docs/screenshots/00a-project-start.png" alt="Empty app.py" width="370"> <img src="docs/screenshots/00b-python-working.png" alt="Python test" width="370">

   *Figure 4: The start of the project: an empty `app.py`, then a first test that Python works. Screenshots taken by me.*

   <img src="docs/screenshots/00c-install-requests.png" alt="Installing requests" width="560">

   *Figure 5: Installing the `requests` library in the VS Code terminal. Screenshot taken by me.*

2. **Backend.** `app.py` has two main routes: `/` shows the web page and `/api/flights` returns flight data as JSON. All input is checked. For example, the airport must be one of the ten real airport codes, and the date must be within the range the API supports.
3. **API client.** `swedavia_client.py` builds the official API address, sends the key in the header and waits a maximum of 15 seconds. All errors (wrong key, no data, too many requests, timeout, broken data) become short, friendly messages.
   <img src="docs/screenshots/05-code-client.jpg" alt="normalize_flight code" width="760">

   *Figure 6: `normalize_flight` in `swedavia_client.py` reads status and gate from `locationAndStatus`, as described in the official API guide. The file list on the left shows the project structure. Captured with the AI assistant's built-in browser (GitHub view).*

4. **Converting the data.** The API returns a lot of fields. The client turns each flight into a simple format with flight number, airline, city, times, terminal, gate and status. UTC times are converted to Swedish time.
5. **Status rules.** Every flight gets one status: scheduled, delayed (15 minutes or more), boarding, departed, landed, cancelled or diverted. The status decides the colour and which filter the flight belongs to.
6. **Demo mode.** `demo_data.py` creates example flights in exactly the same format as the real API. Demo mode therefore uses the same code as Live mode. Every airport and date gets its own flights. Flights earlier in the day show as departed or landed.
7. **Web page.** The page has controls for airport, departures/arrivals, date and data source; summary cards; status filter buttons; a search box; and a flight table. On a phone the table turns into cards.
8. **Design.** Dark theme and light theme, clear colours for each status, and a layout that works on both computer and phone.

<img src="docs/screenshots/06-server-running.png" alt="FlightScope started with run.bat. The server runs at http://127.0.0.1:5055 in Demo mode because no API key is configured." width="760">

*Figure 7: FlightScope started with `run.bat`. The server runs at http://127.0.0.1:5055 in Demo mode because no API key is configured. Screenshot taken by me.*

### 3.3 Security

- The API key is only stored in `.env`. This file is listed in `.gitignore`, so it is never uploaded to GitHub.
- The key is never sent to the browser, never written to logs and never shown in error messages. Automated tests check this.
- All input is checked against fixed lists before it is used.
- Security headers protect against scripts from other websites and against the page being shown inside other sites.
- Text from the API is shown as plain text, which prevents cross-site scripting (XSS).
- The server only runs on the local computer (`127.0.0.1`) with debug mode turned off.

### 3.4 Accessibility

All controls have labels. The page can be used with the keyboard, and pressing `/` jumps to the search box. Screen readers are told when flights are loading, when an error happens or when no flights are found. Every status has text as well as colour. Animations are turned off for users who prefer reduced motion.

## 4. Phase 3: Testing and completion

### 4.1 Automated tests

Command:

```powershell
python -m unittest discover -s tests -v
```

**Result (26 October 2026, Windows 11, Python 3.14): 28 tests ran, 27 passed, 1 skipped.** The skipped test only runs when a real API key exists. It checks that the key is not saved in any project file.

| Test group | What is tested |
|---|---|
| Page and security | The page loads with all ten airports; security headers; static files; errors are returned as JSON |
| Input checks | Wrong airport, wrong direction, wrong date format, impossible date (30 February), dates outside the API range |
| Demo mode | Works for all 10 airports, both departures and arrivals; the same input gives the same flights; flights are sorted by time |
| Data conversion | UTC to Swedish time (winter and summer time); departure and arrival fields; all status types; broken data is skipped |
| Live mode with fake answers | Missing key; correct API address and header; wrong key (401/403); no data (404); too many requests (429); server error; timeout; broken data |
| Repository safety | `.env` is ignored by Git; `.env.example` contains no key |

<img src="docs/screenshots/12-tests-ok.png" alt="Automated tests passing in the VS Code terminal" width="760">

*Figure 8: The automated tests in the VS Code terminal (inside the `.venv` virtual environment): "Ran 28 tests … OK (skipped=1)". Screenshot taken by me.*

The Live mode tests use **fake API answers**. They show that the code handles answers in the documented format and all error cases. They do **not** prove that Live mode works with real Swedavia data.

### 4.2 Manual tests

**Tested by me on my Windows laptop:**

- [x] The application starts and runs
- [x] Choosing a different airport loads that airport's flights
- [x] Arrivals view (the heading, the "From" column and the baggage belt column change)
- [x] Dark mode
- [x] Searching for flight **SK123** gave exactly one result (Demo mode, Kiruna arrivals, 26 October 2026)
- [x] Light theme
- [x] Flight statuses, delays and cancellations are shown in the table

<img src="docs/screenshots/07-dashboard-dark.png" alt="The dashboard in dark mode (Stockholm Arlanda, arrivals, Demo mode)." width="760">

*Figure 9: The dashboard in dark mode (Stockholm Arlanda, arrivals, Demo mode). Screenshot taken by me.*

<img src="docs/screenshots/14-dashboard-light.png" alt="The same dashboard in the light theme (Stockholm Arlanda, departures)." width="760">

*Figure 10: The same dashboard in the light theme (Stockholm Arlanda, departures). Screenshot taken by me.*

<img src="docs/screenshots/08-arrivals.png" alt="Arrivals at Luleå. The table shows 'From', terminal and gate, baggage belt, codeshare numbers, and a cancelled flight with a remark." width="760">

*Figure 11: Arrivals at Luleå. The table shows "From", terminal and gate, baggage belt, codeshare numbers, and a cancelled flight with a remark. Screenshot taken by me.*

<img src="docs/screenshots/09-search-sk123.png" alt="Manual test: searching for SK123 at Kiruna arrivals shows exactly one flight ('1 of 9 flights shown')." width="760">

*Figure 12: Manual test: searching for SK123 at Kiruna arrivals shows exactly one flight ("1 of 9 flights shown"). Screenshot taken by me.*

<img src="docs/screenshots/10-status-and-delays.png" alt="Kiruna arrivals. Changed times are crossed out with the new time below, and each flight has a coloured status: Landed, Cancelled, Scheduled or 'Delayed 20 min'." width="760">

*Figure 13: Kiruna arrivals. Changed times are crossed out with the new time below, and each flight has a coloured status: Landed, Cancelled, Scheduled or "Delayed 20 min". Screenshot taken by me.*


**Also checked during development (AI-assisted testing in the browser and terminal):**

- [x] Starting with `run.bat` on a clean installation (it creates the virtual environment and installs the packages)
- [x] Searching for a city ("copen" shows only Copenhagen flights)
- [x] Status filter buttons show the right numbers and filter the table
- [x] Live mode without a key shows a clear message and a "Try again" button instead of crashing
- [x] Light theme
- [x] Phone size (375 pixels wide): the table becomes cards and the page does not scroll sideways
- [x] An invalid airport in the address (`airport=XXX`) gives a clear 400 error

<img src="docs/screenshots/11-live-no-key.jpg" alt="Live API selected without a key. The application shows a clear message and a 'Try again' button instead of crashing." width="760">

*Figure 14: Live API selected without a key. The application shows a clear message and a "Try again" button instead of crashing. Captured with the AI assistant's built-in browser.*

<img src="docs/screenshots/15-mobile.jpg" alt="Phone layout" width="300">

*Figure 15: Phone size (375 px). The table changes into cards. Captured with the AI assistant's built-in browser.*

<img src="docs/screenshots/16-invalid-input.jpg" alt="Input check: /api/flights?airport=XXX returns the JSON error 'Unknown airport'." width="760">

*Figure 16: Input check: /api/flights?airport=XXX returns the JSON error "Unknown airport". Captured with the AI assistant's built-in browser.*


**Not tested yet:**

- [ ] Using the whole page with only the keyboard
- [ ] **Live mode with a real API key.** I do not have a subscription key yet, so Live mode has not been tested with real flight data.

### 4.3 Publishing on GitHub

The project is published at <https://github.com/nedababaki-pixel/flightscope-swedavia>. Before publishing I checked that:

- no passwords, API keys or `.env` file are included;
- the virtual environment (`.venv`) and temporary Python files are not uploaded;
- commits use my private GitHub **noreply** email address instead of my personal email.

<img src="docs/screenshots/13-github-repo.jpg" alt="The public GitHub repository with all project files." width="760">

*Figure 17: The public GitHub repository with all project files. Captured with the AI assistant's built-in browser.*

<img src="docs/screenshots/17-gitignore.jpg" alt=".gitignore on GitHub. The .env file with the secret key, the virtual environment and temporary files are never uploaded." width="760">

*Figure 18: `.gitignore` on GitHub. The `.env` file with the secret key, the virtual environment and temporary files are never uploaded. Captured with the AI assistant's built-in browser.*

## 5. Phase 4: Problems and solutions

| # | Problem | Cause | Solution |
|---|---|---|---|
| 1 | Downloading `www.swedavia.se` with Python returned **HTTP 403 Forbidden** | The website blocks scripts. It is not an API. | I stopped trying to read the website and used the official FlightInfo API v2 instead (Figures 1–3) |
| 2 | I had no API key | Live data needs a personal subscription | I built a clearly labelled Demo mode that uses the same data format as the real API, and tested Live mode with fake API answers |
| 3 | The first version read status and gate from the **wrong fields** | The code was based on guesses, not on the documentation | A code review against the official API guide showed the correct fields (`locationAndStatus`). The code was rewritten to use them, and tests were added |
| 4 | On Windows the application **crashed at start**: `No time zone found with key Europe/Stockholm` | Windows does not include the time-zone database that Python needs | I added the `tzdata` package to `requirements.txt` |
| 5 | Demo mode showed the **same six flights** for every airport and date | The demo data ignored what the user chose | Demo flights are now created per airport, direction and date |
| 6 | Changes to the HTML page did not appear while the server was running | Flask keeps the page in memory when debug mode is off | Restart the server after changing the page (written in the README) |
| 7 | My personal email could become public on GitHub | Git puts the author's email in every commit | I turned on email privacy on GitHub and used my noreply address for this project |

Problems 3–5 were found during an AI-assisted code review, when the code was compared with the official API documentation and tested on Windows.

## 6. Conclusion

I built a working flight information dashboard by studying a sample application and recreating its function with my own code. The most important things I learned:

- how to **find and read official API documentation**, and why reading a website with a script is the wrong approach;
- how to **keep secrets safe**: the API key lives in `.env` and only the server uses it;
- that it is important to **check my assumptions against the documentation**, because this found real bugs;
- how to make an application **robust** with input checks, timeouts and clear error messages;
- how **automated tests with fake API answers** let me test code without internet or a key;
- how to build a **responsive and accessible** web page with HTML, CSS and JavaScript;
- how to **publish a project on GitHub safely**.

**Next steps:** get my own API key and test Live mode with real flight data, add a page with more details for each flight, and add a Swedish language option.

## 7. References

- Swedavia API developer portal: <https://apideveloper.swedavia.se/>
- Swedavia, *Using the FlightInfo API V2* (PDF): <https://apideveloper.swedavia.se/content/Using_the_FlightInfo_API.pdf>
- Flask documentation: <https://flask.palletsprojects.com/>
- Requests documentation: <https://requests.readthedocs.io/>
- MDN Web Docs: <https://developer.mozilla.org/>

## Appendix: related files

- `README.md`: installation and overview
- `docs/GITHUB_GUIDE.md`: how to publish safely to GitHub
- `docs/SCREENSHOT_CHECKLIST.md`: screenshots for the report
- `docs/VIDEO_SCRIPT.md`: narration and scene guide for the demonstration video
