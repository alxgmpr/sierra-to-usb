# Keyed vendor-profile assemblies

J202 is **3M N2520-6002-RB**, mated to **89120-0101HA** (centre bump, no strain relief supplied). Make two separately labelled, permanently wired assemblies using 3M **3365/20** 28 AWG stranded ribbon. Add strain relief **3448-89120**. No loose individual jumpers are used. The header centre slot and socket bump establish orientation; align both position-1 triangles. The socket bottom-view drawing is mirrored relative to the PCB component-side view.

| Assembly | Join only these contact pairs |
|---|---|
| SIERRA EM9190 | 1–2, 3–4, 5–6, 7–8, 9–10, 11–12, 15–16, 17–18 |
| QUECTEL RM520N-GL V1.0 | 13–14, 15–16 |

Terminate the ribbon with the specified IDC press/locator arrangement; do not close it unevenly with pliers. Fold the ribbon through the strain relief, then join the specified pairs at the free end. Keep each conductor from IDC contact to splice at most25 mm; solder, insulate each splice separately and enclose all ends in a labelled insulating sleeve. Unused conductors end separately insulated, with no exposed copper. This is a fabricated harness, not an off-the-shelf coded plug. Its final termination and retention require first-article inspection.

The power calculation does not depend on the three supplemental Sierra supply paths for its minimum five-contact supply model. Their branch current must remain below1 A. The 891 current table permits1.25 A per line with all28 AWG lines powered under the stated thermal test; the header permits1.75 A with all contacts powered. These ratings do not establish hot assembly current sharing. Ribbon temperature rating limits this assembly to−20…+105°C before system derating.

Reserve **34×10 mm** around the header body, plus a **34×25 mm** ribbon/splice service area beside it and **22 mm** clear height above the carrier. The header drawing gives32.72×8.59 mm body and9.91 mm height. The socket drawing gives30.0 mm length and approximately16.3 mm assembled socket/strain-relief height; the22 mm reserve accommodates the mated assembly conservatively. Confirm actual mated height and cable folding on the first article. The connector is a standard keyed 20-pin IDC connection, not a debug/programming port. Keep its plug fitted during operation. The orange service-volume model has been removed; the header remains.

Before installing either harness, check every pair against this table and test that every other pair is isolated. On the unpowered assembled carrier, verify Sierra continuity to24/38/68/20/22/28 and Quectel isolation of all six. Then exercise absent, code00 and code11 cases and verify BUCK_EN remains low. A valid plug cannot identify the wrong physical modem: match its permanent label to the actual module. Disconnect USB, wait10 s and measure VCC below0.1 V before any change.

Sources reviewed2026-09-06: [3M header drawing Rev U,2026-03-04](https://multimedia.3m.com/mws/media/330367O/3m-four-wall-header-2500-series-ts-0770.pdf), [891 drawing Rev M,2021-04-27](https://multimedia.3m.com/mws/media/22265O/3mtm-idc-ribbon-cable-socket-891-series-ts0449.pdf), [891 product specification Rev C](https://multimedia.3m.com/mws/media/787866O/3m-tm-idc-ribbon-cable-socket-891-series.pdf), and [3365 ribbon data](https://multimedia.3m.com/mws/media/22052O/3m-round-conductor-flat-cable-050in-3365-series-ts0080.pdf). Read-only distributor snapshot: `build/profile-stock.json`. No procurement or supplier contact occurred.
