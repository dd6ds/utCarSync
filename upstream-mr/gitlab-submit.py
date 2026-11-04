#!/usr/bin/env python3
"""Erledigt die restlichen GitLab-Schritte per API:
  1. MR lomiri-obex-call-data!3: Beschreibung ersetzen + "Allow commits from members" an
  2. Issue bei packaging/bluez anlegen (Hänger bei nicht vertrauenswürdigem Gerät)
  3. Testbericht als Kommentar an bluez MR !8 (mit Link auf das Issue)

Token: gitlab.com -> Edit profile -> Access tokens -> Add new token, Scope "api".
  GITLAB_TOKEN=glpat-... ./upstream-mr/gitlab-submit.py        (sonst wird gefragt)
  ./upstream-mr/gitlab-submit.py --dry-run                      nur anzeigen
Der Token wird nirgends gespeichert.
"""
import getpass, json, os, re, sys, urllib.parse, urllib.request, urllib.error

API = "https://gitlab.com/api/v4"
HERE = os.path.dirname(os.path.abspath(__file__))
LOCD = "ubports/development/core/lomiri-obex-call-data"
BLUEZ = "ubports/development/core/packaging/bluez"
MR_LOCD, MR_BLUEZ = 3, 8
DRY = "--dry-run" in sys.argv


def section(path, name):
    """Text unter '# <name>' bis zur nächsten '# '-Überschrift, ohne HTML-Kommentare."""
    s = re.sub(r"<!--.*?-->", "", open(os.path.join(HERE, path), encoding="utf-8").read(), flags=re.S)
    m = re.search(rf"^# {name}\n(.*?)(?=^# |\Z)", s, flags=re.S | re.M)
    if m:
        return m.group(1).strip()
    return s.strip()


def call(method, path, token, data=None):
    url = f"{API}{path}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method,
                                 headers={"PRIVATE-TOKEN": token, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> HTTP {e.code}: {e.read().decode(errors='replace')[:400]}")


def pid(p):
    return urllib.parse.quote(p, safe="")


def main():
    mr_desc = section("MR-lomiri-obex-call-data.md", "Description")
    issue_title = section("ISSUE-pbap-untrusted-device.md", "Title")
    issue_body = section("ISSUE-pbap-untrusted-device.md", "Description")
    comment = section("COMMENT-bluez-MR8.md", "")

    print("=" * 70)
    print(f"1) {LOCD}!{MR_LOCD}: Beschreibung ersetzen ({len(mr_desc)} Zeichen), allow_collaboration=true")
    print("   Anfang:", mr_desc.splitlines()[0])
    print(f"2) Issue in {BLUEZ}:\n   Titel: {issue_title}")
    print(f"3) Kommentar an {BLUEZ}!{MR_BLUEZ} ({len(comment)} Zeichen), <ISSUE-LINK> wird ersetzt")
    print("=" * 70)
    if DRY:
        print("\n--- Kommentar ---\n" + comment)
        return

    token = os.environ.get("GITLAB_TOKEN") or getpass.getpass("GitLab-Token (Scope api): ")
    me = call("GET", "/user", token)
    print(f"angemeldet als @{me['username']}")
    if input("Abschicken? [j/N] ").strip().lower() not in ("j", "ja", "y", "yes"):
        sys.exit("abgebrochen")

    # 1) MR-Beschreibung
    mr = call("PUT", f"/projects/{pid(LOCD)}/merge_requests/{MR_LOCD}", token,
              {"description": mr_desc, "allow_collaboration": True})
    print("1) ok:", mr["web_url"])

    # 2) Issue (nicht doppelt anlegen)
    existing = call("GET", f"/projects/{pid(BLUEZ)}/issues?author_username={me['username']}"
                           f"&search={urllib.parse.quote(issue_title[:60])}", token)
    if existing:
        issue = existing[0]
        print("2) Issue existiert schon:", issue["web_url"])
    else:
        issue = call("POST", f"/projects/{pid(BLUEZ)}/issues", token,
                     {"title": issue_title, "description": issue_body})
        print("2) ok:", issue["web_url"])

    # 3) Kommentar
    body = comment.replace("<ISSUE-LINK>", issue["web_url"])
    notes = call("GET", f"/projects/{pid(BLUEZ)}/merge_requests/{MR_BLUEZ}/notes?per_page=100", token)
    if any(n["author"]["username"] == me["username"] and "Test report" in n["body"] for n in notes):
        print("3) Kommentar steht schon da, übersprungen")
    else:
        call("POST", f"/projects/{pid(BLUEZ)}/merge_requests/{MR_BLUEZ}/notes", token, {"body": body})
        print(f"3) ok: https://gitlab.com/{BLUEZ}/-/merge_requests/{MR_BLUEZ}")


if __name__ == "__main__":
    main()
