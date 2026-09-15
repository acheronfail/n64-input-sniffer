# N64 soldering jig v1.1

This compact fixture holds one male/female pair with their wiring ends toward a central work area.
The 50 × 80.1 mm base supports both housings on keyed seats.
Two removable contour clamps prevent lift and rotation.
The male clamp grips the middle flat portion, away from the curved front lip.
Lower shoulders and flange grooves resist axial movement.

Connector axes are 18 mm above the bench.
A 26 × 18.1 mm opening sits under the wiring area.
The female rear passage is 12.8 mm wide.

[Print-ready 3MF](N64-Soldering-Jig-v1.1.3mf) · [FreeCAD model](N64-Soldering-Jig-v1.1.FCStd)

## Printing

The 3MF contains one each of `JigBase`, `MaleClamp`, and `FemaleClamp`.
The parts already have their print orientation: base upright and clamps upside down, with their flat top faces on the bed.
Print at 100% scale.
The parts need no supports, embedded nuts, or pauses.

The 3MF uses the current enclosure's Bambu Lab P1S 0.4 mm printer and Supertack bed profile.
It uses PLA slot 5, 0.16 mm layers, a 0.20 mm first layer, three walls, and 15% infill.
Make sure the selected filament matches the loaded filament.
Keep the soldering iron away from the plastic fixture.

## Hardware

Use **four 2 mm nominal × 8 mm countersunk screws suitable for plastic**, two per clamp.
The enclosure's port keepers use the same screws.
Holes are 1.6 mm pilots, with 2.2 mm clamp clearances and 4.2 mm 90-degree head seats.
The 3 mm clamp tabs leave about 5 mm of screw engagement.
The clamps need no nuts.

## Load the connectors

1. Place the jig on the bench.
   The four 4.4 mm corner holes are optional bench mounts.
   A small bench clamp can also hold the side rails.
2. Seat the male housing flat side up in the longer saddle.
   Its black mating portion points outward, with its flat side down.
   The wiring end points into the central opening.
3. Seat the female port in the short saddle to match the keyed lower contour and flange groove.
   Its mating opening faces outward. Its terminals point toward the male wiring end.
4. Install the blue male clamp (one identification dimple) and the female clamp (two dimples).
5. Tighten their screws gently until the tabs seat on the posts.
   Do not use the screws to force an incorrectly oriented connector into place.

## Solder and remove the pair

1. Solder the pair through the central work area.
2. Let the joints cool.
3. Remove the four screws.
4. Lift both clamps and the connected pair out of the jig.

## Fit and model details

The fixture uses the supplied connector housing shapes with 0.22 mm clearance.
CAD checks cover retention in all six translation directions, resistance to rolling, clamp installation clearance, and clear paths to the terminals.
The model does not include individual metal terminals or wires.
**Status: verified.** The owner printed v1.1 and confirmed that it works on 2026-09-15.

The FreeCAD document embeds the connector references and all three print solids.
It opens without external models or scripts.

The 18.1 mm connector gap matches enclosure v1.1, which leaves at least 2 mm between its opposing keeper towers.
The original [v1 model](N64-Soldering-Jig-v1.FCStd) and [v1 print project](N64-Soldering-Jig-v1.3mf) remain unchanged.

## Design changes

1. Edit `build.py`.
2. Run `build.FCMacro` in FreeCAD to produce `N64-Soldering-Jig-v1.1.FCStd` and print meshes.

See the [development instructions](../DEVELOPMENT.md) for checks and 3MF generation.
The versioned release files remain unchanged until an explicit replacement.
