# N64InputMod v0.12 — console-facing USB prototype

Use [the v0.12 OrcaSlicer project](../../N64InputMod-full-enclosure-v0.12-Orca-complete.3mf), containing all 12 parts on three plates and checked toolpaths. The Bambu Lab P1S 0.4 mm profile uses 0.16 mm layers with a 0.20 mm first layer. All three plates sliced successfully in OrcaSlicer 2.4.2 with no reported plate warnings.

- Plate 1: both shells, keeper and four rigid shoes; source PLA assignment, Supertack bed. Support generation is disabled; the USB shroud is removed.
- Plate 2: four TPU pads; Textured PEI bed (Orca rejects TPU on Supertack).
- Plate 3: optional PETG light window; Supertack bed. Use translucent filament for light transmission.

Both shells need reprinting. STL files in this folder are bed-oriented, in millimetres at 100% scale: lower shell floor down, upper shell roof down. These parts have not been physically printed or fit-tested. Use the v0.12 project: v0.11 includes the removed shroud and v0.10 has front-facing USB.

The keeper, four M3 clamp shoes, four TPU pads and optional light window retain their previous shapes and may be reused. New keeper/window STL positions are normalized for printing.

## Embedded nuts

Retain six M2 nuts for the M2 × 20 flat-head closure screws and four M3 nuts for the M3 × 8 clamp screws. The keeper uses two normal M2 × 8 plastic screws.

The supplied 3MF includes two native pauses on plate 1:

| Pause before layer | Z height | Insert |
|---|---|---|
| 34 | 5.48 mm | Four M3 nuts in the clamp pockets |
| 88 | 14.12 mm | Six M2 nuts in the enclosure screw pockets |

Seat every nut fully below the printed rim before resuming. Generated toolpaths verify all ten pocket caps begin after the appropriate pause. Recheck the pauses if you change layer height, first-layer height, orientation or geometry. Standalone STLs do not contain pause commands.

## Assembly and physical checks

1. Check the revised shells against the actual console before installing the electronics. The board remains console-facing; the shroud is removed.
2. Install the ESP component side up with USB toward the four male console plugs. Refit the keeper with its open end facing USB. The 1.5 mm additional mount inset must still allow your USB cable to seat fully with the adapter removed.
3. Fit the relocated LED window, connectors, clamp pads/shoes and enclosure hardware as in the previous assembly. Verify keeper screw heads and all wiring clear the lid. Keep capacitor leads short and insulate connections.
4. Wire DATA 1–4 to GPIO 13/12/11/10, and take ESP 3V3/GND from one console port. Connect the 470 µF capacitor positive to 3V3 and negative to GND.
5. Fully disconnect the adapter from all four console ports before connecting USB-C. Disconnect USB-C before reconnecting to the console.

Always unplug the complete adapter from all four console ports before connecting USB. Turning the console off alone does not disconnect its power rail. The rear-facing USB location and warnings are the intended precautions; the enclosure is not an electrical or mechanical interlock.
