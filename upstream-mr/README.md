# Upstream-Beiträge an UBports (GitLab)

UBports arbeitet auf gitlab.com mit Merge Requests (MR), nicht auf GitHub.

| Was | Wohin | Datei |
|---|---|---|
| **MR** Backend-Fallback (2 Commits) | `ubports/development/core/lomiri-obex-call-data` -> `main` | `MR-lomiri-obex-call-data.md`, Patches in `../patches/lomiri-obex-call-data/` |
| **Kommentar** Testbericht + Bitte um 24.04-2.x | bluez packaging MR !8 | `COMMENT-bluez-MR8.md` |
| **Issue** Hänger bei nicht vertrauenswürdigem Gerät | `ubports/development/core/packaging/bluez` Issues | `ISSUE-pbap-untrusted-device.md` |

## Ablauf

1. GitLab-Konto (falls nicht vorhanden) und SSH-Key hinterlegen:
   gitlab.com -> Preferences -> SSH Keys -> Inhalt von `~/.ssh/id_ed25519.pub`.
   Test: `ssh -T git@gitlab.com` sollte "Welcome to GitLab" melden.
   In den GitLab-Einstellungen als Commit-E-Mail `dd6ds@eclipso.de` eintragen
   (Preferences -> Emails), sonst werden die Commits keinem Konto zugeordnet.
2. https://gitlab.com/ubports/development/core/lomiri-obex-call-data -> **Fork**
3. `./upstream-mr/push-to-fork.sh <gitlab-name>` pusht den Branch
   `personal/dd6ds/contacts-backend-fallback` und gibt den Link zum Anlegen des MR aus
4. Titel und Beschreibung aus `MR-lomiri-obex-call-data.md` einfügen.
   Option "Allow commits from members who can merge" anhaken
5. Das Issue anlegen und den Link im Kommentar eintragen. Dann den Kommentar bei bluez MR !8 posten,
   dort `<NUMMER EINTRAGEN>` durch die MR-Nummer aus Schritt 4 ersetzen
6. Optional im Forum-Thread (topic 10556) auf MR und Testbericht verlinken

Die Commits tragen `dd6ds <dd6ds@eclipso.de>` und einen `Co-Authored-By: Claude`-Trailer.
Wer das nicht möchte, entfernt ihn vor dem Push:
`git -C upstream/lomiri-obex-call-data rebase -i origin/main` (Commit-Message bearbeiten).
