# Remove LED-kill Gate + DIP Switches Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Delete the killable-LED power gate (SW2/Q33/Q35/R82/R84) and config DIP bank (SW1/R88–R91) from the schematic; rewire all `LED_PWR` consumers to `+3V3`; NC the freed RP2040 pins; keep every gate green.

**Architecture:** TDD against the project's connectivity checker — rewrite `tools/netchecks.txt` to the post-removal state first (RED), then edit the three sheets until `check_nets.py` + ERC pass (GREEN). The mcu-sheet surgery is one Python script driven by two bounding boxes that contain the doomed clusters and nothing else; it aborts if it finds any object it doesn't expect.

**Tech Stack:** KiCad 10 s-expression files, `uv run` Python, `kicad-cli` at `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` (KCLI below).

**Spec:** `docs/superpowers/specs/2026-07-19-remove-led-kill-dip-design.md`

## Global Constraints

- KiCad GUI must be fully quit before any file edit (project directive; GUI saves have clobbered sheets 3×).
- Netlist export is the ONLY connectivity ground truth — never reason from coordinates for verification (coordinates are used only to *select* objects for deletion; verification is netlist/ERC).
- Every commit must pass the pre-commit hook (check_nets + friends). No `--no-verify` on schematic commits.
- Do not push to the remote. Do not touch `sierra-to-usb.kicad_pcb` beyond Task 1's snapshot (footprint removal happens at the user's next F8 sync).
- Keep resource usage light: serialize kicad-cli invocations, no parallel agent fan-outs.
- Scratchpad dir (SCRATCH below): `/private/tmp/claude-501/-Users-alex-sierra-to-usb/b3ac2763-ab0f-4b1c-b2d0-0d988ce10fc2/scratchpad`
- Baseline netlist already exported: `SCRATCH/pre-simplify.net`.

## Netlist-verified facts (2026-07-19, do not re-derive)

- `DIP0`: R88.1, SW1.1, U24.31 · `DIP1`: R89.1, SW1.2, U24.32 · `DIP2`: R91.1, SW1.3, U24.34 · `DIP3`: R90.2, SW1.4, U24.35
- `LED_EN_CTL`: Q35.1, R84.1, U24.12 · `/MCU/N_LEDKILL_GATE`: Q33.1, R82.1, SW2.2 · `/MCU/N_SW2_KILL`: Q35.3, SW2.1
- `LED_PWR`: C77.1, Q33.3, R120.1, R121.1, R67.1, U28.2 (Q33 source is `+3V3`, so `+3V3` is the drop-in replacement rail)
- All rail attachments in the doomed clusters are **global labels** (`+3V3`, `+3V3_MCU`), except two `power:GND` symbols at (266.7, 182.88) [Q35 source] and (387.35, 152.4) [SW1 common chain].

---

### Task 1: Quit KiCad and snapshot the user's in-progress work

The working tree has the user's uncommitted layout/schematic session across all 9 sheets + board files + new untracked `lib/` assets. Snapshot it as its own commit so the removal diff is clean and revertible.

**Files:**
- Modify: none (git only)

**Interfaces:**
- Produces: a green baseline commit; later tasks diff against it.

- [ ] **Step 1: Quit KiCad**

```bash
pgrep -fl kicad || echo "not running"
osascript -e 'quit app "KiCad"' 2>/dev/null; sleep 5
pgrep -fl kicad && echo "STILL RUNNING - STOP" || echo "kicad closed"
```

If still running after a second attempt (likely an unsaved-changes dialog), **stop and ask the user** — do not kill -9.

- [ ] **Step 2: Verify baseline gates pass on the user's tree**

```bash
uv run tools/check_nets.py
KCLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$KCLI sch erc -o "$SCRATCH/erc-baseline.rpt" --severity-error --exit-code-violations sierra-to-usb.kicad_sch && echo ERC-OK
```

Expected: check_nets exit 0; `ERC-OK`. If either fails, **stop and report** — the user's session left a broken state and they must decide (this happened before with usb3_data; do not auto-fix their work).

- [ ] **Step 3: Snapshot commit**

