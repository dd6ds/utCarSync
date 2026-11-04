<!-- Comment for https://gitlab.com/ubports/development/core/packaging/bluez/-/merge_requests/8 -->

Test report: works in a car 🎉

- Device: Xiaomi Poco X3 Pro (vayu), `24.04-2.x/arm64/android9plus/stable`
- `bluez-obexd` built from `ubports/latest` (5.85-4ubports1, `--with-phonebook=lomiri`) for arm64
- `lomiri-obex-call-data` from `main` plus a fallback to the galera backend
  (patches: lomiri-obex-call-data#<ISSUE-NUMMER EINTRAGEN>). Without it the phonebook stays empty
  on 24.04-2 stable, because the contacts are still in address-book-service.

Results:
- Stock 24.04-2 obexd (phonebook-ebook): `pb` → `Internal Server Error`, call lists → `Not Found`
- With this MR: PBAP `pb` 174 contacts, `ich/och/mch/cch` ok (BlueZ PCE on a laptop)
- SEAT Leon 2019, VW MIB2 Standard (Technisat `MST2_EU_SE_ZR_P0516T`, HMI `H29.344.66_STD2Plus_EU`):
  contacts are browsable in the car, incoming calls show the caller's name

Would be great to get this into 24.04-2.x (the branch currently has no phonebook-lomiri patch).

Observation (separate issue opened, see <ISSUE-LINK>): if the PCE is not trusted on the phone,
the PBAP connection hangs in bluetoothd's authorization, and afterwards RFCOMM channel 15
refuses connections until Bluetooth is toggled.
