"""Fail-closed CAD checkpoint checks. Coupon checks never authorize release."""
from collections import Counter
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / "full-adapter/.venv/bin/python"
if Path(sys.executable).parent != PYTHON.parent:
    if not PYTHON.is_file():
        raise SystemExit("Install full-adapter CAD validation dependencies first")
    result = subprocess.run([str(PYTHON), __file__, *sys.argv[1:]])
    raise SystemExit(result.returncode)

import sexpdata as sx


def children(node, tag):
    return [v for v in node if isinstance(v, list) and str(v[0]) == tag]


def one(node, tag):
    return children(node, tag)[0]


def check():
    tracked = subprocess.check_output(["git", "ls-files", "--cached"], cwd=ROOT, text=True).splitlines()
    cad = {p for p in tracked if p.endswith((".kicad_pcb", ".kicad_sch", ".kicad_pro"))}
    coupon = "full-adapter/studies/processor-escape"
    allowed = {coupon + ".kicad_pcb", coupon + ".kicad_pro"}
    ddr_cad = {"full-adapter/cad/" + p for p in
               ("full-adapter.kicad_sch", "full-adapter.kicad_pro",
                "ddr-signals.kicad_sch", "ddr-power.kicad_sch", "core-power.kicad_sch", "cpu-regulator.kicad_sch", "pmic-ldo.kicad_sch", "pmic-ddr.kicad_sch", "pmic-core.kicad_sch", "pmic-aux.kicad_sch", "pmic-control.kicad_sch", "processor-pmu.kicad_sch", "processor-io-power.kicad_sch", "processor-phy-power.kicad_sch", "processor-unused.kicad_sch", "processor-control.kicad_sch", "processor-clock.kicad_sch", "emmc-signals.kicad_sch", "emmc-power.kicad_sch", "console.kicad_sch", "recovery-usb.kicad_sch", "recovery-detect.kicad_sch")}
    allowed |= ddr_cad
    assert cad <= allowed, "Add explicit system electrical checks for new CAD: " + str(cad - allowed)
    assert allowed <= cad, "Coupon checkpoint requires both PCB and project settings"
    # Validate the staged snapshot, not a possibly newer/older file on disk.
    with tempfile.TemporaryDirectory(prefix="full-adapter-check-") as tmp:
        stage = Path(tmp)
        for path in tracked:
            if path.startswith("full-adapter/"):
                dest = stage / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(subprocess.check_output(["git", "show", ":" + path], cwd=ROOT))
        board_path = stage / (coupon + ".kicad_pcb")
        board = sx.loads(board_path.read_text())
        source = json.loads((stage / "full-adapter/research/processor-pins.json").read_text())
        pins = {p["ball"]: p for p in source["pins"]}
        assert len(pins) == 636
        fp = children(board, "footprint")
        assert len(fp) == 1 and one(fp[0], "property")[2] == "U1"
        pads = children(fp[0], "pad")
        assert len(pads) == 636 and {p[1] for p in pads} == set(pins)
        for pad in pads:
            assert one(pad, "at")[1:3] == pins[pad[1]]["xy_mm"]
        # Physical signal anchors from the manufacturer pin tables, independent
        # of the escape generator's selection logic.
        anchors = {"G1": "DDR3_DQS0P", "G2": "DDR3_DQS0N", "A9": "DDR3_DQ17",
                   "D8": "DDR3_CS0n", "B4": "DDR3_CLKP", "A4": "DDR3_CLKN",
                   "U27": "USB3_HOST1_SSRXN", "U28": "USB3_HOST1_SSRXP",
                   "V27": "USB3_HOST1_SSTXN", "V28": "USB3_HOST1_SSTXP",
                   "P24": "USB3_HOST1_DP", "P25": "USB3_HOST1_DM",
                   "W27": "PCIE20_TXP", "W28": "PCIE20_TXN",
                   "Y27": "PCIE20_RXP", "Y28": "PCIE20_RXN"}
        pad_nets = {p[1]: one(p, "net")[1] for p in pads if children(p, "net")}
        assert all(pad_nets[ball] == net for ball, net in anchors.items())
        report = json.loads((stage / "full-adapter/studies/processor-escape.json").read_text())
        assert report["status"] == "GEOMETRIC_ESCAPE_STUDY_NOT_RELEASE"
        assert report["selected_signals"] == report["escaped_signals"] == 114
        assert not report["failures"]
        segments = children(board, "segment")
        assert len(segments) == 228
        origin = one(fp[0], "at")[1:3]
        for route in report["routes"]:
            assert pad_nets[route["ball"]] == route["net"]
            start = [a + b for a, b in zip(origin, pins[route["ball"]]["xy_mm"])]
            assert all(abs(a - b) < 1e-6 for a, b in zip(start, route["path"][0]))
            assert max(abs(c - 20) for c in route["path"][-1]) >= 13
            actual = [s for s in segments if one(s, "net")[1] == route["net"]]
            assert len(actual) == 2
            for s, (a, b) in zip(actual, zip(route["path"], route["path"][1:])):
                assert one(s, "start")[1:3] == a and one(s, "end")[1:3] == b
                assert one(s, "layer")[1] == route["layer"]
                assert one(s, "width")[1] == .09
        project = json.loads((stage / (coupon + ".kicad_pro")).read_text())
        rules = project["board"]["design_settings"]["rules"]
        assert rules["min_hole_clearance"] >= .2 and rules["min_clearance"] >= .1
        drc_path = stage / "drc.json"
        subprocess.run(["/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli", "pcb", "drc",
                        str(board_path), "--format", "json", "-o", str(drc_path)], check=True,
                       stdout=subprocess.DEVNULL)
        drc = json.loads(drc_path.read_text())
        kinds = Counter(v["type"] for v in drc["violations"])
        assert not [v for v in drc["violations"] if v["type"] not in
                    {"via_dangling", "track_dangling", "lib_footprint_issues", "lib_footprint_mismatch"}], kinds
        assert kinds["track_dangling"] == 114 and kinds["via_dangling"] == 199, kinds
        assert len(drc["unconnected_items"]) == 251
        assert all("full-adapter" in v["description"] for v in drc["violations"]
                   if v["type"] == "lib_footprint_issues"), "Unexpected library fault"
        print("Coupon checkpoint: 636 pad positions, 114 escape paths, critical USB/PCIe/DDR anchors checked.")
        print("Fresh DRC: no geometry faults. UNFINISHED: 251 unconnected items, 199 dangling vias,")
        print("114 dangling ends. System ERC/parity/DRC and release remain NOT PASSED.")
        spec = importlib.util.spec_from_file_location(
            "staged_ddr_checks", stage / "full-adapter/tools/check_ddr.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        spec = importlib.util.spec_from_file_location(
            "staged_cpu_regulator_checks", stage / "full-adapter/tools/check_cpu_regulator.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("RK860 circuit checkpoint: all 20 balls, inductor, enable and remote sense checked; upstream power unfinished.")
        spec = importlib.util.spec_from_file_location(
            "staged_core_power_checks", stage / "full-adapter/tools/check_core_power.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("Core power checkpoint: 30 supply balls, 208 ground balls and 21 capacitors checked; upstream supplies unfinished.")
        spec = importlib.util.spec_from_file_location(
            "staged_pmic_library_checks", stage / "full-adapter/tools/check_pmic_library.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("PMIC library checkpoint: 68 pins, exposed ground and thermal lands checked; circuit unfinished.")
        spec = importlib.util.spec_from_file_location(
            "staged_pmic_ldo_checks", stage / "full-adapter/tools/check_pmic_ldo.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("PMIC LDO checkpoint: nine outputs, twelve capacitors and CPU enable source checked; PMIC integration unfinished.")
        spec = importlib.util.spec_from_file_location(
            "staged_pmic_ddr_checks", stage / "full-adapter/tools/check_pmic_ddr.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("PMIC DDR checkpoint: switching path, hardware divider and local bypass checked; upstream power unfinished.")
        spec = importlib.util.spec_from_file_location(
            "staged_pmic_core_checks", stage / "full-adapter/tools/check_pmic_core.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("PMIC core checkpoint: three switching paths and Kelvin feedback nets checked; physical placement unfinished.")
        spec = importlib.util.spec_from_file_location(
            "staged_pmic_aux_checks", stage / "full-adapter/tools/check_pmic_aux.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("PMIC auxiliary checkpoint: 1.8V buck and independent 3.3V switches checked; peripheral loads unfinished.")
        spec = importlib.util.spec_from_file_location(
            "staged_pmic_control_checks", stage / "full-adapter/tools/check_pmic_control.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("PMIC control checkpoint: all 69 pins, RTC and control passives checked; processor connections and startup recovery unfinished.")
        spec = importlib.util.spec_from_file_location(
            "staged_processor_pmu_checks", stage / "full-adapter/tools/check_processor_pmu.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("Processor PMU checkpoint: seven supply balls and twelve local bypass capacitors checked; remaining supplies unfinished.")
        spec = importlib.util.spec_from_file_location(
            "staged_processor_io_power_checks", stage / "full-adapter/tools/check_processor_io_power.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("Processor IO checkpoint: eleven supply balls and twelve capacitors checked; boot strap and peripheral loads unfinished.")
        spec = importlib.util.spec_from_file_location(
            "staged_processor_phy_power_checks", stage / "full-adapter/tools/check_processor_phy_power.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("Processor PHY checkpoint: active rails, filter paths and unused-domain isolation checked; all power-input balls present.")
        spec = importlib.util.spec_from_file_location(
            "staged_processor_control_checks", stage / "full-adapter/tools/check_processor_control.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("Processor control checkpoint: PMIC host, hardware straps and console endpoints checked.")
        spec = importlib.util.spec_from_file_location("staged_console_checks", stage / "full-adapter/tools/check_console.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("Console checkpoint: translator, connector, idle defaults and separated supplies checked.")
        spec = importlib.util.spec_from_file_location("staged_recovery_checks", stage / "full-adapter/tools/check_recovery.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("Recovery checkpoint: data path and separate VBUS domain checked; electrical qualification and modem endpoints unfinished.")

        spec = importlib.util.spec_from_file_location(
            "staged_processor_clock_checks", stage / "full-adapter/tools/check_processor_clock.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("Processor clock checkpoint: crystal, feedback, output damping, loads and TVSS reference checked; bench tuning pending.")

        spec = importlib.util.spec_from_file_location(
            "staged_emmc_checks", stage / "full-adapter/tools/check_emmc.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.check(stage / "full-adapter")
        print("eMMC checkpoint: 153 balls, eight data bits, rails and reset checked; sequencing qualification and system routing unfinished.")


if __name__ == "__main__":
    check()
