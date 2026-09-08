# N64InputMod — fit prototype v0.1

Open **N64InputMod.FCStd** in FreeCAD. The model includes the two enclosure halves, the optional translucent LED window, eight connector envelopes, the ESP32 envelope, construction stages, fit coupons, and aligned lightweight console scans (hidden by default). `assembled.png`, `interior.png`, and `on-console.png` show the actual CAD geometry.

This is a **physical-fit prototype**, not a verified production design. The supplied connector STEP models are approximate, as confirmed by the project owner. Print the fit coupons before committing to the full housing. The firmware repository has not been modified; keep this design outside it until fit is accepted.

## Design

- Rounded front adapter with a shallow curved rear face following the console's front profile. Approximately **169 × 57.5 × 32 mm** for the shell; approximately 73 mm front-to-back including the connector envelopes.
- Four male connector envelopes face the console; four female envelopes face forward. The halves capture the keyed housing profiles and shoulders. Purchased connectors provide the electrical contacts: the STL files do not print functional connectors.
- Port axes at **X = −63.7, −36, +36, +63.7 mm**, with gaps of 27.7 / 72 / 27.7 mm. These nominal centres come from the supplied prior design and agree approximately with the scan's openings.
- The nominal male nose positions are Y = 7 + X²/1450 mm. Rear-shell clearance and nose exposure are provisional. The scans contain shell openings, not a complete model of the installed sockets and their contact engagement.
- Nominal wall/floor/roof thickness: 2.4 mm, with thicker connector collars. The horizontal enclosure seam has a 0.16 mm nominal gap.
- Four underside M2.5 fasteners: 2.8 mm lower clearance, 2.1 mm upper pilot, 5.4 mm head recess. Start with M2.5 × 20 mm plastic-thread/self-tapping screws and check engagement on the actual print. Two small alignment pins register the halves.
- ESP32 cradle for a **22.52 × 18 mm** board, using a provisional 1.6 mm PCB thickness. End-corner supports, end stops and flexible retaining lips allow the board to be pressed in. The component side faces up and the USB connector faces forward. Side solder-pad rows remain accessible.
- A 15.4 × 4.4 mm rounded front opening exposes the USB-C connector. The USB housing envelope and board component heights are provisional; verify your board and cable against the coupon/first print.
- A 17.6 × 17.6 × 1.7 mm translucent insert covers a 15 × 15 mm window above the board. This accommodates uncertainty in onboard LED placement. A little removable adhesive around the insert perimeter may be needed.
- A separate 10.6 × 6.6 mm horizontal passage, centred at Z = −9.3 mm, gives a narrow, approximately head-on sight line toward the original N64 power light. The passage continues through the board's rear stop. Check alignment against your console; it is not guaranteed visible from above.

The generic STEP envelopes show solid connector faces in previews because the source files do not model the contact openings. They are fit references, not proposed solid caps over the ports.

## Print and fit sequence

1. Print `BoardFitCoupon.stl`. Check PCB thickness, solder clearance, press-in force, removal and cable loads. Tune `pcb_width`, `pcb_length`, `pcb_thickness`, `pcb_clearance` and `clip_interference` as needed. The nominal retaining lip overhang is 0.15 mm; material and printer tolerance dominate the real fit.
2. Print `FemaleFitCoupon.stl` to check one lower female seat. This is a half-seat check, not a complete retention test. Measure the real connector's flange and solder-tail geometry.
3. Print both `RearAlignmentGauge.stl` and `RearAlignmentGaugeUpper.stl`. Capture all four actual male connectors in the gauge and test their alignment/engagement with the console. The centre fastener pair can secure the gauge; hold the outer ends together during the fit test. Adjust `port_x` and `nose_y` before a full print if needed. A rigid four-plug assembly depends on accurate connector pitch and depth.
4. Print `LowerShell.stl` with the outside floor on the bed. Print `UpperShell.stl` upside down with the outside roof on the bed. Keep scale at 100%; use the slicer's place-on-face function because the files retain assembly coordinates. Inspect supports around the USB opening and alignment features.
5. PETG is a reasonable first trial for the flexible cradle; start with a 0.4 mm nozzle, 0.2 mm layers and four perimeters. These are prototype starting settings, not qualified manufacturing specifications. Print the window in translucent material, or fabricate an equivalent insert.
6. Wire and seat the connectors, press in the board, route wiring away from the light passage and screws, then install the upper half. Confirm retention under controller insertion/removal and USB cable loads. Inspect the four rear connectors for full and even engagement.

