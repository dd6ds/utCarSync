#!/usr/bin/env python3
"""Laptop spielt 'Auto' (PBAP-Client) und lädt das Telefonbuch vom UT-Telefon.

Voraussetzung auf dem Laptop: bluez-obexd läuft in der Session (systemctl --user start obex),
Telefon und Laptop sind gekoppelt.  python3-dbus.

  ./laptop-pbap-test.py AA:BB:CC:DD:EE:FF [--format vcard21|vcard30]
Ergebnis: analysis/captures/pbap-<repo>-<folder>.vcf
"""
import argparse, os, sys, time
import dbus

OBEX = "org.bluez.obex"
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis", "captures")


def wait_transfer(bus, path, timeout=60):
    props = dbus.Interface(bus.get_object(OBEX, path), "org.freedesktop.DBus.Properties")
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            st = props.Get("org.bluez.obex.Transfer1", "Status")
        except dbus.DBusException:
            return "complete"  # Objekt schon entfernt = fertig
        if st in ("complete", "error"):
            return str(st)
        time.sleep(0.3)
    return "timeout"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("addr")
    ap.add_argument("--format", default="vcard21")
    a = ap.parse_args()
    os.makedirs(OUTDIR, exist_ok=True)
    bus = dbus.SessionBus()
    client = dbus.Interface(bus.get_object(OBEX, "/org/bluez/obex"), "org.bluez.obex.Client1")
    try:
        session = client.CreateSession(a.addr, {"Target": "PBAP"})
    except dbus.DBusException as e:
        sys.exit(f"CreateSession fehlgeschlagen (kein PBAP-Server auf dem Telefon?): {e}")
    print("Session:", session)
    pbap = dbus.Interface(bus.get_object(OBEX, session), "org.bluez.obex.PhonebookAccess1")
    rc = 0
    for folder in ("pb", "ich", "och", "mch", "cch"):
        try:
            pbap.Select("int", folder)
            size = pbap.GetSize()
            listing = pbap.List({})
            print(f"\n[{folder}] GetSize={int(size)}  List={len(listing)} Einträge")
            for h, n in list(listing)[:10]:
                print(f"   {h:>8}  {n}")
            out = os.path.abspath(os.path.join(OUTDIR, f"pbap-int-{folder}.vcf"))
            tr, _ = pbap.PullAll(out, {"Format": a.format})
            st = wait_transfer(bus, tr)
            n = open(out, errors="replace").read().count("BEGIN:VCARD") if os.path.exists(out) else 0
            print(f"   PullAll({a.format}) -> {st}, {n} vCards -> {out}")
            if folder == "pb" and n and listing:
                tr, _ = pbap.Pull(listing[0][0], out + ".first", {"Format": a.format})
                print("   Pull(erster Eintrag) ->", wait_transfer(bus, tr))
        except dbus.DBusException as e:
            rc = 1
            print(f"[{folder}] FEHLER: {e.get_dbus_name()}: {e.get_dbus_message()}")
    client.RemoveSession(session)
    sys.exit(rc)


if __name__ == "__main__":
    main()
