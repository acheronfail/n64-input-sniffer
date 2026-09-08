# N64InputMod — console-facing USB prototype v0.11

Open [N64InputMod.FCStd](N64InputMod.FCStd) in FreeCAD. A versioned copy is saved as `N64InputMod-v0.11.FCStd`. The v0.10 model and sources are preserved in `revisions/v0.10/`.

> [!WARNING]
> **Do not connect USB-C while the adapter is connected to the N64 console.**
> Fully disconnect the adapter from **all four console ports** before connecting USB-C to a computer or USB power source. Disconnect USB-C before reconnecting the adapter to the console.
>
> **Turning the console off is not enough.** USB power can backfeed the console’s 3.3V rail and potentially damage hardware. The 470 µF capacitor does not prevent backfeeding.

## Current revision: USB access from the console side

The ESP assembly rotates 180° about Z and moves between the two middle console plugs. USB now faces the console (+Y), with the board component side still up. The cradle, keeper, component envelopes and LED window move together. The former front USB opening and LED recess are closed. Connector mating positions, seat geometry, clamps, screw locations and the v0.10 wiring-space extension are retained.

The mount is inset an extra 1.5 mm to clear the nearby enclosure screw bosses. Its socket face is at Y = −11.8 mm, about 2.8 mm behind the central rear case face. A split access shroud extends to Y = +0.5 mm; its clear bore is 18 × 6.8 mm. The shroud limits sideways cable access through the gap between the enclosure and console. Its upper face stays at Z = 16 mm to preserve the lid’s roof-down print plane. The existing 10 × 4 mm rounded socket opening remains in the case wall.

**This is a mechanical-access prototype, not a verified electrical interlock.** The approximately aligned scan obstructs the tested 25 mm axial USB access envelope. Physical testing must confirm that the shroud clears your console and that USB cannot be connected while any console contacts remain engaged—including with an angled cable or the adapter partially withdrawn. Always fully disconnect all four console plugs before connecting USB; turning the console off is not isolation. The 470 µF capacitor does not prevent supply backfeeding.

## Current files and checks

- Native CAD: `N64InputMod.FCStd` and `N64InputMod-v0.11.FCStd`.
- STEP: `N64InputMod.step`.
- Print files: [v0.11 STLs and assembly notes](print/full-enclosure-v0.11/PRINT-AND-ASSEMBLE.md). Both shells must be reprinted. The keeper, window, shoes and pads retain their shapes and can be reused.
- `validation.json`: solid validity, hardware collisions, shell and keeper overlap.
- `console-usb-validation.json`: unchanged connector geometry, relocated board parts, sealed old opening, clear new socket path, keeper screw clearance and lid assembly sweep.
- `console-usb-scan-validation.json`: sampled guard/console clearance and axial access obstruction against the approximate scan.
- `mesh-validation.json`: exported STL closure checks.

Use [the complete v0.11 OrcaSlicer 3MF](N64InputMod-full-enclosure-v0.11-Orca-complete.3mf). It contains all 12 parts across three plates, the existing Bambu Lab P1S 0.4 mm profile, and checked toolpaths. All three plates sliced successfully in OrcaSlicer 2.4.2 with no reported plate warnings. Lower-shell tree supports are enabled from the bed for the new USB shroud. Physical printing remains unverified.

Plate 1 retains the source project’s PLA assignment and Supertack plate. Plate 2 contains the four TPU pads and uses Textured PEI because Orca rejects TPU on Supertack. Plate 3 retains the PETG window and Supertack settings; use translucent material if you want to see the LED.

Plate 1 has native `M400 U1` pauses **before layer 34 (Z = 5.48 mm, insert four M3 nuts)** and **before layer 88 (Z = 14.12 mm, insert six M2 nuts)**. Toolpath checks confirm all ten pocket caps start after the corresponding pause. These heights assume 0.16 mm layers and a 0.20 mm first layer; recheck after changing layer heights, orientation or geometry. All v0.10 projects are historical and retain the old front USB opening.

`pcb_console_side=1` enables the relocation. `pcb_front_y` and the earlier USB seam parameters remain in the original local board frame; `build.py` rotates that frame and translates Y by `front_y + rear_y - pcb_console_inset`. The `usb_guard_*` parameters set the new access shroud in assembly coordinates. The shell file contains named BRep features, not a constrained sketch history; regenerate using `build.FCMacro` after changing parameters.

## Earlier revision notes

The sections below record previous fit tests and revisions. Front-facing board instructions and old print sets describe those earlier versions, not v0.11.



## USB opening update (v0.3)

The opening is now **10 × 4 mm**, reduced from 15.4 × 4.4 mm, with 0.7 mm corner radii. This gives nominal 0.4 mm clearance on each side of the 9.2 × 3.2 mm socket envelope. The opening position, PCB mount and keeper are unchanged.

