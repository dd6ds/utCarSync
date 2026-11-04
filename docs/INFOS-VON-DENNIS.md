# Was ich von dir brauche

## Antworten (2026-11-04)
- Testgerät: Xiaomi Poco X3 Pro (vayu)
- Root-Dateisystem beschreibbar machen: ja
- Auto: SEAT Leon, Baujahr 2019, MIB2 Standard (Technisat)
- Android-Referenzgerät: keins vorhanden -> Referenz ist der Laptop-Test (`laptop-pbap-test.py`)
- Upstream zu UBports + GitHub-Repo dd6ds/utCarSync: ja

Noch offen: UT-Version auf dem Poco (liest `phone-status.sh` aus), Fotos vom Telefonmenü im Leon, Mitschnitt im Auto.

## 1. Telefon (vor dem ersten Test)
- [ ] Welches Gerät ist das Testgerät? (Poco X3 Pro, Redmi Note 8 Pro, S22/S23, ...)
- [ ] UT-Version und Kanal: Einstellungen > Info (z. B. 24.04-1.2 stable / 24.04-2 devel)
- [ ] Per USB verbinden, Entwicklermodus an, `adb devices` zeigt das Gerät
- [ ] Darf ich das Root-Dateisystem beschreibbar machen? (für Tests mit eigenem
      obexd/Dienst nötig; eine Overlay-Variante ohne rw ist auch möglich)
- [ ] Wie viele Kontakte ungefähr, und gibt es welche mit Umlauten, mehreren Nummern
      und Fotos? (Ich lege sonst Testkontakte an)

## 2. Auto
- [ ] Fahrzeug, Modell und Baujahr (z. B. Golf 7 2019). MIB2 Standard = Technisat `MST2_*`
- [ ] Zeigt das Auto beim Koppeln eine Option „Kontakte/Telefonbuch übertragen“
      oder „Profile“ mit „Telefonbuch“, „Nachrichten“ oder „Audio“? Bitte ein Foto davon
- [ ] Ein Foto vom Telefonmenü nach dem Koppeln (zeigt das Auto „Kontakte werden geladen“
      oder eine Fehlermeldung?)
- [ ] Wenn vorhanden, kurz ein Android- oder iPhone-Gerät koppeln, bei dem es funktioniert:
      Daran sehen wir im Mitschnitt, was das MIB2 genau anfragt (Referenz-Mitschnitt)

## 3. Mitschnitte (das Wichtigste)
Ablauf im Auto (Zündung an, Laptop nicht nötig, nur das Telefon):
1. `scripts/phone-btsnoop.sh start` (vorher per USB, dann Kabel ab, oder Kabel dran lassen)
2. Im Auto: Telefon entkoppeln, neu koppeln, ~2 min warten
3. Dich vom Zweithandy anrufen lassen (prüft die Namensanzeige)
4. `scripts/phone-btsnoop.sh stop` holt `analysis/captures/*.btsnoop`

Optional: ein Android-Mitschnitt (Entwickleroptionen > „Bluetooth HCI-Snoop-Log“)
mit demselben Auto als Referenz.

## 4. Entscheidungen
- [ ] Ziel nur „läuft bei mir“ oder upstream bei UBports (MR !8 + lomiri-obex-call-data)?
      Ich empfehle upstream; dafür sind gitlab.com-Account und MRs nötig
- [ ] GitHub-Repo `dd6ds/utCarSync` anlegen? (Commits mit dd6ds@eclipso.de)
