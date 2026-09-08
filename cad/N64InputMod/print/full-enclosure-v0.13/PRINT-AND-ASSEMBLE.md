# N64InputMod v0.13 — measured outer male spacing

Reprint **both LowerShell and UpperShell**. The outer male mounts move 0.34 mm outward per side (X = ±64.04 mm); the inner mounts remain at ±36.00 mm. The outer centre span increases from 127.40 to 128.08 mm. Connector depths/heights and female seats are unchanged. Shoes, pads, keeper and window retain their shapes and may be reused.

STLs are bed-oriented, in millimetres at 100% scale: lower shell floor down, upper shell roof down. Use the material and settings from your v0.12 print. This package contains unsliced STLs; replace both shells in your slicer and re-slice. **The v0.12 3MF still contains the old spacing.**

Both original full-resolution shell scans independently support the correction. Measurements describe shell apertures, not installed electrical sockets. Test gentle, even engagement on your console before final assembly; do not force the connectors. An optional matched RearAlignmentGauge / RearAlignmentGaugeUpper pair is available in the parent CAD folder for a smaller fit print.

## Embedded nuts

Retain six M2 nuts for the M2 × 20 flat-head closure screws and four M3 nuts for the M3 × 8 clamp screws. The keeper uses two normal M2 × 8 plastic screws.

For the original 0.16 mm layer / 0.20 mm first-layer profile and roof-down upper shell, retain these nut-insertion pauses when re-slicing:

| Pause before layer | Z height | Insert |
|---|---|---|
| 34 | 5.48 mm | Four M3 nuts in the clamp pockets |
| 88 | 14.12 mm | Six M2 nuts in the enclosure screw pockets |

Seat every nut fully below the printed rim before resuming. Check the new slice preview to confirm all ten pocket caps begin after the appropriate pause. Recheck the pauses if you change layer height, first-layer height, orientation or geometry. Standalone STLs do not contain pause commands.

## Assembly and physical checks

1. Check the revised shells against the actual console before installing the electronics. The board remains console-facing; the shroud is removed.
2. Install the ESP component side up with USB toward the four male console plugs. Refit the keeper with its open end facing USB. The 1.5 mm additional mount inset must still allow your USB cable to seat fully with the adapter removed.
3. Fit the relocated LED window, connectors, clamp pads/shoes and enclosure hardware as in the previous assembly. Verify keeper screw heads and all wiring clear the lid. Keep capacitor leads short and insulate connections.
4. Wire DATA 1–4 to GPIO 13/12/11/10, and take ESP 3V3/GND from one console port. Connect the 470 µF capacitor positive to 3V3 and negative to GND.
5. Fully disconnect the adapter from all four console ports before connecting USB-C. Disconnect USB-C before reconnecting to the console.

Always unplug the complete adapter from all four console ports before connecting USB. Turning the console off alone does not disconnect its power rail. The rear-facing USB location and warnings are the intended precautions; the enclosure is not an electrical or mechanical interlock.
