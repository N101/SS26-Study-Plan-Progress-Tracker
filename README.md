# SS26 Study-Plan Progress Tracker

Read-only public viewer of Noah's SS26 exam-season study progress, published to GitHub Pages:
**https://n101.github.io/SS26-Study-Plan-Progress-Tracker/**

## How it works

The public `index.html` is **generated**, never hand-edited. It's a stripped, read-only
snapshot of the private `tracker.html` app with the current tick state baked in.

```
tracker.html   (private working app — daily tracking in Firefox)
      │
      ▼  make_viewer.py   (bakes tick state, disables editing, stamps "updated …")
      │
   index.html      (public — committed & pushed)
```

- **Tracked (public):** `index.html`, `make_viewer.py`, `.gitignore`, `README.md`
- **Gitignored (private):** `tracker.html`, `tracker-versions/`, `backups/`

## Refreshing the published view

```bash
cd ~/Documents/Projects/Uni_ExamTracker

# 1. (in the tracker) hit "Export backup" — lands in ~/Downloads or backups/
# 2. regenerate: auto-picks the newest ss26-tracker-backup-*.json from backups/ or ~/Downloads
python3 make_viewer.py                 # or: python3 make_viewer.py path/to/backup.json

# 3. sanity-check the scripts parse
node --check <(python3 -c "import re,sys; sys.stdout.write('\n'.join(re.findall(r'<script>(.*?)</script>', open('index.html').read(), re.S)))")

# 4. commit & push — Pages redeploys in ~1 min
git add index.html && git commit -m "refresh progress" && git push
```

`make_viewer.py --help` documents its inputs. If it exits with
`v5 changed, generator needs updating — missing: …`, a design change to `tracker.html`
broke a replacement string — update that `sub(...)` call in the script to match, then re-run.

The viewer is a **snapshot** — each refresh re-bakes the current state; it is not live-synced.