```bash
git add -A
git commit -m "sch/pcb: user session snapshot before LED-kill/DIP removal

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: pre-commit hook passes, commit created. If the hook fails, stop and report.

---

### Task 2: RED — rewrite netchecks.txt to the post-removal state

**Files:**
- Modify: `tools/netchecks.txt`

**Interfaces:**
- Produces: assertion file that Task 3's schematic edits must satisfy. New invariants: `R67.1 = +3V3`, `R120.1 = +3V3`, `R121.1 = +3V3`, `U28.pinfn:VDD = +3V3`, `C77.1 = +3V3`; all SW1/SW2/Q33/Q35/R82/R84/R88/DIP/LED_PWR/LED_EN_CTL/N_LEDKILL_GATE/N_SW2_KILL assertions gone.

All edits are content-anchored (exact strings, not line numbers). Apply with the Edit tool:

- [ ] **Step 1: m2 WWAN LED** — replace `R67.1 = LED_PWR` with `R67.1 = +3V3`. In the comment block above it, replace `LED_PWR is` with `+3V3 is (kill gate removed 2026-07-19; was LED_PWR)` — keep the rest of the comment.

- [ ] **Step 2: usb3_data-section strays** — delete the two lines `SW1.1 = DIP0` and `Q33.pinfn:G = N_LEDKILL_GATE` (they sit together after `U25.pinfn:DO/IO_{1} = QSPI_SD1`).

- [ ] **Step 3: GPIO map** — delete these 5 lines from the `mcu -- full GPIO map` block:

```
U24.pinfn:GPIO9 = LED_EN_CTL
U24.pinfn:GPIO20 = DIP0
U24.pinfn:GPIO21 = DIP1
U24.pinfn:GPIO22 = DIP2
U24.pinfn:GPIO23 = DIP3
```

(GPIO9 appears once here and once in the LED-kill block — both go; the map's copy is the one directly under `U24.pinfn:GPIO8 = VBUSSNS_CTL`.)

- [ ] **Step 4: LED-kill block** — delete the entire block: the comment starting `# mcu -- LED-kill rail-to-rail gate network` through `NET LED_EN_CTL PINS>=3` inclusive (comment lines + 15 assertion lines: Q33.pinfn:S/D/G, SW2.pinfn:B/A, R82.1/.2, Q35.pinfn:D/S/G, R84.1/.2, U24.pinfn:GPIO9, NET N_LEDKILL_GATE, NET LED_EN_CTL). Replace with:

```
# mcu -- LED-kill gate REMOVED 2026-07-19 (spec: docs/superpowers/specs/
# 2026-07-19-remove-led-kill-dip-design.md). LEDs hardwired always-on to
# +3V3; GP9 freed (NC).
```

- [ ] **Step 5: RGB block** — replace `U28.pinfn:VDD = LED_PWR` with:

```
U28.pinfn:VDD = +3V3
C77.1 = +3V3
```

In its comment, replace `powered from LED_PWR, not +3V3_MCU` with `powered from +3V3 (kill gate removed 2026-07-19)`.

- [ ] **Step 6: DIP bank** — delete the three lines `R88.1 = DIP0`, `R88.2 = +3V3_MCU`, `SW1.8 = GND`; change the section comment `# mcu -- DIP0-3 pull-ups + spare header + SWD + Qwiic` to `# mcu -- spare header + SWD + Qwiic (DIP bank removed 2026-07-19)`.

- [ ] **Step 7: Net size floors** — delete both lines `NET LED_PWR PINS>=2` and `NET LED_PWR PINS>=4`.

- [ ] **Step 8: power_input LEDs** — replace `R120.1 = LED_PWR` with `R120.1 = +3V3` and `R121.1 = LED_PWR` with `R121.1 = +3V3`.

- [ ] **Step 9: Run checker, verify RED with exactly the expected failures**

```bash
uv run tools/check_nets.py; echo "exit=$?"
```

Expected: exit 1 with exactly 5 failures — `R67.1` expected `+3V3` got `LED_PWR`; `R120.1` ditto; `R121.1` ditto; `U28` VDD ditto; `C77.1` ditto. Any OTHER failure (e.g. a `+3V3_MCU PINS>=` floor) means a missed edit — fix before proceeding. Do NOT commit (tree is intentionally red).

---

