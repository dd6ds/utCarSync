# utCarSync – Kontakte & Anrufliste per Bluetooth (PBAP) ins Auto

Ziel: Ubuntu Touch soll dem Infotainment im Auto (zuerst VW/VAG MIB2 Standard
von Technisat, `MST2_EU_SE_ZR_P0516T`, HW H50) per Bluetooth das Telefonbuch
und die Anrufliste liefern. Damit kann man im Auto die Kontakte durchsuchen,
und bei einem eingehenden Anruf erscheint der Name statt nur der Nummer.

## Ergebnis der ersten Recherche (2026-11-04)

Das Auto holt sich die Kontakte über **PBAP** (Phone Book Access Profile).
Das Telefon ist dabei der **PSE** (Server) und das Auto der **PCE** (Client).
Den Namen beim Anruf zeigt das Auto selbst an: Es vergleicht die per HFP
gemeldete Rufnummer (`+CLIP`) mit dem Telefonbuch, das es vorher über PBAP
geladen hat. Für den Namen auf dem Display ist also nur **PBAP** nötig, keine
Änderung am HFP.

Unter SailfishOS besteht das aus zwei Teilen:

| Teil | SailfishOS | Ubuntu Touch (UBports, Stand Okt. 2026) |
|---|---|---|
| obexd-Plugin (PBAP-Server in BlueZ) | `obexd/plugins/phonebook-sailfish.c` – **offen** (github.com/sailfishos/bluez5) | `phonebook-lomiri.c` = 1:1-Kopie, nur D-Bus-Namen geändert. Branch `personal/lduboeuf/add_lomiri_phonebook` in `ubports/.../packaging/bluez`, Draft-MR !8 |
| D-Bus-Dienst, der Kontakte + Anrufliste als vCard liefert | `com.jolla.ObexCallData` – **geschlossen** (das „fehlende Stück“) | `lomiri-obex-call-data` (`com.lomiri.ObexCallData`, Qt/QtContacts + History-Service). Branch `main` hat eine erste Version, `ubports/24.04-2.x` ist noch leer |

**Folgerung:** Ein Reverse Engineering des Sailfish-Binaries mit REA ist
**nicht mehr nötig**. Die Schnittstelle (`Count`/`Fetch`/`FetchById` mit
`a(ssss)`) ist durch das offene Plugin vollständig festgelegt, und UBports
hat den Dienst bereits nachgebaut. Unsere Arbeit besteht deshalb aus
**Integration, Test am echten MIB2 und dem Beheben der Fehler, die dabei
auftreten** (vCard-Format, Rufnummernformat, SDP-Eintrag, obexd-Autostart,
AppArmor). Gefundene Fehler gehen als Patches an UBports zurück.

REA bleibt als Werkzeug für die **Mitschnitt-Analyse** im Projekt
(`rea` kann pcap/btsnoop auswerten), siehe `docs/ANALYSE-PLAN.md`.

## Verzeichnisse

```
upstream/                 Referenz-Quellen (git clones)
  sailfish-bluez5/          SailfishOS BlueZ inkl. phonebook-sailfish.c
  ubports-bluez/            UBports bluez packaging (Branch mit Lomiri-Plugin)
  lomiri-obex-call-data/    UBports D-Bus-Dienst für Kontakte/Anrufliste
  lomiri-phonebook.patch    der obexd-Patch aus dem UBports-Branch
analysis/                 extrahierte Dateien, Mitschnitte, Notizen
docs/
  ARCHITEKTUR.md            Ablauf Auto <-> Telefon, Komponenten
  INFOS-VON-DENNIS.md       was ich von dir brauche
  ANALYSE-PLAN.md           Vorgehen: Mitschnitte, Tests, Build, Upstream
  VAG-MIB2-NOTIZEN.md       bekannte Eigenheiten des MIB2 Standard
scripts/
  phone-status.sh           prüft per adb: BlueZ/obexd/PBAP-SDP/D-Bus-Dienst
  phone-btsnoop.sh          startet btmon auf dem Telefon, holt .btsnoop
  laptop-pbap-test.py       Laptop spielt "Auto" (PCE) und lädt das Telefonbuch
```

## Status

- [x] Projekt angelegt, Upstream-Stand recherchiert
- [ ] Infos von Dennis (siehe `docs/INFOS-VON-DENNIS.md`)
- [ ] Ist-Zustand des Telefons erfassen (`scripts/phone-status.sh`)
- [ ] PBAP gegen den Laptop testen (ohne Auto)
- [ ] bluez-obexd mit Patch und lomiri-obex-call-data für arm64 / 24.04-2 bauen
- [ ] Test im Auto mit btsnoop-Mitschnitt
- [ ] Fehler beheben, Patches upstream (UBports MR)
