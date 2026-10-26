# Demonstration video: scene guide and narration

**Length:** about 4 minutes 45 seconds (about 630 spoken words at a calm speed)
**Format:** screen recording with your voice. Use English throughout.

## Before you record

1. Start the app with `run.bat` and open <http://127.0.0.1:5055>. Set the browser zoom to 100 %.
2. Open VS Code with the project folder. **Close `.env` if it exists.** Do not show any API key.
3. Close your email, chat apps and other browser tabs. Turn on **Focus assist / Do not disturb** in Windows.
4. Have the screenshots `01`, `02` and `03` ready (see `SCREENSHOT_CHECKLIST.md`). You can show them in the Windows Photos app or as browser tabs.
5. Choose a recording tool: **Win + Alt + R** (Xbox Game Bar, records one window) or **OBS Studio** (records the whole screen).
6. Do one practice run. Demo flights depend on the date, so check which flight number you will search for (scene 4).

**Tip:** read the narration slowly. Pausing is fine, and short silences while you click are normal.

---

## Scene 1: Introduction (0:00–0:25)

**Show:** the FlightScope dashboard in dark mode (Stockholm Arlanda, Departures). Slowly scroll from the top to the flight table.

**Say:**
> "Hi, my name is Neda Babaki. This is FlightScope, my project for the reverse engineering assignment. FlightScope is a web application that shows departures and arrivals for Swedavia's ten Swedish airports. I built it with Python and Flask for the backend, and HTML, CSS and JavaScript for the web page."

## Scene 2: Research (0:25–1:15)

**Show:** screenshot `02-website-403.png` → screenshot `01-api-docs.png` → screenshot `03-api-401.png`.

**Say:**
> "I started by looking at the sample video. The user chooses an airport, departures or arrivals, and a date. The application then shows flights with times, destinations, gates and status.
>
> First I tried to download the Swedavia website with Python, but the server answered 403 Forbidden. The website does not allow scripts, so I needed another data source.
>
> I found Swedavia's developer portal and the official FlightInfo API, version 2. I read the documentation and learned the API address, that a subscription key must be sent in a header, and that all times are in UTC.
>
> When I call the API without a key, it answers 401. That shows the address is correct, but a key is needed. I don't have a key yet, so I also built a demo mode."

## Scene 3: Implementation (1:15–2:05)

**Show:** VS Code. Click through the files in this order: `app.py` → `swedavia_client.py` (scroll to `normalize_flight`) → `demo_data.py` → `templates/index.html` → `static/app.js`. End with the terminal showing "FlightScope running…" (or screenshot `06-server-running.png`).

**Say:**
> "Here is the project in VS Code. `app.py` is the Flask server. It checks all input, for example that the airport is one of the ten real airport codes, and it returns the flights as JSON.
>
> `swedavia_client.py` talks to the real API. It reads the key from a private `.env` file, so the key stays on the server and is never sent to the browser or uploaded to GitHub. It also converts the flight data and changes UTC times to Swedish time.
>
> `demo_data.py` creates example flights in exactly the same format as the real API. So demo mode uses the same code as live mode.
>
> The web page is one HTML file, one CSS file and one JavaScript file. JavaScript loads the flights and handles search and filters."

## Scene 4: Live demonstration, part 1 (2:05–3:05)

**Show and do (in the browser):**
1. Point at the yellow **Demo mode** banner.
2. Change the airport to **Göteborg Landvetter**.
3. Click **Arrivals**. Point at the "From" and "Baggage" columns.
4. Change the airport to **Kiruna**. Type a flight number in the search box (**SK123** if you record on 26 October 2026; otherwise any flight number you see). Show the single result.
5. Press **Esc** to clear the search.

**Say:**
> "Now I will show the application. First, notice the yellow banner. This is demo mode, so these flights are generated examples, not real flights.
>
> I can choose any of the ten airports. I'll choose Göteborg Landvetter and switch to arrivals. The column now says 'From', and instead of check-in desks it shows the baggage belt.
>
> The search works immediately. If I type a flight number, only that flight is shown. I can also search for an airline, a city or a gate. Escape clears the search."

## Scene 5: Live demonstration, part 2 (3:05–3:50)

**Show and do:**
1. Click the **Delayed** filter. Point at a crossed-out time and the new time.
2. Click **All** again.
3. Click **Live API**. Show the red message. Click **Demo** again.
4. Click the **theme button** (top right) to show the light theme, then switch back.
5. Optional: press **F12**, turn on the phone view, and show the cards. Close DevTools.

**Say:**
> "These buttons filter the flights by status, and each one shows how many flights there are. Here are the delayed flights. The old time is crossed out and the new time is shown.
>
> If I choose Live API without a key, the application does not crash. It explains that a key is needed. Live mode has not been tested with real data yet, because I don't have a key.
>
> There is also a light theme, and on a phone the table changes into cards."

## Scene 6: Testing and problems (3:50–4:25)

**Show:** the VS Code terminal. Run `python -m unittest discover -s tests -v` and scroll to **"Ran 28 tests … OK"**. Then show the problems table in `DOCUMENTATION.md` (section 5).

**Say:**
> "I have 28 automated tests. They test input checks, time conversion, demo mode for all airports, and error handling in live mode with fake API answers. All tests pass; one is skipped because it only runs with a real key.
>
> Some problems I solved were the 403 from the website, data fields that were read from the wrong place, and a crash on Windows because the time-zone data was missing. I fixed that by adding the tzdata package."

## Scene 7: GitHub and conclusion (4:25–4:50)

**Show:** the GitHub repository page: <https://github.com/nedababaki-pixel/flightscope-swedavia>. Scroll down to the README.

**Say:**
> "The project is published on GitHub with a README and documentation. I made sure no API keys or personal email addresses are included.
>
> In this project I learned how to use official API documentation, keep secrets safe, handle errors and write tests. My next step is to get an API key and test live mode with real flight data. Thank you for watching."

---

## Checklist after recording

- [ ] The video is **at least 4 minutes** long (aim for 4:30–5:00)
- [ ] The sound is clear and not too quiet
- [ ] No API key, `.env` file, personal email or private notifications are visible
- [ ] You never say that Live mode works with real data
- [ ] The Demo mode banner is visible when you show flights
