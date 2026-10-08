# Update Documentation Logs

Update all project documentation with the work completed since the last log update.

**Paths:** `<root>` means `/Users/frankserrao/Dropbox/Customers/c2m/projects/c2m-api/C2M_API_v2`.

## 0. Establish scope first

- Find the last update: the most recent `/update-logs` entry at the end of `<root>/c2m-api-v2-postman/c2m-api-v2-postman-claude.log`.
- List every commit since then in **both** repos, so work done in earlier, unlogged sessions is not missed:
  ```bash
  git -C <root>/c2m-api-v2-postman log --since='<last update>' --format='%h %ad %s' --date=format:'%Y-%m-%d %H:%M' --reverse
  git -C <root>/c2m-api-v2-manuals log --since='<last update>' --format='%h %ad %s' --date=format:'%Y-%m-%d %H:%M' --reverse
  ```
- Combine those commits with the conversation history.
- Commits not covered by the conversation get labelled "(previously unlogged)".

## 1. System-wide CLAUDE.md — `/Users/frankserrao/.claude/CLAUDE.md`

- Add a dated entry at the top of the "Recent Work Completed" section: summary, key accomplishments, commit hashes.
- Add a fuller dated entry at the top of the "Session History" section (newest first): project, repositories, context, commit table, decisions, verification, open items.
- This file is not version-controlled. Save it on disk only.

## 2. Project CLAUDE.md files (both)

**`<root>/CLAUDE.md`** (top-level project orientation):
- Add a dated entry at the top of "Recent Updates": repositories, commits per repo, open items.
- Keep "Session Startup Guidance" pointing to the latest accomplishments file and any new key reports.
- Not version-controlled. Save it on disk only.

**`<root>/c2m-api-v2-postman/CLAUDE.md`** (pipeline repo), when pipeline work was done:
- Add a dated entry at the top of "Recent Changes".
- Update "Key Pipeline Components", "Important Patterns", "Validation Quick Reference" (targets and expected test counts) and "Known Gaps" if anything they state has changed.

## 3. Project log — `<root>/c2m-api-v2-postman/c2m-api-v2-postman-claude.log`

- Append chronological entries in the form `[YYYY-MM-DD HH:MM] - Action/Decision/Discovery`.
- Include major actions, commits (with hashes), decisions (and who made them), findings, corrections to earlier findings, and CI run IDs.
- Finish with an `[YYYY-MM-DD] - Updated documentation logs (/update-logs)` entry. The next run uses it to find its starting point.
- This file is git-ignored. Save it on disk only.

## 4. Accomplishments log — `<root>/c2m-api-v2-manuals/logs/accomplishments/ACCOMPLISHMENTS_<MON>_<YYYY>.md`

- Use the file for the month the work happened, e.g. `ACCOMPLISHMENTS_OCT_2026.md`. If the work spans months, add an entry to each month's file.
- Create the file if it doesn't exist, starting with a one-line pointer to the previous month's file.
- Each entry gets a dated heading (`## YYYY-MM-DD — Title`, or a date range) and covers:
  - a summary of the work completed;
  - key decisions and outcomes;
  - files modified/created;
  - commits per repo;
  - open items;
  - time spent (`### Time`).
- (`temp-reports/` was removed 2026-09-22; do not use it.)

## 5. Commit and push

- Manuals: commit the accomplishments file(s).
- Postman: commit `CLAUDE.md` if it changed. `.md`-only commits don't trigger CI.
- Push each repo to **both** remotes:
  - `click2mail master` and `origin master` for manuals;
  - `click2mail main` and `origin main` for postman.
- Report which files were saved on disk only (`~/.claude/CLAUDE.md`, `<root>/CLAUDE.md`, the project log) and which were committed, with hashes.
