# Demonstration video: storyboard and narration

> **Note (27 October 2026):** This storyboard was written as a plan before the final recording. The final video, `FlightScope_Final_Presentation.mp4` (4 minutes 29 seconds), was made separately, and its narration may differ from the text below. This file is kept as a record of the plan.

**Target length:** 4:30–4:50 (the minimum is 4:00)
**Narration:** about 690 words in simple English
**Visuals:** your real screenshots from `docs/screenshots/`, plus two short live screen recordings of the app (≈ 30–40 s each)

---

## Easiest method: Microsoft Clipchamp with an AI voice

Clipchamp is free and already installed on Windows 11 (Start menu → "Clipchamp"). It has screen recording, image slides and **text-to-speech** in one place.

1. **Create a new video** (16:9).
2. **Import media:** drag in the whole `docs/screenshots/` folder.
3. **Record the two live clips:** *Record & create* → *Screen recording*. Start FlightScope with `run.bat` first. The clicks to make are listed in scenes 4 and 5.
4. **Add the AI voice:** *Record & create* → *Text to speech*. Language **English (United States or United Kingdom)**, choose a calm voice (for example "Jenny" or "Libby"), and paste the narration for **one scene at a time**. Set speed to **0.9×** if the total is shorter than 4:15.
5. **Place each voice clip** on the timeline and put the matching screenshots/clips above it. Stretch each image so it lasts as long as its narration.
6. **Optional:** add a text box with the scene title, and zoom (*Transform* → *Zoom*) on small details such as the 403 or the 401 message.
7. **Export** → **1080p**. Check that the video is at least 4 minutes long.

**Be transparent:** mention in your submission (or at the end of the video) that the narration was created with text-to-speech. Ask your teacher first if you are unsure whether an AI voice is allowed. You can also record your own voice in Clipchamp (*Record & create* → *Audio*) using the same script.

**Alternative:** record everything live with **Win + Alt + R** (Xbox Game Bar) while reading the script yourself.

---

## Storyboard

| # | Time | Visual | Narration |
|---|---|---|---|
| 1 | 0:00–0:25 | `07-dashboard-dark.png` (slow zoom-in) | Intro |
| 2 | 0:25–1:20 | `02-website-403.png` → `01-api-docs.jpg` → `03-api-401.jpg` | Research |
| 3 | 1:20–2:15 | `00b-python-working.png` → `00c-install-requests.png` → `05-code-client.jpg` → `06-server-running.png` | Implementation |
| 4 | 2:15–3:05 | **Live clip A** (actions below), or `08-arrivals.png` → `09-search-sk123.png` | Demo: airports, arrivals, search |
| 5 | 3:05–3:45 | **Live clip B** (actions below), or `10-status-and-delays.png` → `11-live-no-key.jpg` → `14-dashboard-light.png` → `15-mobile.jpg` | Demo: statuses, Live API message, themes, phone |
| 6 | 3:45–4:20 | `12-tests-ok.png` (take it first) → `16-invalid-input.jpg` | Testing and problems |
| 7 | 4:20–4:45 | `13-github-repo.jpg` → `17-gitignore.jpg` → `07-dashboard-dark.png` | GitHub and conclusion |

---

## Scene 1: Introduction (0:00–0:25)

**Visual:** `07-dashboard-dark.png`. Add the title text "FlightScope – Saiedeh Mangolian Shahrbabaki (Neda)".

> Hi, my name is Saiedeh Mangolian Shahrbabaki, Neda. This is FlightScope, my project for the reverse engineering assignment. FlightScope is a web application that shows departures and arrivals for Swedavia's ten Swedish airports. I built it with Python and Flask for the backend, and HTML, CSS and JavaScript for the web page.

## Scene 2: Research (0:25–1:20)

**Visual:** `02-website-403.png` (zoom on "Website status: 403") → `01-api-docs.jpg` (zoom on "Using the FlightInfo v2.0") → `03-api-401.jpg`.

> I started by studying the sample video. The user chooses an airport, departures or arrivals, and a date. The application then shows flights with times, destinations, gates and status.
>
> My first idea was to read the Swedavia website with a small Python script. But the server answered with status 403, Forbidden. The website does not allow scripts, so I needed a better data source.
>
> I found Swedavia's developer portal and the official FlightInfo API, version 2. In the documentation I learned the address format, that a subscription key must be sent in a header, and that all times are in UTC.
>
> When I call the API without a key, it answers 401, access denied. This shows that the address is correct, but a key is needed. I don't have a key yet, so I also built a demo mode.

