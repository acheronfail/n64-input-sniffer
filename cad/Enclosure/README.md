# Enclosure v1.4

**Status: physically verified on 2026-09-25.** The owner confirmed that all changes are working well. The exact tested model and print project are retained.

 v1.4 moves the two outer closure bolts and captive nuts from (X, Y) = (±79.5, 2) to (±79.5, −13.8) mm. They are now centred along the left and right side edges. The four inner closure fasteners retain their positions. Four narrow upper-shell slots between paired connector collars are filled, joining the brittle wall pairs into continuous ribs (approximately 1.0 mm at the male row and 1.66 mm at the female row).

The verified [v1.3 model](Enclosure-v1.3.FCStd) and [v1.3 print project](Enclosure-full-enclosure-v1.3-Orca-complete.3mf) remain unchanged.

The final keepers omit the small central pad tier. The wider step, deeper cradle and reinforced front sides retain the successful fit.

[FreeCAD model](Enclosure-v1.4.FCStd) · [Full-enclosure 3MF](Enclosure-full-enclosure-v1.4-Orca-complete.3mf)

Like v1.3, this enclosure uses the male connector's inner body after its outer moulded housing is removed.
The enclosure is 15.5 mm shallower than v1.2: approximately 58.1 mm instead of 73.6 mm over the curved shell (21% less depth).
Its width and 32 mm height are unchanged. The female connector seats and their closure screws move 15.5 mm toward the console.
The male port axes, board, USB socket, and LED window keep their v1.2 positions.
The new male seats and individual keepers capture the smaller D-shaped body.
Each male keeper now uses the existing wider internal step. The additional 10 × 6.5 mm central tier, projecting approximately 2.1–2.2 mm, is removed.
The nominal smooth connector model does not predict the real cover contact accurately; the owner’s trimmed-part test establishes the successful single-port fit and clamping pressure.

The measured male body is an 18.5 mm diameter circle clipped to 14.3 mm from its flat to the opposite arc.
Its axial length is 18 mm from the plug shoulder to the back; the 29.9 mm total length leaves an 11.9 mm mating projection.
The body flat faces up. The mating cross-section and concentric alignment use the inherited reference geometry; the v1.3 enclosure was tested with the owner’s stripped connectors.
Two generous side-tab insertion pockets and a 7 mm-long keeper relief accommodate the features found during the first physical test.
The 7 mm relief covers the measured 6.5 mm section behind the plug shoulder with 0.5 mm extra axial clearance.
The tabs use clearance envelopes inferred from the photographs, not exact measured shapes.
The keeper top is solid; its former square material-saving recess has been filled. The front relief is now an internal 22.8 mm-wide pocket, with 1.9 mm side walls joining the front face to the keeper. Its 7 mm axial clearance remains.
The lower cradle alone has 1.5 mm extra depth; the plug opening, side-tab pockets, and screws stay at their tested positions. The small pad tier is omitted.

The closest male/female bodies remain approximately 18.1 mm apart.
Opposing keeper towers retain at least 2 mm of wiring space.
The [v1.3 soldering jig](../SolderingJig/README.md) models the stripped male body and was also marked verified by the owner on 2026-09-25.
The old jig fits the full outer housing and is not a fit reference for this revision.

The six closure screws are at CAD (X, Y) = (±18, −32.7), (±18, 3), and (±79.5, −13.8) mm.
Hardware quantities are unchanged. The board keeper, female keepers, and light window retain their previous shapes.
The four new male keepers are numbered by port.

The physically verified [v1.2 model](Enclosure-v1.2.FCStd) and [v1.2 print project](Enclosure-full-enclosure-v1.2-Orca-complete.3mf) remain available unchanged, along with v1.0 and v1.1.
v1.3 has its own successful physical test dated 2026-09-25.

## Fit-test development files

Intermediate fit-test models and print projects were removed after the successful full print. The source scripts can regenerate a compact fixture, a keeper-only plate or the four-port gauge; see [development instructions](../DEVELOPMENT.md).

## Printing

The final gap-fill change affects only the upper shell compared with the first v1.4 prototype. The reinforced version is the retained, verified release.

To update a printed v1.3 enclosure, reprint **LowerShell, UpperShell, MalePortKeeper1 and MalePortKeeper4**. The two outer keepers need their new local clearance notches. Reuse male keepers 2–3, all female keepers, the board keeper and light window. The complete 3MF still contains all parts; select only the required objects when reusing parts.

The 3MF includes all 12 parts and sliced toolpaths across three plates.
It uses a Bambu Lab P1S 0.4 mm profile, Supertack bed, 0.16 mm layers, and a 0.20 mm first layer.

| Plate | Parts and material | Pauses |
| --- | --- | --- |
| 1 | Lower and upper shells, PLA | One pause to insert nuts |
| 2 | Four distinct male keepers, four identical female keepers, and one board keeper, PLA | None |
| 3 | One optional light window, PETG | None |

The saved profile estimates **5 h 37 min and 130.1 g PLA** for the shells and keepers together. The optional PETG window adds about 9 minutes and 0.8 g.

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
Check that the wider keeper step holds the cover when the keeper seats; extra torque cannot correct a contact gap.

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
- 11.9 mm projection from the stripped body
- Concentric with the housing
- Flat side down, opposite the stripped body's flat side (up)

The 0.35 mm mating-opening clearance is per axis.
The model does not include contacts.

## Install the connectors

1. Remove the male connector’s outer moulded housing without damaging the inner body or wires.
   Check that the exposed body matches the dimensions above, including any remaining tabs.
   With the lower shell open, seat it with the body flat side up.
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
Thus, approximately 9.9 mm of the 11.9 mm projection remains beyond the local case face.
The optional `RearAlignmentGauge.stl` can be regenerated and paired with the four keepers; it is not on the three full-enclosure plates.
Check seating, clearance around any tabs, retention in both axial directions, and full insertion on the real console before final wiring and assembly.
These checks passed on the owner’s complete v1.4 print. Repeat them after changes or when using different connector samples.

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
3. Run `build.FCMacro` in FreeCAD to produce `Enclosure-v1.4.FCStd` and print meshes.

See the [development instructions](../DEVELOPMENT.md) for checks, packaging, and slicing.
The saved model parameter snapshot does not recompute the design on its own.