### Task 3: GREEN — schematic surgery, gates back to green, commit

**Files:**
- Modify: `sheets/mcu.kicad_sch` (scripted), `sheets/m2.kicad_sch`, `sheets/power_input.kicad_sch` (Edit tool)
- Create: `$SCRATCH/mcu_surgery.py` (scratchpad only, not committed)

**Interfaces:**
- Consumes: Task 2's netchecks.txt as the acceptance test.
- Produces: green tree, single commit with sheets + netchecks.

- [ ] **Step 1: m2 + power_input label renames (Edit tool)**

In `sheets/m2.kicad_sch`: exactly 1 occurrence of `(global_label "LED_PWR"` → `(global_label "+3V3"`.
In `sheets/power_input.kicad_sch`: exactly 2 occurrences (replace_all) of `(global_label "LED_PWR"` → `(global_label "+3V3"`.
Then check for stale prose: `grep -n LED_PWR sheets/m2.kicad_sch sheets/power_input.kicad_sch` — any remaining hits are `(text` notes; update their wording to `+3V3` via Edit.

- [ ] **Step 2: Write the mcu surgery script**

Write to `$SCRATCH/mcu_surgery.py`:

```python
#!/usr/bin/env python3
"""Remove LED-kill gate + DIP bank from sheets/mcu.kicad_sch.

Selection is geometric (two boxes that contain the doomed clusters and
nothing else) with a whitelist abort; verification is netlist/ERC later.
"""
import re, sys, uuid
from pathlib import Path

SCH = Path("sheets/mcu.kicad_sch")
BOX_A = (198.0, 133.0, 275.0, 196.0)   # LED-kill: SW2 Q33 Q35 R82 R84 + GND@266.7,182.88
BOX_B = (330.0, 128.0, 395.0, 172.0)   # DIP bank: SW1 R88-R91 + GND@387.35,152.4
OK_REFS = {"SW1","SW2","Q33","Q35","R82","R84","R88","R89","R90","R91"}
OK_LABELS = {"LED_EN_CTL","DIP0","DIP1","DIP2","DIP3","LED_PWR","+3V3","+3V3_MCU",
             "N_LEDKILL_GATE","N_SW2_KILL"}
# U24 pins to convert label -> no_connect (label anchor == pin position)
NC_POINTS = [(175.26,85.09),(175.26,113.03),(175.26,115.57),(175.26,118.11),(175.26,120.65)]
RENAME_POINTS = {(295.91,134.62),(311.15,138.43)}   # U28 VDD, C77 top: LED_PWR -> +3V3

def top_level_objects(txt):
    """Yield (start, end) spans of depth-1 children of (kicad_sch ...), string-aware."""
    depth = 0; in_str = False; esc = False; start = None
    for i, ch in enumerate(txt):
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': in_str = False
            continue
        if ch == '"': in_str = True
        elif ch == "(":
            depth += 1
            if depth == 2: start = i
        elif ch == ")":
            if depth == 2 and start is not None:
                yield (start, i + 1); start = None
            depth -= 1

def anchor_points(obj):
    """All coordinate anchors: first (at x y) for most objects, both (xy ...) for wires."""
    if obj.lstrip("(").split(None,1)[0] == "wire":
        return [(float(a),float(b)) for a,b in re.findall(r"\(xy ([\d.-]+) ([\d.-]+)\)", obj)]
    m = re.search(r"\(at ([\d.-]+) ([\d.-]+)", obj)
    return [(float(m.group(1)), float(m.group(2)))] if m else []

def in_box(p, box):
    return box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]

txt = SCH.read_text()
out, deleted, ncs = [], [], []
tail_prev = 0
head_end = None
for (s, e) in top_level_objects(txt):
    if head_end is None:
        head_end = s
        out.append(txt[:s])
    else:
        out.append(txt[tail_prev:s])
    tail_prev = e
    obj = txt[s:e]
    kind = obj.lstrip("(").split(None, 1)[0]
    pts = anchor_points(obj)
    boxed = any(in_box(p, BOX_A) or in_box(p, BOX_B) for p in pts)
    name = (re.search(r'\((?:global_label|label) "([^"]+)"', obj) or [None,None])[1] \
           if kind in ("global_label","label") else None
    ref = (re.search(r'\(property "Reference" "([^"]+)"', obj) or [None,None])[1] \
          if kind == "symbol" else None

    if boxed and kind in ("symbol","wire","junction","label","global_label","no_connect"):
        if kind == "symbol" and "power:" not in obj and ref not in OK_REFS:
            sys.exit(f"ABORT: unexpected symbol {ref} in box — refine boxes")
        if kind in ("label","global_label") and name not in OK_LABELS:
            sys.exit(f"ABORT: unexpected label {name} in box — refine boxes")
        deleted.append(f"{kind} {ref or name or ''} @ {pts}")
        continue
    if kind == "global_label" and pts and (round(pts[0][0],2),round(pts[0][1],2)) in \
       {(round(x,2),round(y,2)) for x,y in NC_POINTS} and name in OK_LABELS:
        ncs.append(pts[0]); deleted.append(f"global_label {name} -> no_connect @ {pts[0]}")
        continue
    if kind == "global_label" and name == "LED_PWR" and pts and \
       (round(pts[0][0],2),round(pts[0][1],2)) in {(round(x,2),round(y,2)) for x,y in RENAME_POINTS}:
        obj = obj.replace('(global_label "LED_PWR"', '(global_label "+3V3"', 1)
        deleted.append(f"RENAMED LED_PWR->+3V3 @ {pts[0]}")
    if kind == "text":
        tm = re.search(r'\(text "((?:[^"\\]|\\.)*)"', obj)
        body = tm.group(1) if tm else ""
        if body.startswith("SW1 DIP-4 ->") or body.startswith("LED-kill gate logic"):
            deleted.append(f"text note: {body[:50]}...")
            continue
        if "LED_PWR" in body:
            obj = obj.replace("LED_PWR (killable 3.3V rail)", "+3V3 (kill gate removed 2026-07-19)")
            obj = obj.replace("LED_PWR", "+3V3")
            deleted.append("text note LED_PWR wording updated")
    out.append(obj)

nc_blocks = "".join(
    f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n' for x, y in ncs)
final = "".join(out) + nc_blocks + txt[tail_prev:]
if len(ncs) != 5:
    sys.exit(f"ABORT: expected 5 NC conversions, got {len(ncs)}")
SCH.write_text(final)
print(f"{len(deleted)} operations:"); [print(" ", d) for d in deleted]
```