## Scene 3: Implementation (1:20–2:15)

**Visual:** `00b-python-working.png` → `00c-install-requests.png` → `05-code-client.jpg` (zoom on `locationAndStatus`) → `06-server-running.png`.

> I started in Visual Studio Code by checking that Python works, and then I installed the requests library.
>
> The application has three main Python files. app.py is the Flask server. It checks all input, for example that the airport is one of the ten real airport codes, and it returns the flights as JSON.
>
> swedavia_client.py talks to the real API. It reads the key from a private file called dot env, so the key stays on the server and is never uploaded to GitHub. This function converts each flight into a simple format and changes UTC times to Swedish time.
>
> demo_data.py creates example flights in the same format as the real API, so demo mode uses the same code. To start the application on Windows, I just double-click run.bat.

## Scene 4: Live demonstration, part 1 (2:15–3:05)

**Live clip A, actions:**
1. Start on Stockholm Arlanda, Departures. Point the mouse at the yellow **Demo mode** banner.
2. Choose **Luleå** in the airport list.
3. Click **Arrivals**. Point at the "From" and "Baggage" columns.
4. Choose **Kiruna**. Type **SK123** in the search box (or any flight number you can see; demo flights change with the date).
5. Press **Esc** to clear the search.

> Now let's look at the application. First, notice the yellow banner. This is demo mode, so these flights are generated examples, not real flights.
>
> I can choose any of the ten airports. Here I choose Luleå and switch to arrivals. The column now says "From", and instead of check-in desks it shows the baggage belt.
>
> The search works immediately. When I search for flight SK123 at Kiruna, only that flight is shown. I can also search for an airline, a city or a gate. Pressing Escape clears the search.

## Scene 5: Live demonstration, part 2 (3:05–3:45)

**Live clip B, actions:**
1. Scroll to the table. Point at a crossed-out time and a "Delayed" status.
2. Click the **Delayed** filter, then **All**.
3. Click **Live API**. Show the red message. Click **Demo** again.
4. Click the **sun/moon button** for the light theme, then switch back.
5. Optional: press **F12**, turn on the phone view, show the cards, and close DevTools.

> Every flight has a coloured status. When a time changes, the old time is crossed out and the new time is shown. These buttons filter the flights by status.
>
> If I choose Live API without a key, the application does not crash. It explains that a key is needed. I want to be clear: Live mode has not been tested with real data yet, because I don't have an API key.
>
> The application also has a light theme, and on a phone the table changes into cards.

## Scene 6: Testing and problems (3:45–4:20)

**Visual:** `12-tests-ok.png` → `16-invalid-input.jpg`.

> I wrote 28 automated tests. They test input checks, time conversion, demo mode for all ten airports, and error handling in live mode, using fake API answers. All tests pass, and one is skipped because it only runs when a real key exists. For example, an invalid airport code gives a clear error message.
>
> I also solved real problems. The website blocked my script, so I switched to the official API. Some data fields were first read from the wrong place, and I fixed them by following the documentation. On Windows the app crashed because time-zone data was missing, and I fixed it by adding the tzdata package.

## Scene 7: GitHub and conclusion (4:20–4:45)

**Visual:** `13-github-repo.jpg` → `17-gitignore.jpg` → end on `07-dashboard-dark.png` with the text "github.com/nedababaki-pixel/flightscope-swedavia".

> The project is published on GitHub with a README and full documentation. The gitignore file makes sure that secret keys and temporary files are never uploaded, and my commits use a private email address.
>
> In this project I learned how to research and use an official API, keep secrets safe, handle errors, and write automated tests. My next step is to get my own API key and test live mode with real flight data. Thank you for watching!

---

## Final check before submitting

- [ ] The video is **4:00 or longer** (aim for 4:30–4:50)
- [ ] The voice is clear, and the music (if any) is quiet
- [ ] The Demo mode banner is visible whenever flights are shown
- [ ] The video never says that Live mode works with real data
- [ ] No API key, `.env` file, email inbox or private notification is visible
- [ ] If you used an AI voice, this is stated in the submission