No external bracket or adhesive mount to the console is included. The assembly relies on the four plug connections; leverage and retention under cable load must be tested physically.

## Wiring accommodation

Provide straight-through connections for each male/female pair's three contacts, with passive DATA taps to GPIO 13/12/11/10 in port order. Route 3V3 and GND to the centre as planned. The common interior space between front and rear connector tails accommodates these wires and strain relief; there is no custom PCB in this design.

The repository currently describes USB-powered sniffing with a shared ground and no console 3V3 connection. The requested console-powered arrangement is a hardware change: establish the actual Super Mini's power path before connecting its 3V3 rail while USB is also attached. This CAD work does not validate power-source isolation or change the firmware.

The window itself needs no extra GPIO. A programmable onboard LED still needs appropriate firmware. An ESP32 LED can remain illuminated from USB while the N64 is off, so it is not inherently a console-power indicator. The original-light passage avoids that ambiguity when aligned and viewed head-on.

## Editing and regeneration

The FCStd contains named solid features and reference geometry. It is **not a fully constrained Part Design sketch history**. `DesignParameters` records a snapshot; changing that snapshot alone does not recompute the solids.

Edit `parameters.json`, then run `build.FCMacro` in FreeCAD's Macro dialog to regenerate. Keep `build.py` beside the macro, and keep the supplied male/female STEP files in the parent directory. `build.py` is the editable source for larger structural changes. The most useful fit variables are connector centres, connector clearance, male nose depth and board dimensions/clip fit. Large changes to overall dimensions also require reviewing the support and fastener locations in the script.

Connector clearance uses the union of housing copies translated ±0.22 mm along each axis. This is an axis-based clearance envelope, not a mathematically uniform surface offset; diagonal clearance is smaller. Tune it with the actual connectors.

A successful build writes FCStd, STEP, seven STL files and `validation.json`. A failed geometric or collision check stops the build. Regeneration replaces those outputs; copy a revision first if you want to preserve it. The optional `preview.FCMacro` is a development rendering helper and closes its FreeCAD window after rendering. It is not the normal modelling entry point.

## Validation performed

FreeCAD 1.1.3 reports every exported print part/coupon as a valid single solid. No volumetric interference was found between either full enclosure half and any of the eight connector envelopes or the PCB envelope, or between the two halves. See `validation.json`.

All seven STL exports have zero boundary edges and zero non-manifold edges after welding coincident vertices at 0.0001 mm precision; see `mesh-validation.json`. `stl-dimensions.json` contains bounds measured directly from exported triangles. FreeCAD's analytic BREP bounding boxes can overestimate trimmed curved faces, particularly on the small coupons.

These checks do not establish physical fit, contact alignment, cable load strength, actual LED location, print tolerances, or exact console collision clearance. The board is an envelope model, and scan alignment is approximate.

## References and provenance

- [Wesk's N64 Console Scan, BitBuilt](https://bitbuilt.net/forums/threads/n64-console-scan.5527/). The author explicitly supplies these scans as reference only and notes possible scanning artifacts. The original Top/Bottom meshes are retained in `reference/`; reduced 75,000-triangle versions are embedded in the FreeCAD document. The bottom was translated by (0, 103.5, −29.3) mm and the top by (0, 71.5, 2.2) mm to approximate the socket-axis coordinate system. No rotation or scaling was applied. These transforms are approximate shell registration, not a dimensional certification.
- [ESP32-S3 Super Mini board reference supplied by the user](https://www.espboards.dev/esp32/esp32-s3-super-mini/). Used for the nominal 22.52 × 18 mm footprint; board thickness, component envelope, connector and LED placement need measurement on the actual variant. Its generic pin tables were not used to revise the existing GPIO assignments.
- Supplied `n64-input-ControllerPortMale.step`: 22 × 33.5 × 22 mm envelope.
- Supplied `n64-input-ControllerPortFemale.step`: 21 × 17.5 × 16.9 mm envelope.
- Supplied `n64-input2-cals-poor-attempt.step`: used for initial layout context and nominal male port centres; the new enclosure geometry is generated independently.
- `n64-input-sniffer/README.md`, `platformio.ini`: used for passive-tap wiring and USB/Wi-Fi context.

Review the scan author's terms before redistributing their meshes. The large raw scans/archive should not be committed to the firmware repository as part of a later CAD integration.
