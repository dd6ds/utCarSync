# VAG MIB2 Standard (Technisat) – Notizen

Gerät von Dennis: SEAT Leon, Baujahr 2019
- Software `MST2_EU_SE_ZR_P0516T`, HW `H50`, SW/MU `0516`, Codec `5001.0.0.2`
- HMI `H29.344.66_STD2Plus_EU`, Model `GuideModel_29.344.12`, Base `H29.344.66-201906171929`
- Hersteller Technisat -> „MIB2 Standard / Composition Media/Colour“ (Plattform Seat/Skoda/VW, Firmware 0516 vom Juni 2019)

Zu prüfen (in Mitschnitten bestätigen, nicht als gesichert ansehen):
- PBAP-Version, die das Gerät anfragt (1.1 über RFCOMM oder 1.2 über L2CAP/GOEP)
- vCard 2.1 oder 3.0, welche Filterbits (N, TEL, FN, PHOTO?)
- ob es zuerst `MaxListCount=0` schickt und dann in welchen Blöcken lädt
- ob es Anruflisten (`cch`) lädt und ob deren Fehlen den ganzen Download abbricht
- ob es zusätzlich MAP (Nachrichten) anfragt; das ist für die Kontakte nicht nötig
- ob es zum Normalisieren der Nummer `+49` und `0` gleich behandelt

UBports hat schon einen Carkit-Fix für Nissan (`device-fixes-nissan-connect.patch`):
Fahrzeugspezifische BlueZ-Workarounds werden dort also angenommen.
