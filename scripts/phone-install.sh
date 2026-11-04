#!/usr/bin/env bash
# Installiert bluez-obexd (PBAP) + lomiri-obex-call-data auf dem UT-Telefon.
#   phone-install.sh <ordner-mit-debs>     installieren
#   phone-install.sh --rollback            Originalpakete aus dem UBports-Repo zurück
# Die Installation läuft über phone-repair.sh: apt mit --no-remove und einem
# Probelauf, der abbricht, sobald apt etwas entfernen will.
# (Die erste Version nutzte "dpkg -i || apt-get -f install" und hat dabei
#  ubuntu-touch-Metapakete entfernt -> nie wieder -f install.)
# Achtung: Ein OTA-Update überschreibt das Root-Dateisystem -> danach erneut installieren.
set -eu
HERE="$(dirname "$0")"
if [ "${1:-}" = "--rollback" ]; then
  exec "$HERE/phone-repair.sh" --original
fi
DIR="${1:?Ordner mit den .deb angeben}"
adb get-state >/dev/null
adb shell 'mkdir -p /home/phablet/utcarsync'
adb push "$DIR"/bluez-obexd_*_arm64.deb "$DIR"/lomiri-obex-call-data_*_arm64.deb /home/phablet/utcarsync/
exec "$HERE/phone-repair.sh"
