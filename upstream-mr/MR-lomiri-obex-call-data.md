<!-- Merge request for https://gitlab.com/ubports/development/core/lomiri-obex-call-data
     Source branch: personal/dd6ds/contacts-backend-fallback (from your fork)
     Target branch: main -->

# Title

contactsservice: honour LOMIRI_CONTACT_BACKEND (fixes empty phonebook on galera devices)

# Description

## Problem

`ContactsService` always opens the `org.nemomobile.contacts.sqlite` backend.
On Ubuntu Touch 24.04-2.x stable the user's contacts are still stored in
address-book-service (`galera` QtContacts backend), and `qtcontacts-sqlite` is
either not installed or empty. As a result, obexd's PBAP server (phonebook-lomiri
plugin, bluez MR !8) sends an empty phonebook to car kits.

## Change

1. `contactsservice: honour LOMIRI_CONTACT_BACKEND`
   Use the session-wide `LOMIRI_CONTACT_BACKEND` variable (set by ubuntu-touch-pim-settings and present
   in the systemd user environment the service is activated from), with qtcontacts-sqlite as default.
   The chosen backend is logged.

2. `d/control: accept galera as alternative contacts backend`
   `Depends: libqt5contact5-plugin-sqlite | qtcontact5-galera`, so the package can
   be installed on galera-only devices without pulling in an unused backend.

## Testing

Device: Xiaomi Poco X3 Pro (vayu), channel `24.04-2.x/arm64/android9plus/stable`,
174 contacts in address-book-service.
Packages: `bluez-obexd` built from `ubports/latest` (5.85, with
`obexd-add-lomiri-phonebook-plugin.patch`) plus this branch, both built for arm64.

| Test | Before (stock 24.04-2) | With bluez MR !8 + this MR |
|---|---|---|
| `com.lomiri.Contacts.Count` | backend sqlite: 0 | 174 (`LOMIRI_CONTACT_BACKEND=galera`, `using contacts backend "galera"`) |
| PBAP PCE on a Linux laptop (`org.bluez.obex.PhonebookAccess1`): `pb` GetSize / List / PullAll(vcard21) / Pull | `Internal Server Error` | 174 / 174 / 174 vCards / ok |
| `ich` / `och` / `mch` / `cch` | `Not Found` | 3 / 3 / 0 / 6 |
| Umlauts in vCard 2.1 | – | `N;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE` ok |
| SEAT Leon 2019, VW MIB2 Standard (Technisat, SW `MST2_EU_SE_ZR_P0516T`) | no contacts | contacts browsable in the car, incoming calls show the caller's name |

Note: galera does not support sorting by `QContactDisplayLabel`
(`No sorting support for QContactSortOrder(detailType=25 ...)` in the log). The car
sorts by itself, so this is not a blocker. A follow-up could sort by `QContactName`
when the backend is galera.

## Related

- bluez packaging MR !8 "Obexd: add lomiri pbap plugin"
- Forum: "Sync Contacts via Bluetooth - VAG Group Car not working"
  https://forums.ubports.com/topic/10556
