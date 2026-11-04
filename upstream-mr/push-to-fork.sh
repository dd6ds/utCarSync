#!/usr/bin/env bash
# Pusht den MR-Branch in deinen GitLab-Fork von lomiri-obex-call-data.
#   push-to-fork.sh <gitlab-benutzername> [ssh|https]
# Voraussetzung: Fork existiert (gitlab.com/ubports/development/core/lomiri-obex-call-data -> "Fork").
set -eu
U="${1:?GitLab-Benutzername angeben}"; MODE="${2:-ssh}"
REPO="$(cd "$(dirname "$0")/../upstream/lomiri-obex-call-data" && pwd)"
BR=personal/dd6ds/contacts-backend-fallback
cd "$REPO"
if [ "$MODE" = ssh ]; then URL="git@gitlab.com:$U/lomiri-obex-call-data.git"
else URL="https://gitlab.com/$U/lomiri-obex-call-data.git"; fi
git remote remove fork 2>/dev/null || true
git remote add fork "$URL"
echo "Commits im MR:"; git log --format='  %h %an <%ae> %s' origin/main.."$BR"
git log --format='%ae%n%ce' origin/main.."$BR" | grep -qviE '^(dd6ds@eclipso.de|noreply@anthropic.com)$' \
  && { echo "ABBRUCH: unerwartete E-Mail im Commit"; exit 1; }
git push -u fork "$BR"
echo
echo "Jetzt MR öffnen:"
echo "https://gitlab.com/$U/lomiri-obex-call-data/-/merge_requests/new?merge_request%5Bsource_branch%5D=$BR&merge_request%5Btarget_project_id%5D=ubports%2Fdevelopment%2Fcore%2Flomiri-obex-call-data&merge_request%5Btarget_branch%5D=main"
echo "Titel/Beschreibung: upstream-mr/MR-lomiri-obex-call-data.md"
