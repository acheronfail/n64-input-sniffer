# N64InputMod v0.16 — connector fit corrections

Use the [print-ready OrcaSlicer 3MF](../../N64InputMod-full-enclosure-v0.16-Orca-complete.3mf). It includes all 12 parts and checked G-code across three plates, using the existing Bambu Lab P1S 0.4 mm profile, 0.16 mm layers and a 0.20 mm first layer:

1. Both shells — existing PLA assignment, Supertack bed. One nut-insertion pause.
2. Eight port keepers and PCB keeper — same PLA assignment and bed. No pause.
3. Optional window — existing PETG assignment and Supertack bed. Use translucent filament if desired. No pause.

All three plates sliced successfully in OrcaSlicer 2.4.2 with no reported plate warnings. Physical printing remains unverified. Select the actual corresponding printer, bed and filament before printing; changes to the slice require rechecking the pause.

Reprint both shells and all eight port keepers. The female screw centres move outward to provide a 12.8 mm terminal passage. The male mating portion is now flat down, opposite the housing flat, and the male keepers have 0.70 mm clearance around the curved front housing lip (previously 0.22 mm). The existing base housing seat is retained. The LED window, recess and support move 6 mm inward; reuse the existing window insert and PCB keeper. The six closure nut positions and fully enclosed seats are unchanged from v0.15.

Male housings are captured by their contours and a front retaining lip around the smaller mating portion. There are **no screws into connector housings, no TPU pads, no pressure shoes, and no M3 clamp hardware**. Female keepers capture the existing flange. Connector housing positions remain those of v0.13; the board, board keeper and USB opening retain their v0.15 positions. The window alone moves 6 mm inward.

Before another full enclosure print, trial-fit a revised male keeper on the current base: its mounting holes are unchanged. The extra lip clearance is a prototype allowance and still needs checking against the real moulded connector. Female keepers now require the revised base because their screws moved outward.

## Print list

- LowerShell × 1, outside floor on the bed.
- UpperShell × 1, outside roof on the bed.
- MalePortKeeper1, 2, 3 and 4 × 1 each, flat top faces on the bed. Each has one, two, three or four small identification dimples on the rear screw bridge. They are port-specific; do not substitute four copies of one file.
- FemalePortKeeper × 4, flat top faces on the bed. All four are identical.
- BoardKeeper × 1 and optional LightWindow × 1; their shapes are unchanged and existing prints can be reused.

The supplied STL files are already bed-oriented, in millimetres at 100% scale. Use the rigid material that worked for the previous enclosure; flexible pads are no longer needed. The standalone STL files are unsliced; the companion 3MF contains verified toolpaths. Inspect the slice for bridges and support needs, especially the split front openings and recessed keeper screw holes. Do not reuse v0.12/v0.13 shell toolpaths or the historical M3 pause.

## Hardware

- Six existing **M2 × 20 mm countersunk machine screws** and six M2 nuts for case closure.
- Sixteen **2 mm nominal × 8 mm countersunk screws suitable for plastic** for the eight port keepers, two each. Keeper clearance holes are 2.2 mm, with 90-degree countersinks sized to 4.2 mm heads. Lower posts have 1.6 mm nominal printed pilot holes, 8 mm deep. Select the screw/pilot combination for the actual printed material; these are not modelled M2 metal threads. Ordinary machine screws require suitably tapped posts or another threaded fastening solution.
- Two existing normal M2 × 8 mm plastic screws for the board keeper.

The port-keeper screw heads must finish flush or below their keeper surfaces. Nominal countersunk screw length is measured including the head. An 8 mm keeper screw has approximately 6 mm of engagement below the 2 mm keeper bridge. Tighten until the keeper seats on its posts; extra torque is not needed to squeeze the connector.

## Embedded closure nuts

Only the **six M2 closure nuts** remain embedded in the upper shell. The supplied 3MF contains one native `M400 U1` pause on plate 1, before layer 88 at Z=14.12 mm. Toolpath checks confirm all six pocket caps start after the pause; plates 2 and 3 have none. At the previous 0.16 mm layer / 0.20 mm first-layer profile, roof-down orientation and Z=16 mm outside roof datum, the geometric pause target remains **before layer 88, Z=14.12 mm**. Verify it against the new slice before printing: the nut-pocket cap must not begin until the nuts are installed. Standalone STLs contain no pauses. Remove the obsolete four-M3-nut pause at layer 34.

## Assembly

1. Check that the real male mating portion agrees with the extended CAD reference: 16 mm circular diameter, flattened to 12 mm high, projecting 12 mm from the housing. The model assumes it is concentric with the housing and has its flat side down, opposite the housing's flat side (up). The 0.35 mm mating-opening clearance is per axis. Contacts are not modelled.
2. With the lower shell open, seat one male connector at a time, flat housing side up. Fit its matching keeper and two keeper screws before proceeding to the next port. Keepers 1–4 correspond to increasing CAD X: −64.04, −36.00, +36.00, +64.04 mm. The identification dimples are on the rear screw bridge, toward the wiring cavity. Viewed from the controller/female side with the case upright, this is left to right; viewed directly into the male tips, it is reversed.
3. Seat each female connector in its existing groove, fit an identical female keeper, and secure its two screws. No port should depend on the lid for retention.
4. Route wires through the spaces between the keeper posts. Fit the board and its keeper, USB toward the male connectors. Keep wiring below the moving lid and clear of screw tips.
5. With the lid still off, gently check each port for lift and movement in both axial directions. Small clearance movement is expected; no housing should escape its keeper. Confirm even console engagement and full insertion without force.
6. Install the light window if desired, lower the lid vertically, and install the six closure screws. Reopening uses only these closure screws; leave the port keepers attached.

The retaining lip surrounds the mating portion near its root, so approximately 10 mm of the measured 12 mm projection remains beyond the local case face. Verify full insertion on the real console before final wiring/assembly. Printed fit and load strength remain unverified.

## CAD and scan checks

The companion source STEP now includes the measured D-shaped mating envelope. The original housing-only STEP is preserved separately. The supplied STEP still does not model individual contacts, recesses or moulding details.

Full-resolution Top/Bottom scan triangles are checked for surface intersections, without decimation, against the shells and complete male envelopes. The console overlay is shifted +12 mm in Y relative to the historical overlay to account for the previously omitted mating projection; each scan's measured X symmetry offset is removed. This retains the historical intended tip engagement and is an explicit registration assumption. It does not measure installed socket/contact positions or certify insertion depth.

See `independent-retention-validation.json`, `console-retention-fit.json` and `mesh-validation.json` in the CAD folder for the geometric results. The supplied previews use reduced scan meshes for display only.

## Existing electrical precaution

Fully disconnect the adapter from all four console ports before connecting USB-C. Disconnect USB-C before reconnecting to the console. Turning the console off alone does not disconnect its power rail; the enclosure is not an electrical interlock.
