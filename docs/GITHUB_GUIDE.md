# Keeping the FlightScope repository on GitHub (safely)

**Current state:** the project is published at <https://github.com/nedababaki-pixel/flightscope-swedavia> as a public repository with the `main` branch. This guide explains how to check the state and how to publish future changes. It is written for the VS Code terminal (PowerShell) on Windows.

## 1. Check the state before any change

Run these in the project folder:

```powershell
# Which branch and remote are used
git status -sb
git remote -v

# The most recent commits
git log --oneline -5
```

- `git remote -v` should show `origin` pointing to `https://github.com/nedababaki-pixel/flightscope-swedavia.git`.
- `git status -sb` should show `## main...origin/main` when everything is published. If it shows `ahead` or `behind`, see section 3.
- `git status` lists changed files. Anything listed there is **not yet on GitHub**.

## 2. Secret check (before every commit)

```powershell
# 1. .env must be ignored. The output should show ".gitignore:...:.env"
git check-ignore -v .env

# 2. Search the files Git tracks for anything that looks like a real key.
#    Real keys are long strings of letters and digits, so this pattern does not
#    match the empty example line or the README text.
git grep -nE "SWEDAVIA_API_KEY=[A-Za-z0-9]{16,}"

# 3. Run the tests. One test checks that no key is saved in tracked files.
python -m unittest discover -s tests -v
```

Step 2 must print **nothing**. If it prints a line, stop. Remove the key from the file before committing (see section 5).

Never put a real key in `.env.example`, the README, screenshots, commit messages or the documentation.

## 3. Publish a change

```powershell
git add -A
git status
```

Check the `git status` list. It must **not** include `.env`, `.venv/` or `__pycache__/`. If one of them appears, run `git reset <file>` for that file and check `.gitignore` before continuing.

```powershell
git commit -m "Describe what changed in one short sentence"
git push
```

**Confirm the push worked.** Run `git status -sb`; it should show `## main...origin/main` with nothing after it. Then open the repository on GitHub and check that the new commit is at the top of the history.

If `git push` asks you to sign in, sign in through the browser window. Use your own GitHub account.

## 4. Commit identity (privacy)

Commits should use the private **noreply address** that GitHub shows under **Settings → Emails** (with "Keep my email addresses private" turned on), not your personal email.

```powershell
git config user.name
git config user.email
```

If the email shown is not the noreply address, set it inside the project folder:

```powershell
git config user.email "<your-noreply-address>"
```

Commits already in the history keep the name and email they were made with. Do not rewrite the history to change them (see section 5).

## 5. If a key was ever committed

1. **Revoke or regenerate the key first**, in the Swedavia developer portal. Once a key has been pushed, treat it as public.
2. Remove the key from the working files, then commit and push the removal.
3. **Do not rewrite the Git history** (for example with `git filter-repo`, `git rebase` or a forced push) without first discussing it with your teacher. The removed key stays visible in the old commits, so the revocation in step 1 is what makes it safe.

## 6. Make the repository look professional

- **About** (gear icon on the repository page): add the description and topics such as `python`, `flask`, `api`, `dashboard`, `swedavia`, `accessibility` and `portfolio`.
- **Pin** the repository on your GitHub profile.
- Check that the README renders with all screenshots. Images that do not appear usually have a wrong path, so check the names in `docs/screenshots/`.
- Optional: add a `LICENSE` file (MIT is common for portfolio projects). The repository does not have one yet.

## 7. Files in this repository

| Path | Purpose |
|---|---|
| `README.md` | Setup, features, integration notes and limitations |
| `DOCUMENTATION.md` | The project report (also published as `docs/FlightScope_Documentation.pdf`) |
| `docs/` | This guide, the screenshot checklist and the video script |
| `docs/screenshots/` | Screenshots used in the report and the README |