- [ ] **Step 3: Run it and audit the log**

```bash
cd /Users/alex/sierra-to-usb && uv run python "$SCRATCH/mcu_surgery.py"
```

Expected operation log (audit every line): 12 symbols (SW1, SW2, Q33, Q35, R82, R84, R88, R89, R90, R91, 2× power:GND), 12 wires, 4 junctions, 5 local labels (3× N_LEDKILL_GATE, 2× N_SW2_KILL), ~14–17 in-box global labels (2× LED_EN_CTL, 2 ea. DIP0–3, 1× LED_PWR, 2× +3V3, 2–5× +3V3_MCU — the R89/R90/R91 free-pin rail labels are swept by box B), 5 label→no_connect conversions, 2 LED_PWR→+3V3 renames, 2 text notes deleted, ≤1 text wording update. Anything else in the log, or an ABORT: **stop, `git checkout sheets/mcu.kicad_sch`, investigate, adjust script.**

- [ ] **Step 4: check_nets GREEN**

```bash
uv run tools/check_nets.py && echo GREEN
```

Expected: `GREEN` (exit 0). If failures remain, diagnose from the message (each names the pin, expected, and actual net) — do not loosen assertions to pass.

- [ ] **Step 5: ERC = 0**

```bash
KCLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$KCLI sch erc -o "$SCRATCH/erc-post.rpt" --severity-error --exit-code-violations sierra-to-usb.kicad_sch && echo ERC-OK || cat "$SCRATCH/erc-post.rpt"
```