**Physical fit confirmed by the owner on 2026-09-07. No further board-coupon print is needed.** Proceed to the full enclosure; the separate male-clamp gauge test has been waived by the owner. The coupon now includes the complete curved front-wall thickness; the earlier coupon cut away about 1 mm from its front. Its footprint is now approximately 36 × 28.5 mm. The socket is recessed about 1.3 mm behind the case face, so the cable check matters as well as the gap appearance. The smaller opening is sized around the metal socket, not a universal cable overmould.

`usb_opening_width`, `usb_opening_height` and `usb_corner_radius` in `parameters.json` control this detail. `usb-revision-checks.json` verifies that the keeper and all lower-shell geometry outside the USB region remain unchanged, with no collision against the socket envelope.

## Retention changes retained from v0.2

- Removed the N64 power-light passage entirely. The top ESP32 LED window remains.
- Lowered the board by 12.6 mm. Its seats now rise 5 mm from the interior floor and are connected by a rigid perimeter foundation.
- Replaced the tiny spring lips with **BoardKeeper**, an open U-shaped keeper secured by two M2 screws. Four corner fingers limit PCB lift; the centre, component area, solder rows and USB connector remain accessible. This replaces clip-only/press-fit retention with a positive fastener-held keeper.
- Moved the front USB opening down with the board. The old upper USB opening is gone.
- Added an independently adjustable pressure shoe for each male connector, driven by an M3 screw through a captive nut in the upper shell. Each shoe bears on a soft pad over the housing's flat surface. These are friction clamps, not a groove/flange interlock.
- Added two outer M2.5 enclosure fasteners. The full enclosure uses six; the rear gauge includes four, so its ends remain secured while testing the male clamps.
- Preserved the female seat dimensions, the male seat clearances, and the four nominal port centres. The new lower rear gauge has additional fastener holes and no light passage, so use the new matched gauge pair for the retention test.

The old flimsy PCB coupon and clearance-only gauge should not be used to judge this revision's retention.

## Optional male-retention gauge (skipped for this build)

| File | Quantity | Purpose |
|---|---:|---|
| `BoardFitCoupon.stl` | — | Board retention and USB fit confirmed; no reprint needed |
| `BoardKeeper.stl` | 1 | Reuse the one already printed; unchanged |
| `RearAlignmentGauge.stl` | 1 | Updated lower male gauge |
| `RearAlignmentGaugeUpper.stl` | 1 | Upper gauge with nut pockets and shoe guides |
| `MaleClampShoe.stl` | 4 | Rigid pressure shoes, all identical |
| `MaleClampPad.stl` | 4 | Soft pads, 12 × 8 × 0.8 mm |

The female coupon has already passed your fit test; no need to reprint it.

Use the same material and settings intended for the final case. PETG is a prototype starting choice for the rigid parts. The clamp pads need flexible TPU or equivalent soft rubber sheet, **not rigid PLA/PETG**. Actual grip still needs testing. Print at 100% scale; the STLs retain assembly coordinates, so use the slicer's place-on-face function. Lower parts go outside-floor down, upper parts outside-roof down, and the keeper/shoes/pads lie flat on their broad faces. Inspect bridges over USB and connector openings in the slicer.

## Board keeper assembly

1. Seat the board component-side up, with USB pointing through the front opening. Check clearance around actual solder joints and underside components.
2. Place the U-shaped keeper over it. The open end faces USB; the four small fingers sit over PCB corners. The two screw ears sit on the side bosses.
3. Install **two M2 × 8 mm screws suitable for plastic pilot holes**. The coupon has 1.6 mm pilot holes and the keeper has 2.2 mm clearance holes. Tighten only until the keeper seats on its bosses.
4. Check USB insertion/removal and pull on the board gently. The keeper should prevent it escaping even though the nominal vertical allowance is 0.15 mm. This is a mechanical capture test, not just a friction test.

PCB nominal size remains 22.52 × 18 × 1.6 mm. The board's underside is at Z = −8.6 mm. End-corner supports avoid relying on four tall columns. The board is farther below the top LED window now; the LED viewing angle/brightness must be checked with the real board. No light pipe is included.

## Male connector gauge assembly and retention

The gauge is a **split clamp**. Do not push the plugs through the complete gauge axially.

