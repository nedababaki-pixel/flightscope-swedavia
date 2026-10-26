# Evidence and submission checklist

Status on 26 October 2026. All screenshots are in `docs/screenshots/`.

**Source column:**
- **Me:** screenshot I took myself during development and manual testing.
- **AI:** captured by the AI assistant in its built-in browser, from the running application, public Swedavia pages or my public GitHub repository. Nothing was edited or made up.

## 1. Assignment requirements

Figure numbers refer to `DOCUMENTATION.md` and `docs/FlightScope_Documentation.pdf`.

| Teacher requirement | Where | Status |
|---|---|---|
| All documentation and video in English | All files, video | ✅ Fully met |
| Phase 1 Research: information gathering, tools, planning | DOCUMENTATION.md Phase 1, Figures 1–6 | ✅ Fully met |
| Phase 1 problems and solutions | Phase 1, section 1.5 | ✅ Fully met |
| Phase 2 Implementation: how it started, structure, what came first, how features developed | Phase 2, Figures 7–9 | ✅ Fully met |
| Phase 2 problems and solutions | Phase 2, section 2.5 | ✅ Fully met |
| Phase 3 Completion: finishing, testing the whole solution, improvements, publishing/presentation | Phase 3, Figures 10–19 | ✅ Fully met |
| Phase 3 problems and solutions | Phase 3, section 3.6 | ✅ Fully met |
| Phase 4 summary of all major problems | Phase 4 table | ✅ Fully met |
| Conclusion: achieved, learned, what could be improved | Conclusion | ✅ Fully met |
| Reverse Engineer steps 1–6 (look, ask, inputs, process, sketch, build) | Phase 1, section 1.1 | ✅ Fully met |
| Video at least 4 minutes | Video 4:29 | ✅ Fully met |
| Video: purpose, the three phases, problems and solutions, examples | Video | ⚠️ Partially met (reverse engineering and the sample are not mentioned; problems are only partly covered) |
| Video: clear sound, readable screen | Video | ✅ Mostly met (a few small, low-resolution browser captures) |
| Video: "Use screen recording to show your work" | Video | ⚠️ Partially met (slideshow of real screenshots, no live screen recording) |
| GitHub: repository created, git init/add/commit/remote/push | GitHub repository | ✅ Fully met |
| GitHub: latest changes pushed | GitHub repository | ⚠️ The new documentation and PDF are committed locally, waiting for your approval to push |

## 2. Screenshots

| ✓ | File | Shows | Source | Used in |
|---|---|---|---|---|
| ✅ | `00a-project-start.png` | Empty `app.py` at the start of the project | Me | Figure 1 |
| ✅ | `00b-python-working.png` | First Python test: "Python is working successfully." | Me | Figure 2 |
| ✅ | `00c-install-requests.png` | Installing the `requests` library | Me | Figure 3 |
| ✅ | `01-api-docs.jpg` | Swedavia developer portal, FlightInfo v2.0 documentation link | AI | Figure 5, Video scene 2 |
| ✅ | `02-website-403.png` | Python request to www.swedavia.se returns 403 | Me | Figure 4, Video scene 2 |
| ✅ | `03-api-401.jpg` | FlightInfo API without a key returns 401 | AI | Figure 6, Video scene 2 |
| ✅ | `05-code-client.jpg` | `normalize_flight` code and project file list (GitHub view) | AI | Figure 7 |
| ✅ | `06-server-running.png` | `run.bat` running the server | Me | Figure 8, Video scene 3 |
| ✅ | `07-dashboard-dark.png` | Dashboard, dark mode | Me | Figure 9, README, Video scene 1 |
| ✅ | `08-arrivals.png` | Luleå arrivals with baggage belt, codeshares and a cancellation | Me | Figure 11 |
| ✅ | `09-search-sk123.png` | Manual test: search SK123 → 1 result | Me | Figure 12, README |
| ✅ | `10-status-and-delays.png` | Statuses, crossed-out times, "Delayed 20 min" | Me | Figure 13, README |
| ✅ | `11-live-no-key.jpg` | Live API without a key → friendly error message | AI | Figure 15 |
| ✅ | `13-github-repo.jpg` | Public GitHub repository | AI | Figure 18, Video scene 7 |
| ✅ | `14-dashboard-light.png` | Dashboard, light theme | Me | Figure 14 |
| ✅ | `15-mobile.jpg` | Phone layout (375 px), table as cards | AI | Figure 16, README |
| ✅ | `16-invalid-input.jpg` | `airport=XXX` → JSON error "Unknown airport" | AI | Figure 17 |
| ✅ | `17-gitignore.jpg` | `.gitignore` excludes `.env`, `.venv` and temporary files | AI | Figure 19 |
| ✅ | `12-tests-ok.png` | Terminal showing `Ran 28 tests … OK (skipped=1)` | Me | Figure 10, Video scene 6 |

### Not used on purpose

- The phone photo of the Claude/GitHub screen. It is blurry and rotated, and it shows the AI chat. `13-github-repo.jpg` shows the same thing more clearly.
- No screenshot of a real API key, the `.env` file or GitHub email settings.
- No "live data" screenshot, because Live mode has not been tested with a real key.

### Privacy check of the screenshots

- No API keys, passwords or email addresses are visible.
- The terminal screenshots show the Windows user folder `C:\Users\nedab`. That is a username, not sensitive information.
- The browser screenshots show the bookmarks bar (Gmail, YouTube, Maps) and a profile initial, but no account details.
