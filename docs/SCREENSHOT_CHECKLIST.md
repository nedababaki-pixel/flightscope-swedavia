# Evidence and submission checklist

Status on 26 October 2026. All screenshots are in `docs/screenshots/`.

**Source column:**
- **Me:** screenshot I took myself during development and manual testing.
- **AI:** captured by the AI assistant in its built-in browser, from the running application, public Swedavia pages or my public GitHub repository. Nothing was edited or made up.

## 1. Assignment requirements

| Requirement | Where | Status |
|---|---|---|
| Research | DOCUMENTATION.md §2, Figures 1–3 | ✅ Done |
| Implementation | DOCUMENTATION.md §3, Figures 4–7, source code | ✅ Done |
| Completion and testing | DOCUMENTATION.md §4, Figures 8–16, 28 automated tests | ✅ Done |
| Problems and solutions | DOCUMENTATION.md §5 | ✅ Done |
| Conclusion | DOCUMENTATION.md §6 | ✅ Done |
| Published on GitHub | <https://github.com/nedababaki-pixel/flightscope-swedavia>, Figures 17–18 | ✅ Done |
| Video, at least 4 minutes, in English | `docs/VIDEO_SCRIPT.md` (storyboard and narration) | ❌ Still to record |
| Everything in English | All documents | ✅ Done |
| Honest about Live API | README, DOCUMENTATION.md §4.1, §4.2, video script | ✅ Clearly says it is not tested with a real key |

## 2. Screenshots

| ✓ | File | Shows | Source | Used in |
|---|---|---|---|---|
| ✅ | `00a-project-start.png` | Empty `app.py` at the start of the project | Me | Figure 4 |
| ✅ | `00b-python-working.png` | First Python test: "Python is working successfully." | Me | Figure 4 |
| ✅ | `00c-install-requests.png` | Installing the `requests` library | Me | Figure 5 |
| ✅ | `01-api-docs.jpg` | Swedavia developer portal, FlightInfo v2.0 documentation link | AI | Figure 2, Video scene 2 |
| ✅ | `02-website-403.png` | Python request to www.swedavia.se returns 403 | Me | Figure 1, Video scene 2 |
| ✅ | `03-api-401.jpg` | FlightInfo API without a key returns 401 | AI | Figure 3, Video scene 2 |
| ✅ | `05-code-client.jpg` | `normalize_flight` code and project file list (GitHub view) | AI | Figure 6 |
| ✅ | `06-server-running.png` | `run.bat` running the server | Me | Figure 7, Video scene 3 |
| ✅ | `07-dashboard-dark.png` | Dashboard, dark mode | Me | Figure 9, README, Video scene 1 |
| ✅ | `08-arrivals.png` | Luleå arrivals with baggage belt, codeshares and a cancellation | Me | Figure 11 |
| ✅ | `09-search-sk123.png` | Manual test: search SK123 → 1 result | Me | Figure 12, README |
| ✅ | `10-status-and-delays.png` | Statuses, crossed-out times, "Delayed 20 min" | Me | Figure 13, README |
| ✅ | `11-live-no-key.jpg` | Live API without a key → friendly error message | AI | Figure 14 |
| ✅ | `13-github-repo.jpg` | Public GitHub repository | AI | Figure 17, Video scene 7 |
| ✅ | `14-dashboard-light.png` | Dashboard, light theme | Me | Figure 10 |
| ✅ | `15-mobile.jpg` | Phone layout (375 px), table as cards | AI | Figure 15, README |
| ✅ | `16-invalid-input.jpg` | `airport=XXX` → JSON error "Unknown airport" | AI | Figure 16 |
| ✅ | `17-gitignore.jpg` | `.gitignore` excludes `.env`, `.venv` and temporary files | AI | Figure 18 |
| ✅ | `12-tests-ok.png` | Terminal showing `Ran 28 tests … OK (skipped=1)` | Me | Figure 8, Video scene 6 |

### Not used on purpose

- The phone photo of the Claude/GitHub screen. It is blurry and rotated, and it shows the AI chat. `13-github-repo.jpg` shows the same thing more clearly.
- No screenshot of a real API key, the `.env` file or GitHub email settings.
- No "live data" screenshot, because Live mode has not been tested with a real key.

### Privacy check of the screenshots

- No API keys, passwords or email addresses are visible.
- The terminal screenshots show the Windows user folder `C:\Users\nedab`. That is a username, not sensitive information.
- The browser screenshots show the bookmarks bar (Gmail, YouTube, Maps) and a profile initial, but no account details.