1. Lay all four male housings into the open lower cradles from above. Their mating ends point toward the console, away from the wiring/interior side. The modelled flat upper housing surface faces up.
2. Put one soft pad and one rigid shoe on the flat top of each housing. Each shoe fits a rectangular guide in the upper half; its underside contacts the soft pad, not the connector contacts.
3. From underneath the upper gauge, insert **four ordinary M3 hex nuts** into the hex recesses at the tops of those guides. Nut pocket clearance is 5.8 mm across flats. Retain the nuts temporarily with the adjustment screws if convenient, keeping the screw tips retracted while assembling.
4. Install the upper gauge over the housings/shoes. Secure the matched gauge halves with **four M2.5 × 20 mm screws suitable for plastic pilot holes**, inserted from underneath: two near the centre and two near the outer ends.
5. Fit **four M3 × 8 mm adjustment screws**, one above each shoe. Gently tighten each until its pad grips the housing. The head need not bottom out against the roof; it is an adjustment screw. Do not use a bare screw against the connector housing.
6. Test each plug for movement in both axial directions, then check even engagement with the console. Tighten incrementally and inspect the printed nut supports. The clamp performance depends on the real housing, pad hardness and preload.

This creates friction retention through the soft pads and lower seats. It does **not** turn the approximate connector envelope into a positively interlocking mount. If a housing still slips at modest clamp pressure, record that result rather than forcing the screws; a groove/flange capture or different connector mounting scheme will need the actual hardware geometry.

The full enclosure uses the same shoes, pads and M3 hardware, plus **six** M2.5 enclosure screws. All retaining hardware is accessible for disassembly. Cable-load strength has not been physically verified.

## Final enclosure files

The owner has approved proceeding to the full enclosure: print `LowerShell.stl`, `UpperShell.stl`, `BoardKeeper.stl`, four shoes, four soft pads, and optionally `LightWindow.stl` in translucent material. The window is 17.6 × 17.6 × 1.7 mm; a little removable adhesive around its perimeter may be needed.

Shell dimensions remain approximately 169 × 57.5 × 32 mm, excluding exposed connectors and clamp screw heads. Nominal port axes are X = −63.7, −36, +36, +63.7 mm; male nose Y = 7 + X²/1450 mm. Those values still require checking on the actual console. The modelled female fronts look solid because the supplied STEP files are housing envelopes without contact openings. They are not printed connector caps.

## Editable source and checks

Edit `parameters.json`, then run `build.FCMacro` in FreeCAD's Macro dialog. Keep `build.py` beside it and the supplied male/female STEP files in the parent directory. The FCStd contains named solid features and reference geometry, not a fully constrained Part Design sketch history. `DesignParameters` is a snapshot; changing it alone does not recompute geometry. Larger structural changes require editing `build.py`.

Connector clearance is unchanged: the union of housing copies translated ±0.22 mm on each axis. It is not a uniform surface offset; diagonal allowance is smaller. Do not change it solely to improve retention, since the tested seats fit well.

The build checks single-solid validity, housing/PCB interference, enclosure-half overlap, keeper interference and shoe/pad clearance from the enclosure. `validation.json` records these results. `mesh-validation.json` checks STL closure after welding coincident vertices at 0.0001 mm. `stl-dimensions.json` measures the exported mesh bounds. `revision-checks.json` compares the unchanged female coupon and checks the modelled male loading path. These are geometric checks, not physical load or electrical tests.

`assembled.png`, `interior.png`, `on-console.png`, `board-keeper.png` and `rear-gauge.png` are renders of the CAD. The last two are exploded assembly views. `preview.FCMacro` regenerates the previews in a temporary FreeCAD window and closes it.

## Wiring and sources

The current wiring is documented in the [firmware README](../n64-input-sniffer/README.md): DATA taps on GPIO 13/12/11/10, one console port’s 3.3V and GND supplying the ESP, and a 470 µF capacitor across ESP 3V3/GND. The rear USB relocation is intended to prevent ordinary USB access while mounted; physical verification is still required. Do not connect powered USB with the console power tap electrically connected.

