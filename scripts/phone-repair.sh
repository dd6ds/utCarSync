#!/usr/bin/env bash
# Reparatur nach dem fehlgeschlagenen ersten phone-install.sh (2026-11-04):
# installiert libqt5contact5-plugin-sqlite + unsere Pakete + die entfernten
# Metapakete ubuntu-touch / ubuntu-touch-android9plus wieder.
# Entfernt NIE etwas (--no-remove + Probelauf mit Abbruch bei "Remv").
#   phone-repair.sh            mit unseren Paketen
#   phone-repair.sh --original nur Originalpakete aus dem UBports-Repo
# Telefon braucht Internet (WLAN) für apt-get update.
set -eu
[ -n "${UT_PW:-}" ] || { read -rsp "UT-Passwort/PIN: " UT_PW; echo; }
adb get-state >/dev/null
D=/home/phablet/utcarsync
if [ "${1:-}" = "--original" ]; then
  PKGS="bluez-obexd ubuntu-touch ubuntu-touch-android9plus"
else
  PKGS="libqt5contact5-plugin-sqlite $D/bluez-obexd_5.85-4ubports1+utcarsync1_arm64.deb $D/lomiri-obex-call-data_1.0.0+utcarsync1_arm64.deb ubuntu-touch ubuntu-touch-android9plus"
fi

adb shell "UT_PW='$UT_PW' PKGS='$PKGS' bash -s" <<'EOF'
set -e
S() { printf '%s\n' "$UT_PW" | sudo -S -p '' "$@"; }
S true || { echo "sudo-Passwort falsch"; exit 1; }
S mount -o remount,rw /
echo "== apt-get update"; S apt-get update -qq
echo "== Probelauf"
SIM=$(S apt-get install -s --no-remove $PKGS 2>&1) || { echo "$SIM" | tail -20; echo "ABBRUCH: Probelauf fehlgeschlagen"; exit 1; }
echo "$SIM" | grep -E '^(Inst|Remv|Conf)' || true
if echo "$SIM" | grep -q '^Remv'; then echo "ABBRUCH: apt will Pakete entfernen"; exit 1; fi
echo "== Installation"; S apt-get install -y --no-remove $PKGS
S sync
echo "== Ergebnis"; dpkg-query -W bluez-obexd lomiri-obex-call-data libqt5contact5-plugin-sqlite ubuntu-touch ubuntu-touch-android9plus 2>&1
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
systemctl --user daemon-reload
systemctl --user restart obex.service; sleep 2
systemctl --user --no-pager status obex.service | head -6
bluetoothctl show | grep -i 112f && echo "PBAP-Server registriert" || echo "PBAP-SDP fehlt"
gdbus call --session --dest com.lomiri.ObexCallData --object-path /contacts --method com.lomiri.Contacts.Count || true
EOF
