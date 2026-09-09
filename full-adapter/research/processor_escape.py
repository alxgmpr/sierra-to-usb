"""Generate a processor escape study, not a board or manufacturing release.

Uses real package balls, all power/ground via obstacles, and deterministic
straight/45-degree escape candidates. KiCad DRC is the independent check.
The coupon does not establish impedance, pair matching, DDR topology or PI.
"""
from pathlib import Path
import copy
import json
import math
import uuid

import sexpdata as sx
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "studies"
S = sx.Symbol


def n(tag, *values):
    return [S(tag), *values]


def children(node, tag):
    return [v for v in node if isinstance(v, list) and str(v[0]) == tag]


def uid(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "full-adapter-escape/" + key))


def signal_name(pin):
    name = pin["workbook_name"]
    ddr = pin.get("ddr3_function")
    if ddr and ddr not in {"DDR3_ODT1", "DDR3_CS1n"}:
        return ddr
    if name.startswith(("EMMC_", "USB3_HOST1_", "PCIE20_", "I2C0_", "UART2_")):
        return name.split("/")[0]
    if pin["ball"] in {"AA20", "AC22", "AF25"}:
        return next(v for v in name.split("/") if v.startswith("PCIE20_"))
    if name in {"DDR_RZQ", "DDR_VREFOUT", "XIN24M", "XOUT24M", "nPOR_u", "USB3_OTG0_DP", "USB3_OTG0_DM", "USB3_OTG0_VBUSDET", "USB3_OTG0_ID"}:
        return name
    if pin["ball"] in {"AD23", "AG28"}:
        return name.split("/")[0]
    return None