- [Wesk's N64 Console Scan](https://bitbuilt.net/forums/threads/n64-console-scan.5527/): reference-only shell scans with possible artifacts. Raw meshes are retained under `reference/`; reduced 75,000-triangle copies are embedded. Approximate translations: Bottom (0, 103.5, −29.3) mm; Top (0, 71.5, 2.2) mm, without rotation or scaling. This is not certified registration of installed sockets.
- [Supplied ESP32-S3 Super Mini reference](https://www.espboards.dev/esp32/esp32-s3-super-mini/): nominal 22.52 × 18 mm footprint. Thickness, components, USB and LED locations still use envelope assumptions.
- Supplied male STEP: 22 × 33.5 × 22 mm envelope. Supplied female STEP: 21 × 17.5 × 16.9 mm envelope. Both are approximate; physical seat fit has now been reported by the owner.
- Supplied prior enclosure STEP and `n64-input-sniffer` README/platform configuration provided layout and firmware context.

Keep the prototype outside the firmware repository until the full enclosure has been assembled and accepted. Do not commit large raw scans; review the scan author's terms before redistribution.


## v0.4 - USB opening shared between shell halves

The upper front tongue now descends to the USB centreline and meets a matching lower-shell notch with 0.16 mm seam clearance. The 10 x 4 mm rounded opening is unchanged. In the supplied floor-down/roof-down print orientations, both USB notches are open-ended, removing the bridge over this opening. This does not remove possible support needs elsewhere. Board mount, keeper and connector seats remain unchanged.

Use `N64InputMod-full-enclosure-v0.4-Orca-complete.3mf` for the complete 12-part, three-plate set, including the keeper. CAD: `N64InputMod-v0.4.FCStd`. Individual bed-oriented STLs: `print/full-enclosure-v0.4/`. This seam revision has geometry checks but awaits a physical print.


## v0.5 - Reduce printing supports

Female seat bases extend to the floor. Alignment-pad undersides have 45-degree braces in each shell print orientation. The LED-window ledge has a tapered underside and retains a 0.6 mm flat land (0.4 mm nominal engagement beneath the insert). The split USB seam remains.

Complete Orca project: `N64InputMod-full-enclosure-v0.5-Orca-complete.3mf` (12 parts on 3 plates, including keeper). Native CAD: `N64InputMod-v0.5.FCStd`. Bed-oriented STLs: `print/full-enclosure-v0.5/`. These changes reduce supports at the targeted features; no claim of a physically verified support-free print is made.


## v0.6 - Raised ESP32 prototype

PCB underside moves from Z=-8.6 to Z=7.0 mm on a rigid perimeter-wall pedestal. The tested keeper is unchanged in shape. PCB top to window underside decreases from 20.95 to 5.35 mm. Actual LED location, light output and physical raised-mount fit still require confirmation. The broad window is retained; no precise LED alignment is claimed.

The lower front tongue now rises to the USB centreline at Z=10.2 mm and is 28 mm nominal width to clear the pedestal. Both halves retain open USB notches and the 10 x 4 mm opening. Modeled component-to-lid clearance is 1.3 mm; assumed 4 mm diameter x 1.7 mm tall keeper screw heads have 1.35 mm clearance.

Use `N64InputMod-full-enclosure-v0.6-Orca-complete.3mf` for all 12 print parts on three plates, or `N64InputMod-v0.6.FCStd` for CAD. The prior v0.5 files remain available.


## v0.7 - Use the available flat-head screws and nuts

The board keeper remains unchanged and uses the owner's two normal M2 x 8 plastic screws. Six M2 x 20 countersunk machine screws replace the M2.5 enclosure fasteners and engage six side-loaded M2 nuts in the lid. Four M3 x 8 flat-head screws and four M3 nuts operate the existing clamps. Brass inserts are not required. The countersinks target 90-degree metric heads, nominal diameters 4 mm (M2) and 6 mm (M3); purchased dimensions have not been confirmed. Clamp heads remain adjustable and may stand proud.

Use `N64InputMod-full-enclosure-v0.7-Orca-complete.3mf` (all 12 print parts) or `N64InputMod-v0.7.FCStd`. Full hardware/assembly instructions are in `print/full-enclosure-v0.7/PRINT-AND-ASSEMBLE.md`. This hardware revision requires a physical fit check.


## v0.8 - Print-in captive nuts

All ten nuts are inserted during a paused roof-down lid print; the M2 side slots are removed and M3 nuts are enclosed by a 0.8 mm cap above the shoe guide. The complete Orca 3MF includes native pauses before layer 34 (Z=5.48 mm; four M3 nuts) and layer 88 (Z=14.12 mm; six M2 nuts), verified against generated toolpaths at 0.16 mm layers / 0.20 mm first layer. Fully seat nuts below the printed rim before resuming. Recheck pauses if changing layer heights or orientation.

Use `N64InputMod-full-enclosure-v0.8-Orca-complete.3mf` or `N64InputMod-v0.8.FCStd`. Detailed instructions: `print/full-enclosure-v0.8/PRINT-AND-ASSEMBLE.md`. Profile bed is now Textured PEI Plate; select your actual bed and filaments. Geometry, insertion, retention, native pauses and cap toolpaths were checked. Physical printing remains unverified.


## v0.9 - Extra rear clearance for the ESP32

The 1.6 mm rear board stop moves 0.8 mm away from the USB end. The low foundation is extended by the same amount to retain the structural connection. All other print parts are unchanged, so only the lower shell needs reprinting. The complete Orca project retains both embedded-nut pauses. Use `N64InputMod-full-enclosure-v0.9-Orca-complete.3mf`, `N64InputMod-v0.9.FCStd`, or the bed-oriented `print/full-enclosure-v0.9/LowerShell.stl`.
