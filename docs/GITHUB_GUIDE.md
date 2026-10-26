# Publishing FlightScope to GitHub (safely)

This guide uses the VS Code terminal (PowerShell) on Windows. **Do these steps yourself when you are ready to publish.** Nothing has been pushed yet.

## 1. Before you publish: secret check

Run these in the project folder:

```powershell
# 1. Confirm .env is ignored (the output should show ".gitignore:1:.env")
git check-ignore -v .env

# 2. Search for anything that looks like a key outside .env (should show only the empty example line)
Select-String -Path *.py,*.md,*.js,*.html,*.txt,.env.example -Pattern "SWEDAVIA_API_KEY="

# 3. Run the tests, including the "key not in files" test
python -m unittest discover -s tests -v
```

Never put a real key in `.env.example`, the README, screenshots or commit messages.

## 2. One-time Git setup

Install Git from <https://git-scm.com/download/win> if `git --version` does not work. Then:

```powershell
git config --global user.name "Your Name"
```

For the commit email, use the private **noreply address** that GitHub shows under **Settings → Emails** (with "Keep my email addresses private" turned on), not your personal e-mail. Copy it from that page and set it with `git config user.email` inside the project folder.

## 3. Create the local repository

```powershell
git init
git branch -M main
git add .
git status
```

**Check the `git status` list carefully.** It must **not** include `.env`, `.venv/` or `__pycache__/`. If `.env` appears, stop and fix `.gitignore` before continuing.

```powershell
git commit -m "FlightScope: Swedavia flight information dashboard"
```

## 4. Create the GitHub repository

1. Go to <https://github.com/new>.
2. Repository name: `flightscope-swedavia` (or similar).
3. Description: *Responsive flight information dashboard for Swedish airports. Python, Flask & Swedavia FlightInfo API v2.*
4. Choose **Public** if it is for your portfolio. Do **not** add a README, .gitignore or licence, because the project already has them.
5. Click **Create repository**.

## 5. Push

```powershell
git remote add origin https://github.com/<your-username>/flightscope-swedavia.git
git push -u origin main
```

Sign in through the browser window if Git asks.

## 6. Make the repository look professional

- **About** (gear icon on the repo page): add the description, plus topics such as `python`, `flask`, `api`, `dashboard`, `swedavia`, `accessibility` and `portfolio`.
- **Screenshots:** save the images from the screenshot checklist in `docs/screenshots/`, then remove the `<!-- -->` comment around the image lines in `README.md`. Commit and push again:

  ```powershell
  git add docs/screenshots README.md
  git commit -m "Add screenshots"
  git push
  ```

- **Pin** the repository on your GitHub profile.
- Optional: add a `LICENSE` file (MIT is common for portfolio projects).

## 7. If you ever commit a key by mistake

1. **Revoke or regenerate the key immediately** in the Swedavia developer portal. This is the only real fix, because the old key must be treated as public.
2. Remove the key from the files, commit and push.
3. Deleting the file in a new commit does **not** remove it from history. For a small school repository, the simplest clean option is to delete the GitHub repository and push a fresh one, made from a folder where `.env` was never committed.
