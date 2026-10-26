# Demonstration video script (about 4:30)

**Setup before recording**

- Start the app (`python app.py`) and open http://127.0.0.1:5055 in a clean browser window at 100 % zoom.
- Open VS Code with the project. Close `.env`, e-mail, chats and notifications (Windows: Focus assist on).
- Have a terminal ready for the tests.
- Recording tool: **Win + Alt + R** (Xbox Game Bar) or OBS Studio. Speak slowly and clearly.

---

### 0:00–0:30 Introduction *(screen: dashboard, dark theme)*

> "Hi, my name is Neda. In this video I present FlightScope, a flight information dashboard for Sweden's ten Swedavia airports. The assignment was to reverse engineer a Swedavia FlightInfo application from a sample video: study what it does from the outside, then build my own working version. I built it with Python and Flask on the backend, and plain HTML, CSS and JavaScript on the frontend."

### 0:30–1:15 Research *(screen: developer portal / API PDF, then the 401 screenshot)*

> "First I analysed the sample. The inputs are an airport, departures or arrivals, and a date. The outputs are flights with times, destinations, gates and status.
> My first idea was to request the Swedavia website directly from Python, but the server answered HTTP 403 Forbidden. The website is not meant to be read by scripts. So I found Swedavia's official developer portal and the FlightInfo API version 2. From the official documentation I learned the endpoint format, that a subscription key must be sent in a header, that all times are in UTC, and exactly which fields hold the status and the gate. A request without a key returns 401, which confirms that the endpoint exists and needs authentication."

### 1:15–2:10 Implementation *(screen: VS Code, show files one by one)*

> "Here is the project structure. `app.py` is the Flask server. It validates every input against an allow-list, adds security headers, and returns JSON.
> `swedavia_client.py` talks to the real API. It sends the key from a private `.env` file, so the key stays on the server and never reaches the browser. It handles timeouts and errors, and converts the API response into a simple format, including converting UTC times to Swedish time.
> Because I don't have an API key yet, I built a demo mode. `demo_data.py` generates example flights in exactly the same format as the real API, so demo mode actually tests the same parsing code. Demo flights are clearly labelled as not real.
> The frontend is one HTML page, a stylesheet with dark and light themes, and a JavaScript file that loads, searches and filters the flights."

### 2:10–3:20 Live demonstration *(screen: browser)*

> "Now the app itself. Note the yellow banner: this is demo mode, so these flights are generated examples, not real flights." *(point at banner)*
> "I can choose any of the ten airports. Let's take Göteborg Landvetter… and switch to arrivals. The column now says 'From', and instead of check-in desks it shows the baggage belt." *(do it)*
> "Search works instantly. If I type 'copen', only Copenhagen flights remain." *(type, then Esc)*
> "These filter buttons show how many flights have each status. Here are the delayed flights: the old time is crossed out and the new time is highlighted." *(click Delayed)*
> "If I select Live API without a key, the app doesn't crash. It explains what to do." *(click Live API, then back to Demo)*
> "There is also a light theme, and on a phone the table turns into cards." *(toggle theme; F12 device toolbar → phone size)*

### 3:20–4:05 Testing and problems *(screen: terminal running tests, then DOCUMENTATION.md table)*

> "I wrote 28 automated tests. They cover input validation, the API field mapping, time-zone conversion, every status, demo mode for all airports, and live-mode errors like a rejected key, a timeout or invalid JSON. They use a fake HTTP connection, so they run without internet or a key." *(run `python -m unittest discover -s tests -v`, show OK)*
> "Some real problems I solved: the 403 from the website; my first parser read status and gate from the wrong fields, which I found by checking against the official documentation; and on Windows the app crashed because Python had no time-zone data, which I fixed by adding the tzdata package."

### 4:05–4:35 Conclusion *(screen: GitHub repo or README)*

> "The project is on GitHub with a README and full documentation. I learned how to research and use an official API, keep secrets safe, handle errors, test code without a network, and build an accessible, responsive interface. My next step is to test live mode with my own subscription key. Thank you for watching."

---

**Honesty rules for the recording**

- Do **not** say that live mode works with real data unless you have tested it with your own key.
- Do **not** show `.env` or any key.
- If your timings run short, show the code in more detail during 1:15–2:10. You need at least 4 minutes.
