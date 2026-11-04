#!/usr/bin/env bash
# HCI-Mitschnitt auf dem Telefon (btmon braucht root -> sudo, Passwort = Entsperr-Code)
#   phone-btsnoop.sh start      startet btmon im Hintergrund auf dem Telefon
#   phone-btsnoop.sh stop       stoppt btmon und holt die Datei nach analysis/captures/
# UT_PW=<code> setzen, sonst wird gefragt.
set -eu
CAP=/home/phablet/utcarsync.btsnoop
DST="$(dirname "$0")/../analysis/captures"
[ -n "${UT_PW:-}" ] || { read -rsp "UT-Passwort/PIN: " UT_PW; echo; }
case "${1:-}" in
  start)
    adb shell "echo '$UT_PW' | sudo -S sh -c 'rm -f $CAP; nohup btmon -w $CAP >/dev/null 2>&1 &'"
    adb shell "pgrep -a btmon" && echo "btmon läuft – jetzt Kabel ab, ins Auto, koppeln, anrufen lassen"
    ;;
  stop)
    adb shell "echo '$UT_PW' | sudo -S pkill -INT btmon; sleep 1; echo '$UT_PW' | sudo -S chmod 644 $CAP"
    mkdir -p "$DST"; f="$DST/mib2-$(date +%Y%m%d-%H%M%S).btsnoop"
    adb pull "$CAP" "$f" && echo "-> $f" && btmon -r "$f" | grep -Ei 'obex|112f|pbap|phonebook|rfcomm' | head -40
    ;;
  *) echo "usage: $0 start|stop"; exit 1;;
esac
