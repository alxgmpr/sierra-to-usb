> Historical evidence from superseded designs. See the [current full adapter](../../../../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# Buffered power envelope results

Analytical time-step model only. Taper is an approximation; efficiency and path resistance are assumed, not measured.

| Case | Available modem W | Startup to 99% (s) |
|---|---:|---:|
| nominal | 11.88 | 2.67 |
| low_line_aged | 9.39 | 1.73 |
| poor_cable_aged | 8.85 | 1.78 |

| Case | Base / peak A | Pulse ms | Result for ten bursts at 2 s intervals |
|---|---:|---:|---|
| nominal | 2.3 / 3 | 100 | No trip in model; minimum 3.914 V |
| nominal | 2.3 / 3 | 500 | No trip in model; minimum 3.901 V |
| nominal | 2.3 / 4 | 100 | No trip in model; minimum 3.869 V |
| nominal | 2.3 / 5 | 100 | No trip in model; minimum 3.775 V |
| nominal | 3 / 4 | 100 | No trip in model; minimum 3.838 V |
| low_line_aged | 2.3 / 3 | 100 | No trip in model; minimum 3.742 V |
| low_line_aged | 2.3 / 3 | 500 | UV trip at 0.4488 s |
| low_line_aged | 2.3 / 4 | 100 | UV trip at 0.0000 s |
| low_line_aged | 2.3 / 5 | 100 | UV trip at 0.0000 s |
| low_line_aged | 3 / 4 | 100 | FAIL: baseline exceeds source budget |
| poor_cable_aged | 2.3 / 3 | 100 | No trip in model; minimum 3.693 V |
| poor_cable_aged | 2.3 / 3 | 500 | UV trip at 0.1122 s |
| poor_cable_aged | 2.3 / 4 | 100 | UV trip at 0.0000 s |
| poor_cable_aged | 2.3 / 5 | 100 | UV trip at 0.0000 s |
| poor_cable_aged | 3 / 4 | 100 | FAIL: baseline exceeds source budget |
