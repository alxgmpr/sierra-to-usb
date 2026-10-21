# Modem documentation and exact-module release gates

Reviewed 2026-10-21. All four profiles remain `released: false`. The socket's
assembly selection is checked electrically; it is not a four-modem support claim.
No modem pin, pull or timing was changed on the basis of an unavailable guide.

| Module | Current manufacturer evidence | Remaining documentation blocker |
|---|---|---|
| EM9190 | [EM919x/EM7690 PTS listing](https://source.sierrawireless.com/resources/airprime/minicard/airprime_em919x-7690_product_technical_specification) lists Rev11. The actual download redirects to “Sign in required”. The project has Rev5. | Obtain controlled Rev11 and compare the complete pin/power/control/USB tables against Rev5 and this capture for the exact order code and hardware revision. |
| EM9293 | [EM92xx PTS listing](https://source.sierrawireless.com/resources/airprime/minicard/airprime_em92xx_product_technical_specification) lists Rev7.2. Its actual download also redirects to sign-in. The project has Rev1. | Obtain Rev7.2 and perform the same exact-module comparison; do not inherit EM9190 results. |
| RM520N-GL | [Quectel's RM520N resources](https://www.quectel.com/product/5g-rm520n-series/) list **Series Hardware Design V1.4** and Reference Design V1.2, both behind Login. The project has RM520N-GL Hardware Design V1.0. | Obtain V1.4 and the matching reference design; establish applicability to the exact order code/hardware before comparing contacts, timing and power. A product specification brochure with the same version number is not the Hardware Design guide. |
| RM551E-GL | [Manufacturer EVB listing](https://www.quectel.com/product/5g-mmwave-evb-kit/) includes this model. No controlled production Hardware Design was obtained from public manufacturer resources. | Obtain the released guide and exact production hardware/firmware identity. Do not turn a third-party indexed V0.1 draft, brochure or another Quectel module's pinout into production evidence. mmWave antenna/power hardware remains outside this capture. |

Access checks used unauthenticated downloads. No account was created, vendor
contact made, firmware downloaded/flashed or device exercised. Redirect URLs,
HTTP/content types, listing hashes, archived-guide hashes and the comparison
checklist are recorded in
[modem-documentation-review.json](../hardware/reference/modem-documentation-review.json).

## A concrete order-code exclusion

Quectel staff identify **RM520NGLAP-M20-HP** as a customer-specific, PCIe-only
variant in the [manufacturer forum response](https://forums.quectel.com/t/rm520n-gl-vs-rm520n-eu/39629).
Exclude that order code from this USB-host architecture. This does not establish
USB support for every other RM520N-GL order code; obtain supplier confirmation
and measure SuperSpeed enumeration on the purchased module. Do not flash a
different SKU's firmware to try to satisfy this gate.

## What must be compared and recorded

For each guide, review all 67 socket contacts for direction, voltage, pulls,
unused-pin termination and power-off behavior. In particular, recheck contacts
20/22/24/38/68/73, USB-mode selection/VBUS sense, RESET and
FULL_CARD_POWER_OFF voltage/timing, USB coupling/ESD, SIM voltage/detect handling
and complete burst/RF accessory power demand.

Sierra VCC contacts 24/38/68 remain connected only by Sierra stuffing. Quectel
must omit R2011/R2012/R2013/R2016/R2017 and C2036/C2037/C2038. Software detection
after applying power cannot replace safe assembly selection. The RM551E profile's
five common VCC contacts are still **provisional**, not verified by a current guide.

Record the order code, hardware revision, firmware, carrier/PRI, SIM/APN,
USB VID/PID/composition, host kernel/driver, software-image hash and measured
boot/traffic/power/recovery results. Every field currently lacks a complete
qualified tuple. Current-document access alone cannot release a profile.

The new `check_modem_documentation.py` runs from `hardware/check.py` and rejects
accidental release of any of these unqualified profiles, missing model rows or
loss of the known order-code exclusion. Existing connectivity checks independently
compute VCC reachability through fitted zero-ohm links for each stuffing profile.
