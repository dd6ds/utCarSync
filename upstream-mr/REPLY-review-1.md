<!-- Antwort auf Lionels Diskussion in !3 (src/contactsservice.cpp) -->
Thanks, good point! Done: the custom detection is gone, the service now uses
`qEnvironmentVariable("LOMIRI_CONTACT_BACKEND", "org.nemomobile.contacts.sqlite")` and logs the chosen backend.

Re-tested on the Poco X3 Pro (24.04-2.x stable): `LOMIRI_CONTACT_BACKEND=galera` is in the systemd user
environment, the service (started through systemd) logs `using contacts backend "galera"`, and `Count` returns 174 contacts.

I kept the second commit (`Depends: libqt5contact5-plugin-sqlite | qtcontact5-galera`). Happy to drop it if you'd rather keep the hard dependency.
