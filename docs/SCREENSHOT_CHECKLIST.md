# Screenshot checklist

Save all screenshots in the folder `docs/screenshots/` with the file names below.
On Windows, press **Win + Shift + S** to take a screenshot of part of the screen.

**Before every screenshot, check that these are NOT visible:** the `.env` file, any API key, your email inbox, other browser tabs, chat apps and pop-up notifications.

**Start the app first:** double-click `run.bat` (or run `python app.py`) and open <http://127.0.0.1:5055>.

> **Demo data changes with the date.** Flight numbers and statuses depend on the day you take the screenshot. Flight SK123 (Kiruna arrivals) existed on 26 October 2026. On another day, search for any flight number you can see in the table.

---

## Required screenshots

| ✓ | File name | How to take it | Used in |
|---|---|---|---|
| ☐ | `01-api-docs.png` | Open <https://apideveloper.swedavia.se/documentation> and capture the FlightInfo section (or the first page of the FlightInfo PDF) | Report 2.2, Video scene 2 |
| ☐ | `02-website-403.png` | In the VS Code terminal run: `python -c "import requests; print(requests.get('https://www.swedavia.se').status_code)"`. It prints **403**. | Report 2.2 / 5, Video scene 2 |
| ☐ | `03-api-401.png` | Open `https://api.swedavia.se/flightinfo/v2/ARN/departures/2026-10-26` in the browser (use today's date). It shows **401, missing subscription key**. | Report 2.2, Video scene 2 |
| ☐ | `04-vscode-project.png` | VS Code with the Explorer open, showing all project folders and files | Report 3, Video scene 3 |
| ☐ | `05-code-client.png` | `swedavia_client.py` scrolled to the `normalize_flight` function (shows `locationAndStatus`) | Report 3.2, Video scene 3 |
| ☐ | `06-server-running.png` | The terminal after starting the app, showing "FlightScope running at http://127.0.0.1:5055" | Report 3, Video scene 3 |
| ☐ | `07-dashboard-dark.png` | Full dashboard, Stockholm Arlanda, departures, **dark theme**. The yellow "Demo mode" banner must be visible. | Report 1 and 4, README, Video scene 4 |
| ☐ | `08-arrivals.png` | Göteborg Landvetter, **Arrivals**, showing the "From" and "Baggage" columns | Report 4.2, Video scene 4 |
| ☐ | `09-search.png` | Search for a flight number (e.g. **SK123** for Kiruna arrivals on 26 Oct 2026), showing exactly one result | Report 4.2, Video scene 4 |
| ☐ | `10-filter-delayed.png` | Click the **Delayed** filter. Old times are crossed out and new times are shown. | Report 4.2, Video scene 5 |
| ☐ | `11-live-no-key.png` | Choose **Live API**. The red message explains that an API key is needed. | Report 4.2, Video scene 5 |
| ☐ | `12-tests-ok.png` | Terminal: `python -m unittest discover -s tests -v`, scrolled to the end: **Ran 28 tests … OK (skipped=1)** | Report 4.1, Video scene 6 |
| ☐ | `13-github-repo.png` | Your repository page on GitHub, showing the files and the README | Report 4.3, Video scene 7 |

## Recommended screenshots

| ✓ | File name | How to take it | Used in |
|---|---|---|---|
| ☐ | `14-dashboard-light.png` | The same view as `07`, but with the **light theme** (sun/moon button at the top right) | README, Video scene 5 |
| ☐ | `15-mobile.png` | Press **F12** in the browser, click the phone/tablet icon and choose a phone. The flights appear as cards. | Report 4.2, README, Video scene 5 |
| ☐ | `16-invalid-input.png` | Open `http://127.0.0.1:5055/api/flights?airport=XXX`. It shows the JSON error "Unknown airport". | Report 4.2 |
| ☐ | `17-gitignore.png` | `.gitignore` open in VS Code, showing that `.env` and `.venv/` are ignored | Report 3.3 and 4.3 |

## Do NOT take

- ✗ Any screenshot of a real API key or the `.env` file
- ✗ Screenshots of "live data". Live mode has not been tested with a real key.
- ✗ Your GitHub email settings page (it shows your personal email address)

## After taking the screenshots

1. Put the files in `docs/screenshots/`.
2. In `README.md`, delete the line starting with `<!--` and the `-->` line around the two image links (the file names already match).
3. Commit and push:

   ```powershell
   git add docs/screenshots README.md
   git commit -m "Add screenshots"
   git push
   ```
