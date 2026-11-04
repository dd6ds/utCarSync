#!/usr/bin/env python3
"""Einmaliges Hilfsskript: baut den Backend-Auswahl-Patch in lomiri-obex-call-data ein."""
import sys, pathlib

src = pathlib.Path(sys.argv[1]) / "src" / "contactsservice.cpp"
s = src.read_text()

old_def = 'static const char *DEFAULT_BACKEND_NAME = "org.nemomobile.contacts.sqlite";\n'
new_def = '''static const char *DEFAULT_BACKEND_NAME = "org.nemomobile.contacts.sqlite";
static const char *LEGACY_BACKEND_NAME = "galera"; // address-book-service (UT 24.04-1.x)

// Choose the QtContacts backend that actually holds the user's contacts.
// 1. $LOMIRI_OBEX_CONTACTS_BACKEND, if set
// 2. qtcontacts-sqlite, if installed and not empty
// 3. galera (address-book-service), if installed
// 4. qtcontacts-sqlite as last resort
static QString selectBackend()
{
    const QString forced = qEnvironmentVariable("LOMIRI_OBEX_CONTACTS_BACKEND");
    if (!forced.isEmpty()) {
        qDebug() << "contacts backend forced by environment:" << forced;
        return forced;
    }

    const QStringList available = QContactManager::availableManagers();
    const QString sqlite = QString::fromLatin1(DEFAULT_BACKEND_NAME);
    const QString legacy = QString::fromLatin1(LEGACY_BACKEND_NAME);
    qDebug() << "available contacts backends:" << available;

    if (available.contains(sqlite)) {
        QContactManager probe(sqlite);
        if (!probe.contactIds().isEmpty() || !available.contains(legacy)) {
            return sqlite;
        }
        qDebug() << "qtcontacts-sqlite is empty, falling back to" << legacy;
    }
    if (available.contains(legacy)) {
        return legacy;
    }
    return sqlite;
}
'''
assert old_def in s, "DEFAULT_BACKEND_NAME not found"
s = s.replace(old_def, new_def, 1)

old_init = "    , mManager(DEFAULT_BACKEND_NAME)\n{\n}"
new_init = ("    , mManager(selectBackend())\n{\n"
            "    qDebug() << \"using contacts backend\" << mManager.managerName();\n}")
assert old_init in s, "constructor init not found"
s = s.replace(old_init, new_init, 1)
src.write_text(s)
print("patched", src)
