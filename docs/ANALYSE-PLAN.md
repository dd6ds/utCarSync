# Analyse- und Arbeitsplan

## Phase 0 – Ist-Zustand (USB, 10 min)
`scripts/phone-status.sh` prüft:
- bluez/obexd-Version, ob obexd in der User-Session läuft
- ob es einen SDP-Eintrag „Phonebook Access PSE“ gibt (`sdptool browse local` bzw. D-Bus)
- ob `com.lomiri.ObexCallData` installiert und per D-Bus aktivierbar ist
- welche obexd-Plugins geladen sind (`journalctl --user -u obex` / Log)

## Phase 1 – Test ohne Auto (Laptop t490s = „Auto“)
`scripts/laptop-pbap-test.py <BT-Adresse des Telefons>` nutzt den obexd-*Client* auf dem
Laptop (org.bluez.obex.PhonebookAccess1) und macht genau das, was das MIB2 macht:
Select(int, pb) -> GetSize -> PullAll(vCard21) -> List -> Anruflisten.
Damit lassen sich Fehler schnell finden, ohne jedes Mal ins Auto zu gehen.

## Phase 2 – Bauen
- `upstream/ubports-bluez`, Branch `personal/lduboeuf/add_lomiri_phonebook`
  (enthält `--with-phonebook=lomiri` + Autostart-Patch), Paket `bluez-obexd` für arm64
- `upstream/lomiri-obex-call-data` (main) als .deb
- Bauweg: Docker `ubports/...:24.04` arm64 mit qemu bzw. clickable/crossbuilder;
  Ziel ist die UT-Basis des Testgeräts (Phase 0)
- Auf das Gerät: `adb push` + `dpkg -i` (rw) oder systemd-user-Override auf
  `/home/phablet/.local/...` (ohne rw)

## Phase 3 – Auto
btsnoop vom Telefon (`scripts/phone-btsnoop.sh`) -> Auswertung mit
`btmon -r`, Wireshark (`obex`/`bthci_acl`) und REA (`rea` kann pcap/btsnoop lesen).
Schauen auf: SDP-Abfrage 0x112F, OBEX-Connect-Antwort, Application-Parameter
(Format, Filter, MaxListCount, ListStartOffset), Fehlercodes (0xC4 Not Found,
0xD3 Service Unavailable), Abbruch nach der ersten vCard.

## Phase 4 – Fehler beheben und upstream bringen
Gezielte Patches an `lomiri-obex-call-data` (vCard-Erzeugung) bzw. obexd-Plugin,
dann als MR an UBports.

## Zu REA / SailfishOS
Das Sailfish-obexd-Plugin ist GPL und liegt offen in `upstream/sailfish-bluez5`.
Geschlossen ist nur der Jolla-Dienst `com.jolla.ObexCallData`. Den hat UBports
bereits als `lomiri-obex-call-data` neu geschrieben. Den Jolla-Dienst müssen wir
nur mit REA ansehen, falls das MIB2 mit Sailfish funktioniert, mit UT aber nicht,
und der Mitschnitt den Unterschied nicht erklärt. Dann vergleichen wir dessen
vCard-Ausgabe (Verhalten), ohne Code zu übernehmen. Das Sailfish-RPM
(`jolla-obex-calldata`/ähnlich) müsstest du dann von einem Sailfish-Gerät besorgen.
