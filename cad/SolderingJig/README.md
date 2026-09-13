# N64 soldering jig v1

A compact fixture for one male/female pair, with their wiring ends facing a central working area. The 50 × 90 mm base supports both housings on keyed seats, and two removable contour clamps prevent lift and rotation. The male clamp grips the middle flat portion, away from the curved front lip. Lower shoulders/flange grooves resist axial movement. Connector axes are 18 mm above the bench, with a 26 × 28 mm opening under the wiring area. The female rear passage is 12.8 mm wide.

[Print-ready 3MF](N64-Soldering-Jig-v1.3mf) · [FreeCAD model](N64-Soldering-Jig-v1.FCStd)

## Printing

The 3MF contains one each of `JigBase`, `MaleClamp` and `FemaleClamp`. The parts are already bed-oriented: base upright and clamps upside down, with their flat top faces on the bed. Print at 100% scale. No supports, embedded nuts or pauses are required.

The 3MF uses the current enclosure's Bambu Lab P1S 0.4 mm printer and Supertack bed profile, PLA slot 5, 0.16 mm layers, 0.20 mm first layer, three walls and 15% infill. Orca estimates 1 hour 9 minutes and 28.6 g of PLA for the complete plate; the slice reports no warnings. Confirm the selected filament matches what is loaded. Keep the soldering iron away from the plastic fixture.

## Hardware and loading

Use **four 2 mm nominal × 8 mm countersunk screws suitable for plastic**, two per clamp, as used for the enclosure's port keepers. Holes are 1.6 mm pilots, with 2.2 mm clamp clearances and 4.2 mm 90-degree head seats. The 3 mm clamp tabs leave about 5 mm of screw engagement. No nuts are needed.

1. Place the jig on the bench. The four 4.4 mm corner holes are optional bench-mounting holes; the side rails can also be held with a small bench clamp.
2. Seat the male housing flat side up in the longer saddle. Its black mating portion points outward, with its flat side down. The wiring end points into the central opening.
3. Seat the female port in the short saddle, matching the keyed lower contour and flange groove. Its mating opening faces outward and its terminals point toward the male wiring end.
4. Install the blue male clamp (one identifying dimple) and the female clamp (two dimples). Tighten their screws gently until the tabs seat on the posts. Do not use the screws to force an incorrectly oriented connector into place.
5. Solder the pair through the central working area, let the joints cool, then remove the four screws and lift out both clamps and the connected pair.

The fixture uses the supplied connector housing shapes with 0.22 mm clearance. CAD checks verify capture in all six translation directions, resistance to rolling, clamp installation clearance and unobstructed terminal approaches. Individual metal terminals and wires are not modelled. Physical fit has not yet been tested.

The FreeCAD document embeds the connector references and all three print solids. It opens without external models or scripts.

## Design changes

Edit `build.py`, then run `build.FCMacro` in FreeCAD to produce `SolderingJig.FCStd` and print meshes. See [development instructions](../DEVELOPMENT.md) for validation and 3MF generation. The versioned release files are preserved until explicitly replaced.
