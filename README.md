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
  phone-install.sh          installiert die CI-Pakete auf dem Telefon (+ --rollback)
patches/                  eigene Patches (gehen als MR an UBports)
.github/workflows/        arm64-Build der .deb-Pakete
```

## Status

- [x] Projekt angelegt, Upstream-Stand recherchiert
- [x] Infos von Dennis: Poco X3 Pro, SEAT Leon 2019, rw erlaubt, upstream ja
- [x] Fund: lomiri-obex-call-data liest nur qtcontacts-sqlite, auf 24.04-1.x liegen die
      Kontakte aber im address-book-service (galera) -> Patch
      `patches/lomiri-obex-call-data/0001-*.patch` (Backend-Auswahl zur Laufzeit)
- [x] CI: `.github/workflows/build.yml` baut bluez-obexd + lomiri-obex-call-data
      für arm64, je für 24.04-1.x (bluez 5.72) und 24.04-2.x (bluez 5.85)
- [ ] Ist-Zustand des Poco erfassen (`scripts/phone-status.sh`)
- [ ] Pakete installieren (`scripts/phone-install.sh <ordner>`), Rückweg: `--rollback`
- [ ] PBAP gegen den Laptop testen (ohne Auto)
- [ ] Test im Auto mit btsnoop-Mitschnitt
- [ ] Fehler beheben, Patches upstream (UBports MR)

## Ist-Zustand Poco X3 Pro (2026-11-04, `analysis/phone-status-*.txt`)
- Kanal `24.04-2.x/arm64/android9plus/stable`, bluez/obexd 5.85 -> passende Pakete: `debs/utcarsync-24.04-2.x-arm64/`
- obexd läuft (`-P ftp,irmc,mas,pcsuite`), **PBAP-Server-SDP (0x112F) ist schon da**,
  aber mit dem Backend `phonebook-ebook` (Evolution-Data-Server), nicht mit `lomiri`
- Kontakte-Backend auf dem Gerät: nur `qtcontact5-galera` (address-book-service),
  **kein qtcontacts-sqlite** -> ohne unseren Patch würde lomiri-obex-call-data ins Leere lesen
- Nächster Schritt: Ausgangsmessung mit den Original-Paketen (Laptop-Test + Mitschnitt im Leon),
  danach unsere Pakete installieren und dieselbe Messung wiederholen

## Messung 1 (2026-11-04): Laptop als PCE gegen das Poco
- **Originalpakete:** Session ok, `pb` -> `Internal Server Error`, `ich/och/mch/cch` -> `Not Found`
  (phonebook-ebook findet kein Evolution-Adressbuch) => das ist der Fehler, den auch das Auto sieht
- **unser lomiri-obex-call-data (ohne root, von Hand gestartet):** Backend-Auswahl greift
  (`available: invalid, galera, memory` -> `galera`), `Count` = 174 Kontakte, `Fetch` liefert
  gültige vCard 2.1 (`N`, `FN`, `TEL;CELL`), Anrufliste `cch` = 6
- Auffällig: galera kann nicht nach DisplayLabel sortieren -> Reihenfolge unsortiert (das Auto sortiert
  selbst, ggf. später nach QContactName sortieren)
- Nächster Schritt: bluez-obexd mit Lomiri-Plugin installieren (braucht sudo-PIN), Messung wiederholen

## Messung 2 (2026-11-04): mit unseren Paketen – Laptop als PCE
- **Erfolg:** `pb` 174 Kontakte (List + PullAll vCard 2.1 + Pull einzeln), `ich` 3, `och` 3, `mch` 0, `cch` 6
- Umlaute korrekt als `CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE` (N, FN, ADR)
- **Wichtig – Trust:** Ist das Gegenüber auf dem Telefon `Trusted: no`, hängt die PBAP-Verbindung in bluetoothd
  (Autorisierung ohne Antwort) und bluetoothd nimmt danach auf RFCOMM-Kanal 15 nichts mehr an
  (`Connection refused`), bis Bluetooth aus/an geschaltet wird. Abhilfe vorerst:
  `adb shell bluetoothctl trust <MAC>`, danach Bluetooth aus/an. Für das Auto ebenso nach dem Koppeln.
  -> eigener Fix nötig (Lomiri-Agent / bluetoothd), Upstream-Issue
- Offene Punkte fürs MIB2: keine Owner-Card `0.vcf` (Liste beginnt bei `1.vcf`), 107 `TEL` ohne Typ,
  1x `TEL;ENCODING=QUOTED-PRINTABLE`, PBAP-SDP-Version 1.1 (RFCOMM, kein L2CAP/1.2)
- Reparatur nach dem ersten Installationsversuch: siehe `scripts/phone-repair.sh` (Commit-Log)
