#!/usr/bin/env python3
"""Regenerate the read-only GitHub Pages viewer (index.html) from the v5 tracker.

Usage:
    python3 make_viewer.py                 # use the newest ss26-tracker-backup-*.json in ~/Downloads
    python3 make_viewer.py <backup>.json   # use a specific "Export backup" file

Falls back to the done-map baked into the current index.html if no backup exists.
The backup file's "tasks" key (or a bare done-map JSON) supplies the ticks.
After running: git add index.html && git commit && git push.
"""
import json, re, sys, pathlib
from datetime import datetime

SRC = pathlib.Path(__file__).parent/"tracker-v5.html"
OUT = pathlib.Path(__file__).parent/"index.html"

def load_done(path):
    raw = json.load(open(path))
    done = raw.get("tasks", raw)  # accept a backup-export file or a bare done-map
    if not all(re.fullmatch(r"\d{4}-\d{2}-\d{2}\|\d+\|\d+", k) for k in done):
        sys.exit(f"{path} doesn't look like a tracker done-map (unexpected keys)")
    return done

if len(sys.argv) > 1:
    done, source = load_done(sys.argv[1]), sys.argv[1]
else:
    # newest backup across both the repo's backups/ and ~/Downloads (wherever the export landed)
    search = [pathlib.Path(__file__).parent/"backups", pathlib.Path.home()/"Downloads"]
    backups = sorted((f for d in search for f in d.glob("ss26-tracker-backup-*.json")),
                     key=lambda p: p.stat().st_mtime)
    if backups:
        done, source = load_done(backups[-1]), str(backups[-1])
    else:
        m = re.search(r"let done=(\{.*?\});", OUT.read_text())
        if not m: sys.exit("no backup given, none in backups/ or ~/Downloads, none baked in index.html")
        done, source = json.loads(m.group(1)), "existing index.html (no backup found)"
print("ticks from:", source)

s = SRC.read_text()
stamp = datetime.now().strftime("%-d %b, %H:%M")

def sub(old, new):
    global s
    assert old in s, "v5 changed, generator needs updating — missing: " + old[:60]
    s = s.replace(old, new)

sub('let done=JSON.parse(localStorage.getItem(LS_TASKS)||"{}");', "let done=" + json.dumps(done) + ";")
sub('let nogo=JSON.parse(localStorage.getItem(LS_NOGO)||"[]");', "let nogo=[];")
sub('let ui=JSON.parse(localStorage.getItem(LS_UI)||"{}");', "let ui={};")
sub('const save=()=>localStorage.setItem(LS_TASKS,JSON.stringify(done));', "const save=()=>{};")
sub('const saveNogo=()=>localStorage.setItem(LS_NOGO,JSON.stringify(nogo));', "const saveNogo=()=>{};")
sub('const saveUI=()=>localStorage.setItem(LS_UI,JSON.stringify(ui));', "const saveUI=()=>{};")
sub('function toggleTask(id){', "function toggleTask(id){return;")
sub("</style>", """
  /* --- read-only viewer --- */
  .task .cb,.ccb{pointer-events:none}
  .blk:has(#nogoList){display:none}
  #exportBtn,#importBtn,#collapsePast,#expandAll{display:none}
  .checkin{display:none}
</style>""")
# viewer opens at the top (stats + overall progress); the private tracker keeps its autoscroll-to-today
sub('window.addEventListener("load",()=>{const el=document.getElementById("day-"+TODAY);if(el)setTimeout(()=>el.scrollIntoView({behavior:"smooth",block:"center"}),500);});',
    "/* viewer: no autoscroll-to-today — open at the top */")
sub('<div class="kicker">Expedition · Jul 6 to Aug 7</div>',
    f"<div class=\"kicker\">Noah's expedition · Jul 6 to Aug 7 · updated {stamp}</div>")
sub("<title>", "<title>Noah — ")

OUT.write_text(s)
n = sum(1 for v in done.values() if v)
print(f"wrote {OUT} — {n} tasks done, stamped 'updated {stamp}'")
