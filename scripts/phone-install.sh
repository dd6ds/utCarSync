#!/usr/bin/env bash
# Installiert bluez-obexd (PBAP) + lomiri-obex-call-data auf dem UT-Telefon.
#   phone-install.sh <ordner-mit-debs>     installieren
#   phone-install.sh --rollback            Original-bluez-obexd aus dem UBports-Repo zurück
# Achtung: Ein OTA-Update überschreibt das Root-Dateisystem -> danach erneut installieren.
# UT_PW=<code> setzen, sonst wird gefragt.
set -eu
[ -n "${UT_PW:-}" ] || { read -rsp "UT-Passwort/PIN: " UT_PW; echo; }
S() { adb shell "echo '$UT_PW' | sudo -S -p '' $*"; }
adb get-state >/dev/null

if [ "${1:-}" = "--rollback" ]; then
  S mount -o remount,rw /
  S apt-get update
  S apt-get install -y --reinstall --allow-downgrades bluez-obexd
  S apt-get remove -y lomiri-obex-call-data || true
  S mount -o remount,ro / || true
  adb shell 'systemctl --user restart obex'
  exit 0
fi

DIR="${1:?Ordner mit den .deb angeben}"
ls "$DIR"/bluez-obexd_*_arm64.deb "$DIR"/lomiri-obex-call-data_*_arm64.deb >/dev/null
adb shell 'mkdir -p /home/phablet/utcarsync'
adb push "$DIR"/bluez-obexd_*_arm64.deb "$DIR"/lomiri-obex-call-data_*_arm64.deb /home/phablet/utcarsync/
adb shell 'dpkg-query -W bluez-obexd lomiri-obex-call-data 2>/dev/null' | tee "$(dirname "$0")/../analysis/versions-before-install.txt" || true

S mount -o remount,rw /
S sh -c "'dpkg -i /home/phablet/utcarsync/*.deb || apt-get -f install -y'"
S mount -o remount,ro / || echo "(remount ro später per Neustart)"

adb shell 'export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
  systemctl --user daemon-reload
  systemctl --user enable obex.service 2>/dev/null || true
  systemctl --user restart obex.service
  sleep 2; systemctl --user --no-pager status obex.service | head -8
  echo; bluetoothctl show | grep -i 112f && echo "PBAP-Server registriert" || echo "PBAP-SDP fehlt noch"
  gdbus call --session --dest com.lomiri.ObexCallData --object-path /contacts --method com.lomiri.Contacts.Count'
