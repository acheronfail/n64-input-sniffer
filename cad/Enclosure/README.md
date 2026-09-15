# Enclosure v1.2

**Status: verified.** The owner printed v1.2 and marked it verified on 2026-09-15.
The owner tested the retained v1.1 print on 2026-09-15.

[FreeCAD model](Enclosure-v1.2.FCStd) · [Print-ready OrcaSlicer 3MF](Enclosure-full-enclosure-v1.2-Orca-complete.3mf)

v1.2 moves the ESP board, supports, and keeper 2 mm toward the USB-C wall.
The USB-C socket face moves from Y = 6.2 mm to Y = 8.2 mm.
The USB slot and lid window stay in place.
The existing board keeper fits the moved supports.

v1.1 gives wires at least 2 mm of space between the opposing keeper screw towers.
Connector tails are 18.094 mm apart at the center ports and 19.998 mm at the outer ports.
The matching soldering jig uses an 18.1 mm gap.
Female terminal passages remain 12.8 mm wide.

The ESP window, recess, and support ledge move 4 mm toward the N64-facing edge.
They stay centered from left to right.
v1.2 adds the board move described above.

Four of the six closure bolts now sit near the N64-facing edge: CAD (X, Y) = (±18, 3) and (±79.5, 2) mm.
The remaining pair stays near the female side at (±18, −48.2) mm.
This puts more fasteners along the edge that lifted.

Hardware quantities are unchanged.
The closure bosses stay inside the original 168 mm case outline.
Local reliefs let the two outer male keepers lift past the internal side bosses.

The original [v1.0 model](Enclosure-v1.0.FCStd) and [v1.0 print project](Enclosure-full-enclosure-v1.0-Orca-complete.3mf) remain unchanged.
Physical tests of v1.0 took place on 2026-09-13.

## Printing

The 3MF includes all 12 parts and sliced toolpaths across three plates.
It uses a Bambu Lab P1S 0.4 mm profile, Supertack bed, 0.16 mm layers, and a 0.20 mm first layer.

| Plate | Parts and material | Pauses |
| --- | --- | --- |
| 1 | Lower and upper shells, PLA | One pause to insert nuts |
| 2 | Four distinct male keepers, four identical female keepers, and one board keeper, PLA | None |
| 3 | One optional light window, PETG | None |

Parts have their print orientation in millimeters at 100% scale.
The four male keepers have one through four identification dimples and each fits a specific port.

1. Select the actual printer, bed, and filament before you print.
2. If you slice the project again, check the nut pause again.

## Hardware

- Six **M2 × 20 mm countersunk machine screws** and six M2 nuts for case closure.
- Sixteen **2 mm nominal × 8 mm countersunk screws suitable for plastic** for the eight port keepers, two each.
- Two normal M2 × 8 mm plastic screws for the board keeper.

Keeper clearance holes are 2.2 mm, with 90-degree countersinks sized to 4.2 mm heads.
Lower posts have 1.6 mm nominal printed pilot holes, 8 mm deep.
Select the screw/pilot combination for the actual printed material.
These holes are not modeled M2 metal threads.
Ordinary machine screws need suitably tapped posts or another threaded fastener arrangement.

The port-keeper screw heads must finish flush or below their keeper surfaces.
Nominal countersunk screw length is measured including the head.
An 8 mm keeper screw has approximately 6 mm of engagement below the 2 mm keeper bridge.
Tighten until the keeper seats on its posts.
Extra torque is not needed to squeeze the connector.

## Embedded closure nuts

Only the **six M2 closure nuts** remain embedded in the upper shell.
The supplied 3MF contains one native `M400 U1` pause on plate 1, before layer 88 at Z=14.12 mm.
Toolpath checks show that all six pocket caps start after the pause.
Plates 2 and 3 have no pauses.

Check the pause against the new slice before you print.
The nut-pocket cap must not start until the nuts are installed.

## Check the male connector

Check the real male mating portion against the extended CAD reference:

- 16 mm circular diameter, flattened to 12 mm high
- 12 mm projection from the housing
- Concentric with the housing
- Flat side down, opposite the housing's flat side (up)

The 0.35 mm mating-opening clearance is per axis.
The model does not include contacts.

## Install the connectors

1. With the lower shell open, seat one male connector, flat housing side up.
2. Fit its matching keeper and two keeper screws before the next port.
   Keepers 1–4 correspond to increasing CAD X: −64.04, −36.00, +36.00, +64.04 mm.
   The identification dimples sit on the rear screw bridge, toward the wiring cavity.
   From the controller/female side with the case upright, the order is left to right.
   From directly in front of the male tips, the order is reversed.
3. Repeat steps 1 and 2 for each remaining male port.
4. Seat each female connector in its existing groove.
5. Fit an identical female keeper and two screws to each female connector.
   No port must depend on the lid for retention.

## Install the board and check fit

1. Route wires through the spaces between the keeper posts.
2. Fit the board and its keeper, with USB toward the male connectors.
3. Keep wiring below the moving lid and clear of screw tips.
4. With the lid still off, gently check each port for lift and movement in both axial directions.
   Small clearance movement is expected. No housing must escape its keeper.
5. Make sure the console engagement is even and permits full insertion without force.

The retaining lip surrounds the mating portion near its root.
Thus, approximately 10 mm of the measured 12 mm projection remains beyond the local case face.
Check full insertion on the real console before final wiring and assembly.
The v1.1 geometry and toolpaths passed digital checks.
The owner confirmed that the printed v1.1 enclosure works on 2026-09-15.
The owner also printed v1.2 and marked it verified on 2026-09-15.

## Close the case

1. If desired, install the light window.
2. Lower the lid vertically.
3. Install the six closure screws.

To open the case again, remove only these closure screws.
Leave the port keepers attached.

## Existing electrical precaution

Fully disconnect the adapter from all four console ports before connecting USB-C. Disconnect USB-C before reconnecting to the console. Turning the console off alone does not disconnect its power rail; the enclosure is not an electrical interlock.

## Design changes

1. Edit `parameters.json` for exposed dimensions.
2. Edit `build.py` for geometry changes.
3. Run `build.FCMacro` in FreeCAD to produce `Enclosure-v1.2.FCStd` and print meshes.

See the [development instructions](../DEVELOPMENT.md) for checks, packaging, and slicing.
The saved model parameter snapshot does not recompute the design on its own.