Expected: `ERC-OK`. If violations: the report lists coordinates — typically a dangling straggler the boxes missed; delete that object by coordinate (extend the script's boxes or Edit by hand), re-run Steps 4–5.

- [ ] **Step 6: Netlist double-check (independent of check_nets)**

```bash
$KCLI sch export netlist -o "$SCRATCH/post-simplify.net" sierra-to-usb.kicad_sch
uv run python - <<'EOF'
import re, sys
txt = open("/private/tmp/claude-501/-Users-alex-sierra-to-usb/b3ac2763-ab0f-4b1c-b2d0-0d988ce10fc2/scratchpad/post-simplify.net").read()
dead_nets = ["DIP0","DIP1","DIP2","DIP3","LED_PWR","LED_EN_CTL","N_LEDKILL_GATE","N_SW2_KILL"]
bad = [n for n in dead_nets if re.search(r'\(name "[^"]*%s"\)' % n, txt)]
dead_refs = ["SW1","SW2","Q33","Q35","R82","R84","R88","R89","R90","R91"]
bad += [r for r in dead_refs if '(ref "%s")' % r in txt]
blocks = re.split(r"\(net\b", txt)
p3v3 = next(b for b in blocks if '(name "+3V3")' in b)
need = ["R67","R120","R121","U28","C77"]
missing = [r for r in need if '(ref "%s")' % r not in p3v3]
print("FAIL", bad, missing) if bad or missing else print("NETLIST-OK")
sys.exit(1 if bad or missing else 0)
EOF
```

Expected: `NETLIST-OK`.

- [ ] **Step 7: Commit (hook is the final gate)**

```bash
git add sheets/mcu.kicad_sch sheets/m2.kicad_sch sheets/power_input.kicad_sch tools/netchecks.txt
git commit -m "sch: remove LED-kill gate + DIP bank, LEDs hardwired to +3V3

SW2/Q33/Q35/R82/R84 and SW1/R88-R91 deleted; LED_PWR consumers
(R67, R120, R121, U28, C77) rewired to +3V3; GP9 + GP20-23 NC'd.
Spec: docs/superpowers/specs/2026-07-19-remove-led-kill-dip-design.md

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: hook passes, commit created. Hook failure = a checker the plan missed; read its output, fix, re-commit. Never `--no-verify`.

---

### Task 4: Docs, memory, and handoff notes

**Files:**
- Modify: `docs/superpowers/specs/2026-07-19-remove-led-kill-dip-design.md`
- Modify: `/Users/alex/.claude/projects/-Users-alex-sierra-to-usb/memory/universal-m2-carrier.md`

**Interfaces:** none downstream.

- [ ] **Step 1: Fix the spec's pin typo** — the netchecks file (checker-verified) has `R121.1` on LED_PWR / `R121.2` on N_D30_A; the spec's table says R121.2. Edit the spec row to `R121.1 on LED_PWR → R121.1 → +3V3`.

- [ ] **Step 2: Update project memory** — in `universal-m2-carrier.md`: (a) replace the `LED_EN_CTL is ACTIVE-LOW kill` clause with a note that the LED-kill gate and DIP bank were removed 2026-07-19 (LEDs hardwired to +3V3; GP9/GP20–23 NC; task-9 GPIO map superseded for those pins); (b) note the F8 re-sync now also drops SW1/SW2/Q33/Q35/R82/R84/R88–R91 footprints from the board, on top of the pending J1 SS rebind.

- [ ] **Step 3: Commit docs**

```bash
git add docs/superpowers/specs/2026-07-19-remove-led-kill-dip-design.md
git commit -m "docs: spec pin fix (R121.1) post-implementation

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 4: Final report to user** must include: what was removed, the two commits, and the standing reminder — **next KiCad session: re-run F8 with the green schematic** (rebinds J1 SS pads AND removes the 10 dead footprints; the parked footprints for deleted parts will vanish from the parking lot).

## Self-Review (done at planning time)

- Spec coverage: removal list → Task 3 Step 2/3; rewiring table → Steps 1–3 + netchecks Task 2; NC flags → NC_POINTS; gates → Steps 4–7; out-of-scope (SW3/SW4/board) → untouched by boxes (SW3 at (59.69,~47), SW4 at (59.69,~110), both far outside boxes A/B; board file never opened).
- No placeholders: every step has exact strings, code, or commands.
- Consistency: `R121.1` used throughout (netchecks is authority; spec typo fixed in Task 4); NC coordinates match the label-anchor==pin-position fact verified 2026-07-19.
