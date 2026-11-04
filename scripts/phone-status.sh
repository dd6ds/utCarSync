#!/usr/bin/env bash
# Ist-Zustand PBAP auf dem Ubuntu-Touch-Telefon (per adb, read-only)
# Ausgabe zusätzlich nach analysis/phone-status-<datum>.txt
set -u
OUT="$(dirname "$0")/../analysis/phone-status-$(date +%Y%m%d-%H%M%S).txt"
adb get-state >/dev/null 2>&1 || { echo "kein adb-Gerät gefunden"; exit 1; }

adb shell 'bash -s' <<'EOF' | tee "$OUT"
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
sec(){ echo; echo "===== $* ====="; }
sec System;        cat /etc/os-release | grep -E 'PRETTY|VERSION_ID'; uname -a
                   cat /etc/system-image/channel.ini 2>/dev/null; system-image-cli -i 2>/dev/null | head -8
sec Pakete;        dpkg -l | grep -Ei 'bluez|obex|ofono|address-book|history-service|qtcontacts' | awk '{print $2, $3}'
sec obexd-Binary;  for b in /usr/libexec/bluetooth/obexd /usr/lib/bluetooth/obexd; do [ -x $b ] && { echo $b; strings $b | grep -Ei 'phonebook|ObexCallData|pbap' | sort -u | head -20; }; done
sec Prozesse;      ps -eo pid,user,args | grep -Ei 'bluetoothd|obexd|obex-call|ofono' | grep -v grep
sec "systemd --user obex"; systemctl --user status obex 2>&1 | head -15
sec Adapter-UUIDs; bluetoothctl show 2>/dev/null | grep -Ei 'UUID|Name|Powered|Discoverable'
sec "PBAP-SDP (0x112f)"; bluetoothctl show 2>/dev/null | grep -i '112f' || echo "KEIN Phonebook-Access-Server-Eintrag"
sec "Gekoppelte Geräte"; bluetoothctl devices Paired 2>/dev/null || bluetoothctl paired-devices
sec "D-Bus Session obex"; busctl --user list 2>/dev/null | grep -Ei 'obex|calldata'
sec "D-Bus Service-Dateien"; ls /usr/share/dbus-1/services/ | grep -Ei 'obex|calldata'
sec "ObexCallData Test"; gdbus call --session --dest com.lomiri.ObexCallData --object-path /contacts --method com.lomiri.Contacts.Count 2>&1 | head -3
sec "obexd-Log (user journal)"; journalctl --user -b --no-pager 2>/dev/null | grep -Ei 'obex|pbap|phonebook' | tail -30
sec "bluetoothd-Log"; journalctl -b -u bluetooth --no-pager 2>/dev/null | tail -30 || echo "(braucht root)"
sec "AppArmor-Denials"; dmesg 2>/dev/null | grep -i 'apparmor="DENIED"' | grep -Ei 'obex|blue' | tail -10 || true
EOF
echo; echo "gespeichert: $OUT"
