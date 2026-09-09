"""Reproduce preliminary geometry/cost arithmetic; never a board qualification."""
import json
from math import sqrt
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    pitch = 0.65  # RK3568B2 datasheet v2.3, Fig 2-4 (mm)
    land = 0.30  # Hypothesis, not a released footprint
    drill = 0.20
    via = 0.40
    clearance = 0.10
    track = 0.10
    hole_to_track = 0.20  # JLC current published capability
    report = {
        "status": "PRELIMINARY_ONLY_NOT_A_LAYOUT_OR_RELEASE",
        "bga_hypotheses_mm": {
            "pitch": pitch, "land_diameter": land, "via_drill": drill,
            "via_pad": via, "copper_clearance": clearance,
            "trace_width": track, "hole_to_track_clearance": hole_to_track,
        },
        "bga_geometry_mm": {
            "one_trace_between_adjacent_lands_margin": pitch - land - track - 2 * clearance,
            "cell_center_via_to_nearest_land_clearance": pitch / sqrt(2) - (land + via) / 2,
            "straight_track_between_adjacent_drills_available_width": pitch - drill - 2 * hole_to_track,
            "straight_track_between_adjacent_drills_margin": pitch - drill - 2 * hole_to_track - track,
        },
        "bga_conclusion": "An isolated dogbone fits these hypotheses, but a uniform via grid obstructs inner routing. This does not establish full escape, layer count, impedance or manufacturability.",
        "nominal_bandwidth_gbit_per_s": {
            "usb3_gen1_after_8b10b_before_protocol": 5 * 8 / 10,
            "pcie_gen2_x1_after_8b10b_before_protocol": 5 * 8 / 10,
            "ethernet_line_rate": 2.5,
        },
        "bandwidth_conclusion": "Link capacities are plausible for a 2.5GbE modem path; no Linux forwarding or modem throughput has been measured.",
        "candidate_cost_usd_10plus": {
            "RK3568B2_x1": 17.5365, "RK809_5_x1": 2.1103,
            "H5TQ4G63EFR_RDC_x2": 2 * 15.8248,
            "THGBMUG6C1LBAIL_x1": 31.7407,
            "RTL8125BG_CG_x1": 3.8025, "RP2350B_x1": 1.1959,
        },
        "cost_exclusions": "These are unqualified candidate ICs, not a BOM. Excludes CPU regulator, other power components, PoE, magnetics, connectors, passives, MCU flash, PCB, assembly, testing, heatsinks, modem, antennas, shipping and taxes.",
        "power": {
            "EM9190_sub6_document_peak_a": 3.0,
            "EM9190_sub6_document_continuous_a": 2.3,
            "EM9190_mmwave_document_peak_a": 5.0,
            "nominal_3v3_sub6_peak_w": 3.3 * 3.0,
            "RTL8125BG_document_nominal_rail_max_test_current_power_w": 3.3 * 0.100 + 0.95 * 0.650,
            "unresolved": [
                "Final exact modem profiles and worst operating condition across them",
                "SoC/DDR rail demand, startup and simultaneous workloads",
                "Exact storage maximum current and startup",
                "Converter hot loss bounds and transient/inrush requirements",
                "Hardware-enforced accessory and fan allocations",
                "Magnetics DC current/unbalance and isolation qualification",
            ],
            "poe_class": None,
            "reason": "The complete worst-case budget is not closed. Do not select a PoE class using this partial sum or a regulator current rating.",
        },
        "erc": "NOT_RUN_NO_NEW_SCHEMATIC",
        "parity": "NOT_RUN_NO_NEW_CAD",
        "drc": "NOT_RUN_NO_NEW_PCB",
        "routed_board": False,
    }
    report["candidate_ic_subtotal_usd"] = round(sum(report["candidate_cost_usd_10plus"].values()), 4)
    out = root / "engineering-screen.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "candidate_ic_subtotal_usd": report["candidate_ic_subtotal_usd"], "poe_class": None}))


if __name__ == "__main__":
    main()
