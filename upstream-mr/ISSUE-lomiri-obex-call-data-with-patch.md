<!-- Issue (ohne Fork) für https://gitlab.com/ubports/development/core/lomiri-obex-call-data/-/issues/new
     Anhängen: ../patches/lomiri-obex-call-data/0001-*.patch und 0002-*.patch
     (per Drag & Drop ins Textfeld oder über "Attach a file") -->

# Title

Empty phonebook on 24.04-2 stable: contacts are in galera, service only reads qtcontacts-sqlite (patch attached)

# Description

I can't open a merge request (fork requires identity verification), so I'm attaching the patches
here. They apply with `git am` on `main` and build as a Debian package for arm64.

## Problem

`ContactsService` always opens the `org.nemomobile.contacts.sqlite` backend. On Ubuntu Touch
24.04-2.x stable the user's contacts are still stored in address-book-service (`galera`), and
qtcontacts-sqlite is not installed or empty. So obexd's PBAP server (phonebook-lomiri, bluez MR !8)
sends an empty phonebook to car kits.

## Patches

1. `0001-contactsservice-select-contacts-backend-at-runtime.patch`
   The backend is picked at startup: `$LOMIRI_OBEX_CONTACTS_BACKEND` if set ->
   qtcontacts-sqlite if installed and not empty -> galera if installed -> qtcontacts-sqlite.
   The chosen backend is logged. Nothing changes on devices that already use qtcontacts-sqlite.
2. `0002-d-control-accept-galera-as-alternative-contacts-back.patch`
   `Depends: libqt5contact5-plugin-sqlite | qtcontact5-galera`

## Testing

Xiaomi Poco X3 Pro (vayu), `24.04-2.x/arm64/android9plus/stable`, 174 contacts in address-book-service,
`bluez-obexd` from `ubports/latest` (5.85 with obexd-add-lomiri-phonebook-plugin.patch) plus these patches:

| Test | Stock 24.04-2 | With bluez !8 + patches |
|---|---|---|
| `com.lomiri.Contacts.Count` | – | 174 (`using contacts backend "galera"`) |
| PBAP PCE (BlueZ on a laptop): `pb` GetSize/List/PullAll(vcard21)/Pull | `Internal Server Error` | 174 / 174 / 174 / ok |
| `ich` / `och` / `mch` / `cch` | `Not Found` | 3 / 3 / 0 / 6 |
| Umlauts in vCard 2.1 | – | `CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE` ok |
| SEAT Leon 2019, VW MIB2 Standard (Technisat `MST2_EU_SE_ZR_P0516T`) | no contacts | contacts browsable in the car, incoming calls show the caller's name |

Note: galera can't sort by `QContactDisplayLabel` (logged as "No sorting support"). The car sorts by
itself, so this is not a blocker.

Build/CI used for testing: https://github.com/dd6ds/utCarSync

Related: bluez packaging MR !8, forum topic https://forums.ubports.com/topic/10556
