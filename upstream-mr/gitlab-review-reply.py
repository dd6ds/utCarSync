#!/usr/bin/env python3
"""Review-Runde 1 von lomiri-obex-call-data!3:
  - Antwort (REPLY-review-1.md) in Lionels Diskussion zu src/contactsservice.cpp, Diskussion auf "resolved"
  - MR-Beschreibung durch die aktuelle Fassung (MR-lomiri-obex-call-data.md) ersetzen
Token: $GITLAB_TOKEN oder Datei ~/.config/utcarsync/gitlab-token (Scope api)
  ./upstream-mr/gitlab-review-reply.py [--dry-run]
"""
import json, os, re, sys, urllib.parse, urllib.request, urllib.error

API = "https://gitlab.com/api/v4"
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = urllib.parse.quote("ubports/development/core/lomiri-obex-call-data", safe="")
MR = 3
DRY = "--dry-run" in sys.argv
TOKEN_FILE = os.path.expanduser("~/.config/utcarsync/gitlab-token")


def text(path, name=None):
    s = re.sub(r"<!--.*?-->", "", open(os.path.join(HERE, path), encoding="utf-8").read(), flags=re.S)
    if name:
        m = re.search(rf"^# {name}\n(.*?)(?=^# |\Z)", s, flags=re.S | re.M)
        s = m.group(1) if m else s
    return s.strip()


def call(method, path, token=None, data=None):
    h = {"Content-Type": "application/json"}
    if token:
        h["PRIVATE-TOKEN"] = token
    req = urllib.request.Request(API + path, method=method, headers=h,
                                 data=json.dumps(data).encode() if data is not None else None)
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")


def main():
    token = os.environ.get("GITLAB_TOKEN") or (open(TOKEN_FILE).read().strip() if os.path.exists(TOKEN_FILE) else None)
    if not token:
        sys.exit(f"kein Token: GITLAB_TOKEN setzen oder {TOKEN_FILE} anlegen")
    me = call("GET", "/user", token)["username"]
    reply = text("REPLY-review-1.md")
    desc = text("MR-lomiri-obex-call-data.md", "Description")
    title = text("MR-lomiri-obex-call-data.md", "Title")

    discs = call("GET", f"/projects/{PROJ}/merge_requests/{MR}/discussions?per_page=100", token)
    target = None
    for d in discs:
        first = d["notes"][0]
        pos = first.get("position") or {}
        if first["author"]["username"] != me and "contactsservice.cpp" in (pos.get("new_path") or "") \
                and "LOMIRI_CONTACT_BACKEND" in first["body"]:
            target = d
    if not target:
        sys.exit("Lionels Diskussion nicht gefunden")
    already = any(n["author"]["username"] == me and "good point" in n["body"] for n in target["notes"])
    print(f"angemeldet als @{me}")
    print(f"Diskussion {target['id']} von @{target['notes'][0]['author']['username']}: "
          f"{target['notes'][0]['body'][:70]!r}")
    print("Antwort:", "schon vorhanden" if already else reply.splitlines()[0])
    print("Neuer Titel:", title)
    if DRY:
        return

    if not already:
        call("POST", f"/projects/{PROJ}/merge_requests/{MR}/discussions/{target['id']}/notes", token, {"body": reply})
        print("Antwort gepostet")
    call("PUT", f"/projects/{PROJ}/merge_requests/{MR}/discussions/{target['id']}", token, {"resolved": True})
    print("Diskussion resolved")
    call("PUT", f"/projects/{PROJ}/merge_requests/{MR}", token, {"title": title, "description": desc})
    print(f"Beschreibung aktualisiert: https://gitlab.com/ubports/development/core/lomiri-obex-call-data/-/merge_requests/{MR}")


if __name__ == "__main__":
    main()
