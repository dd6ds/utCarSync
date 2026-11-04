<!-- Issue for https://gitlab.com/ubports/development/core/packaging/bluez/-/issues
     (alternatively ubports/ubuntu-touch issues) -->

# Title

PBAP: connection from an untrusted paired device hangs, RFCOMM channel refused afterwards

# Description

Device: Xiaomi Poco X3 Pro (vayu), 24.04-2.x stable, bluez 5.85 with the lomiri phonebook plugin (MR !8).

Steps:
1. Pair a laptop (BlueZ) with the phone. On the phone, `bluetoothctl info <laptop>` shows `Trusted: no`
2. On the laptop: `org.bluez.obex.Client1.CreateSession(<phone>, {"Target": "PBAP"})`

Result:
- The first attempt ends with `org.freedesktop.DBus.Error.NoReply`. obexd (run with `-d`) never
  receives `NewConnection` for the PBAP profile, and no authorization dialog appears on the phone.
  bluetoothd then logs:
  `src/profile.c:ext_io_disconnected() Unable to get io data for Phone Book Access: getpeername: Transport endpoint is not connected (107)`
- All later attempts fail with `Connection refused (111)` on RFCOMM channel 15
  (SDP still announces PBAP PSE 1.1 on channel 15)
- Restarting obexd does not help. `bluetoothctl power off && bluetoothctl power on` does.

Workaround: `bluetoothctl trust <device>` on the phone, then toggle Bluetooth. After that,
PBAP works (174 contacts, all call lists).

Expected: Either the user gets asked to allow phonebook access for the device (Lomiri agent
`AuthorizeService`), or paired car kits / PBAP clients get authorized. In either case, a
pending or failed authorization should not leave the profile listener broken.
