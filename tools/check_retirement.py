"""Repository transition check. This is deliberately not an ERC/DRC check."""
from pathlib import Path
import subprocess


def main():
    root = Path(__file__).resolve().parents[1]
    staged = subprocess.check_output(
        ["git", "ls-files", "--cached"], cwd=root, text=True
    ).splitlines()
    cad = [p for p in staged if p.endswith((".kicad_pcb", ".kicad_sch", ".kicad_pro"))]
    if cad:
        raise SystemExit(
            "BLOCKED: install current-design electrical checks before committing CAD: "
            + ", ".join(cad)
        )
    assert (root / "full-adapter/README.md").is_file()
    assert (root / "docs/legacy/README.md").is_file()
    print("Retirement integrity OK. No current CAD; ERC, parity and DRC NOT RUN.")


if __name__ == "__main__":
    main()
