# Enclosure v1.0

[FreeCAD model](Enclosure-v1.0.FCStd) · [Print-ready OrcaSlicer 3MF](Enclosure-full-enclosure-v1.0-Orca-complete.3mf)

This is the tested v0.16 enclosure, renamed to v1.0 with identical file contents. Physical testing was confirmed by the owner on 2026-09-13. Local slicer changes only rearranged which pieces were printed and their order; this release retains the original saved print project.

## Printing

The 3MF includes all 12 parts and sliced toolpaths across three plates using a Bambu Lab P1S 0.4 mm profile, Supertack bed, 0.16 mm layers and a 0.20 mm first layer:

1. Lower and upper shells, PLA. One nut-insertion pause.
2. Four distinct male keepers, four identical female keepers and one board keeper, PLA. No pauses.
3. One optional light window, PETG. No pauses.

Parts are bed-oriented in millimetres at 100% scale. Select the actual printer, bed and filament before printing; recheck the nut pause if reslicing. The four male keepers have one through four identification dimples and are port-specific.

## Hardware

- Six **M2 × 20 mm countersunk machine screws** and six M2 nuts for case closure.
- Sixteen **2 mm nominal × 8 mm countersunk screws suitable for plastic** for the eight port keepers, two each. Keeper clearance holes are 2.2 mm, with 90-degree countersinks sized to 4.2 mm heads. Lower posts have 1.6 mm nominal printed pilot holes, 8 mm deep. Select the screw/pilot combination for the actual printed material; these are not modelled M2 metal threads. Ordinary machine screws require suitably tapped posts or another threaded fastening solution.
- Two normal M2 × 8 mm plastic screws for the board keeper.

The port-keeper screw heads must finish flush or below their keeper surfaces. Nominal countersunk screw length is measured including the head. An 8 mm keeper screw has approximately 6 mm of engagement below the 2 mm keeper bridge. Tighten until the keeper seats on its posts; extra torque is not needed to squeeze the connector.

## Embedded closure nuts

Only the **six M2 closure nuts** remain embedded in the upper shell. The supplied 3MF contains one native `M400 U1` pause on plate 1, before layer 88 at Z=14.12 mm. Toolpath checks confirm all six pocket caps start after the pause; plates 2 and 3 have none. Verify it against the new slice before printing: the nut-pocket cap must not begin until the nuts are installed.

## Assembly

1. Check that the real male mating portion agrees with the extended CAD reference: 16 mm circular diameter, flattened to 12 mm high, projecting 12 mm from the housing. The model assumes it is concentric with the housing and has its flat side down, opposite the housing's flat side (up). The 0.35 mm mating-opening clearance is per axis. Contacts are not modelled.
2. With the lower shell open, seat one male connector at a time, flat housing side up. Fit its matching keeper and two keeper screws before proceeding to the next port. Keepers 1–4 correspond to increasing CAD X: −64.04, −36.00, +36.00, +64.04 mm. The identification dimples are on the rear screw bridge, toward the wiring cavity. Viewed from the controller/female side with the case upright, this is left to right; viewed directly into the male tips, it is reversed.
3. Seat each female connector in its existing groove, fit an identical female keeper, and secure its two screws. No port should depend on the lid for retention.
4. Route wires through the spaces between the keeper posts. Fit the board and its keeper, USB toward the male connectors. Keep wiring below the moving lid and clear of screw tips.
5. With the lid still off, gently check each port for lift and movement in both axial directions. Small clearance movement is expected; no housing should escape its keeper. Confirm even console engagement and full insertion without force.
6. Install the light window if desired, lower the lid vertically, and install the six closure screws. Reopening uses only these closure screws; leave the port keepers attached.

The retaining lip surrounds the mating portion near its root, so approximately 10 mm of the measured 12 mm projection remains beyond the local case face. Verify full insertion on the real console before final wiring/assembly. The owner confirmed successful physical testing on 2026-09-13; no instrumented load-strength measurements were recorded.

## Existing electrical precaution

Fully disconnect the adapter from all four console ports before connecting USB-C. Disconnect USB-C before reconnecting to the console. Turning the console off alone does not disconnect its power rail; the enclosure is not an electrical interlock.

## Design changes

Edit `parameters.json` for exposed dimensions and `build.py` for geometry changes. Run `build.FCMacro` in FreeCAD to produce `Enclosure.FCStd` and print meshes. See [development instructions](../DEVELOPMENT.md) for checks, packaging and slicing. The saved model parameter snapshot does not recompute the design on its own.