def main():
    OUT.mkdir(exist_ok=True)
    pins = json.loads((ROOT / "research/processor-pins.json").read_text())["pins"]
    for pin in pins:
        pin["xy"] = tuple(round(c + 20, 6) for c in pin["xy_mm"])
        pin["signal"] = signal_name(pin)
        pin["via"] = bool(pin["signal"] or pin["pin_type"] in {"G", "AG", "PI", "API"})
        if pin["pin_type"] in {"G", "AG"}:
            pin["net"] = "GND"
        elif pin["pin_type"] in {"PI", "API"}:
            pin["net"] = pin["power_domain"] or pin["workbook_name"].rsplit("_", 1)[0]
        else:
            pin["net"] = pin["signal"] or ""
    # Fixed 0.15mm through drills with 0.30mm filled/capped lands. Clearance
    # measured from drill edge remains 0.20mm. Width 0.09mm is a local neckdown.
    width, clearance, drill, land = .09, .10, .15, .30
    via_pins = [p for p in pins if p["via"]]
    via_points = [Point(p["xy"]) for p in via_pins]
    via_tree = STRtree(via_points)
    pad_points = [Point(p["xy"]) for p in pins]
    pad_tree = STRtree(pad_points)
    layer_names = ["F.Cu", "In2.Cu", "In4.Cu", "B.Cu"]
    occupied = {layer: [] for layer in layer_names}
    routes, failures = [], []

    def valid(path, pin, layer):
        line = LineString(path)
        for i in via_tree.query(line.buffer(.4)):
            if via_pins[i]["ball"] != pin["ball"]:
                if line.distance(via_points[i]) < drill / 2 + .20 + width / 2 - 1e-8:
                    return False
        if layer == "F.Cu":
            for i in pad_tree.query(line.buffer(.4)):
                if pins[i]["ball"] != pin["ball"]:
                    if line.distance(pad_points[i]) < land / 2 + clearance + width / 2 - 1e-8:
                        return False
        return all(line.distance(other) >= width + clearance - 1e-8 for other in occupied[layer])

    signals = [p for p in pins if p["signal"]]
    # Hardest interior routes first, preserving outside channels for outer rows.
    signals.sort(key=lambda p: max(abs(c - 20) for c in p["xy"]))
    for pin in signals:
        x, y = pin["xy"]
        directions = sorted([(0, -1), (-1, 0), (1, 0), (0, 1)],
                            key=lambda d: -(d[0] * (x - 20) + d[1] * (y - 20)))
        found = None
        for layer in layer_names:
            for dx, dy in directions:
                for side in (0, 1, -1):
                    # Move to the corridor halfway between the ball columns.
                    corner = (round(x + dx * .325 - dy * side * .325, 6),
                              round(y + dy * .325 + dx * side * .325, 6))
                    end = (7 if dx < 0 else 33 if dx > 0 else corner[0],
                           7 if dy < 0 else 33 if dy > 0 else corner[1])
                    path = [(x, y), corner, end]
                    if valid(path, pin, layer):
                        found = dict(ball=pin["ball"], net=pin["signal"], layer=layer,
                                     path=path, length_mm=LineString(path).length)
                        occupied[layer].append(LineString(path))
                        break
                if found:
                    break
            if found:
                break
        if found:
            routes.append(found)
        else:
            failures.append(pin["ball"])

    fp = sx.loads((ROOT / "lib/full-adapter.pretty/RK3568B2_FCCSP636_19x19mm_P0.65mm.kicad_mod").read_text())
    fp[1] = "full-adapter:RK3568B2_FCCSP636_19x19mm_P0.65mm"
    fp.append(n("at", 20, 20))
    fp.append(n("uuid", uid("processor")))
    for prop in children(fp, "property"):
        if prop[1] == "Reference":
            prop[2] = "U1"
    by_ball = {p["ball"]: p for p in pins}
    for pad in children(fp, "pad"):
        if by_ball[pad[1]]["net"]:
            pad.append(n("net", by_ball[pad[1]]["net"]))
        pad.append(n("uuid", uid("pad/" + pad[1])))
    layers = [n(str(i), name, S("signal")) for i, name in
              [(0, "F.Cu"), (4, "In1.Cu"), (6, "In2.Cu"), (8, "In3.Cu"),
               (10, "In4.Cu"), (12, "In5.Cu"), (14, "In6.Cu"), (2, "B.Cu")]]
    layers += [n(str(i), name, S("user")) for i, name in
               [(1, "F.Mask"), (3, "B.Mask"), (5, "F.SilkS"), (7, "B.SilkS"),
                (13, "F.Paste"), (15, "B.Paste"), (17, "Dwgs.User"), (25, "Edge.Cuts"),
                (31, "F.CrtYd"), (29, "B.CrtYd"), (35, "F.Fab"), (33, "B.Fab")]]
    board = [S("kicad_pcb"), n("version", 20260206), n("generator", "full-adapter-escape"),
             n("general", n("thickness", 1.6)), n("paper", "A4"), n("layers", *layers),
             n("setup", n("pad_to_mask_clearance", 0)), fp]
    for p in via_pins:
        board.append(n("via", n("at", *p["xy"]), n("size", land), n("drill", drill),
                       n("layers", "F.Cu", "B.Cu"), n("net", p["net"]),
                       n("uuid", uid("via/" + p["ball"]))))
    for route in routes:
        for i, (a, b) in enumerate(zip(route["path"], route["path"][1:])):
            board.append(n("segment", n("start", *a), n("end", *b), n("width", width),
                           n("layer", route["layer"]), n("net", route["net"]),
                           n("uuid", uid(f'track/{route["ball"]}/{i}'))))
    for a, b in [((1, 1), (39, 1)), ((39, 1), (39, 39)), ((39, 39), (1, 39)), ((1, 39), (1, 1))]:
        board.append(n("gr_line", n("start", *a), n("end", *b),
                       n("stroke", n("width", .05), n("type", S("default"))),
                       n("layer", "Edge.Cuts"), n("uuid", uid(str(a)))))
    board.append(n("gr_text", "ESCAPE STUDY ONLY - NOT FOR FABRICATION", n("at", 20, 3),
                   n("layer", "Dwgs.User"), n("effects", n("font", n("size", .7, .7), n("thickness", .1)))))
    path = OUT / "processor-escape.kicad_pcb"
    path.write_text("(kicad_pcb\n" + "\n".join(sx.dumps(x) for x in board[1:]) + "\n)\n")
    report = dict(status="GEOMETRIC_ESCAPE_STUDY_NOT_RELEASE", selected_signals=len(signals),
                  escaped_signals=len(routes), failures=failures, populated_balls=len(pins),
                  vias=len(via_pins), via_drill_mm=drill, via_land_mm=land,
                  trace_width_mm=width, hole_to_track_clearance_mm=.20,
                  limitations=["No power planes or rail fanout yet", "No controlled-impedance stackup yet",
                               "No pair matching or return-via optimization", "Not a system PCB"], routes=routes)
    (OUT / "processor-escape.json").write_text(json.dumps(report, indent=2) + "\n")
    project = {"board": {"design_settings": {"rules": {
        "min_clearance": .1, "min_track_width": .09, "min_hole_clearance": .2,
        "min_hole_to_hole": .2, "min_via_diameter": .3,
        "min_through_hole_diameter": .15, "min_via_annular_width": .075,
        "min_copper_edge_clearance": .2, "solder_mask_min_width": .1,
    }}}, "meta": {"filename": "processor-escape.kicad_pro", "version": 1},
        "net_settings": {"classes": [{"name": "Default", "clearance": .1, "track_width": .09,
                                      "via_diameter": .3, "via_drill": .15}], "meta": {"version": 4}}}
    (OUT / "processor-escape.kicad_pro").write_text(json.dumps(project, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "routes"}, indent=2))


if __name__ == "__main__":
    main()
