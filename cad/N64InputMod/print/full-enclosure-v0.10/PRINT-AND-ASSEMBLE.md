# N64InputMod v0.10 - nuts embedded during printing

Use `N64InputMod-full-enclosure-v0.10-Orca-complete.3mf`. All 12 print parts are on three plates. Plate 1 includes the roof-down upper shell and both native Orca pause markers. The M2 side-loading slots are removed. The four M3 clamp nuts are also enclosed, separated from the shoe guides by a 0.8 mm cap with a screw passage.

## Pause sequence - plate 1

These pauses were verified by slicing in OrcaSlicer 2.4.2 at 0.16 mm layer height with a 0.20 mm first layer, no supports, and printing by layer. P1S pause command: `M400 U1`.

| Pause | Before layer | Next layer Z | Completed print height | Insert |
|---|---:|---:|---:|---|
| 1 | 34 | 5.48 mm | 5.32 mm | Four M3 nuts in the clamp pockets |
| 2 | 88 | 14.12 mm | 13.96 mm | Six M2 nuts in the enclosure-fastener pockets |

At each pause, drop the nuts into the upward-facing hexagonal pockets in the upper shell. Fully seat them below the printed rim, then resume. Do not put screws in during printing. The next layer begins closing those pockets, leaving the threaded openings accessible. The nuts cannot be inserted after printing or replaced without opening the printed pocket.

Keep the upper shell roof-down at 100% scale. If you change its orientation, layer heights, first-layer height or use adaptive layers, recheck and move the pause markers in the sliced preview before printing. Do not generate supports inside the nut pockets. The supplied profile has supports disabled; the targeted caps use short bridges over the inserted nuts.

The profile uses a P1S 0.4 mm nozzle, 0.16 mm layers, four walls and Textured PEI Plate. Choose your actual filament profiles and bed type. Rigid parts are assigned PETG, pads TPU and the window translucent PETG as placeholders. The filament purge matrix has been corrected to match the three configured filaments. No G-code is sent to a printer.

## Hardware

| Item | Quantity | Purpose |
|---|---:|---|
| Normal M2 x 8 mm screws suitable for plastic | 2 | Unchanged ESP32 keeper |
| M2 x 20 mm hex-socket flat-head screws | 6 | Enclosure closure |
| M2 nuts, 4 mm across flats, 1.6 mm thick | 6 | Embed at pause 2 |
| M3 x 8 mm hex-socket flat-head screws | 4 | Connector clamps |
| M3 nuts, 5.5 mm across flats, 2.4 mm thick | 4 | Embed at pause 1 |

The M2 pockets are 4.3 mm across flats x 2 mm high. M3 pockets are 5.8 mm across flats x 2.7 mm high. Verify that the nuts in your assortment fit these dimensions before committing to the full print. At the checked pause heights, the nominal inserted M3 nuts sit 0.16 mm below the completed rim and the M2 nuts 0.32 mm below it.

No brass inserts or tapping are needed. The two normal M2 keeper screws still thread into plastic. Flat-head seats assume 90-degree heads with nominal 4 mm (M2) and 6 mm (M3) head diameters; exact purchased screw heads have not been confirmed. Clamp heads may stand proud during adjustment—tighten for connector grip, not until the heads are flush.

## After printing

Install the board and its keeper using the normal M2 x 8 screws. Fit the connectors, route the wires, and install four soft pads and four rigid shoes. Retract the M3 adjustment screws, lower the lid and close it with six M2 x 20 flat-head screws from underneath. Adjust the M3 clamps gently. Fit the optional translucent window with adhesive around its edge as needed.

The raised ESP32 pedestal, shared USB opening, connector seats and prior support-reduction features remain. This is a geometrically checked and toolpath-checked prototype; physical print and assembly still need verification.


Rear-board-stop revision: its 1.6 mm thick wall is moved 0.8 mm away from the USB end. The low foundation extends with it to retain the connection. Board pocket length retains the 0.8 mm clearance added in v0.9.


Revision v0.10 extends the front of the enclosure by 10 mm for wiring. The female ports, board, USB opening, LED window and front fasteners move forward together; the male mating positions stay fixed. The inward tail saddles of all four male seats gain 1.25 mm of downward clearance. Both shells need reprinting for this revision.
