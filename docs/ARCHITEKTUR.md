# Architektur

```
 Auto (MIB2, PBAP-Client/PCE, HFP-Handsfree)
   |  1. SDP-Abfrage: hat das Telefon einen "Phonebook Access PSE" (UUID 0x112F)?
   |  2. RFCOMM oder L2CAP (PBAP 1.2 mit GOEP 2.0) -> OBEX CONNECT, Target = PBAP
   |  3. PullPhoneBook telecom/pb.vcf  (MaxListCount=0 -> nur Anzahl)
   |  4. PullPhoneBook telecom/pb.vcf  in Blöcken, Format vCard 2.1/3.0, Filter
   |  5. dasselbe für ich/och/mch/cch (Anruflisten), optional SIM1/...
   v
 bluetoothd (BlueZ)  <- obexd registriert sein PBAP-Profil über org.bluez.ProfileManager1
   |
 obexd (User-Session!)  plugins/pbap.c + phonebook-lomiri.c
   |  D-Bus Session-Bus, Dienst wird bei Bedarf per D-Bus aktiviert
   v
 com.lomiri.ObexCallData   (lomiri-obex-call-data)
   /contacts     com.lomiri.Contacts     Count / Fetch(off,len,fmt,filter) / FetchById
   /callhistory  com.lomiri.CallHistory  Count(type) / Fetch(type,...) / FetchById
   |
   +-- QtContacts (address-book-service bzw. das neue Kontakt-Backend)
   +-- History-Service (Anrufliste)

 Eingehender Anruf:
   ofono (HFP Audio Gateway) --RING / +CLIP: "+4917..."--> Auto
   Das Auto sucht die Nummer im per PBAP geladenen Telefonbuch -> zeigt den Namen
```

## Rückgabeformat

`a(ssss)` = Liste aus (id, name, tel, vcard). obexd setzt daraus zusammen:
- `pb.vcf`: alle vCards hintereinander (PullPhoneBook)
- `pb/` Listing: `<card handle="N.vcf" name="Nachname;Vorname"/>` (PullvCardListing)
- `0.vcf` ist laut PBAP die eigene Visitenkarte (Owner-Card), sie muss
  vorhanden sein, sonst verschieben sich bei manchen Autos die Indizes

## Wo es typischerweise hakt

1. obexd läuft gar nicht (Autostart in der Lomiri-Session, in 24.04-2 behoben)
2. obexd ohne PBAP-Plugin gebaut (`--with-phonebook=lomiri` fehlt) -> kein SDP-Eintrag
3. D-Bus-Aktivierung von `com.lomiri.ObexCallData` scheitert (Service-Datei/AppArmor)
4. vCard-Inhalt: Das MIB2 erwartet bei 2.1 `N` und `TEL;CELL` usw. Bei fehlendem `N`
   bleibt der Eintrag leer, bei Sonderzeichen ohne `CHARSET=UTF-8`/QP gibt es Zeichensalat
5. Rufnummernformat: Kontakt `0171...` vs. CLIP `+49171...` – das MIB2 normalisiert
   meist selbst, aber nicht immer
6. Das Auto fordert die Daten an, bevor der Benutzer „Kontakte teilen“ erlaubt hat
   (obexd-Agent/Autorisierung)
