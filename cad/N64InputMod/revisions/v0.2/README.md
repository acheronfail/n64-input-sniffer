# N64InputMod — fit prototype v0.2

Open `N64InputMod.FCStd` in FreeCAD. This revision incorporates the physical fit feedback: the ESP32 footprint and female connector seat fit, but the old PCB clips were flimsy; the male seats fit but lacked reliable axial retention. The previous files are preserved in `revisions/v0.1/`.

## What changed

- Removed the N64 power-light passage entirely. The top ESP32 LED window remains.
- Lowered the board by 12.6 mm. Its seats now rise 5 mm from the interior floor and are connected by a rigid perimeter foundation.
- Replaced the tiny spring lips with **BoardKeeper**, an open U-shaped keeper secured by two M2 screws. Four corner fingers limit PCB lift; the centre, component area, solder rows and USB connector remain accessible. This replaces clip-only/press-fit retention with a positive fastener-held keeper.
- Moved the front USB opening down with the board. The old upper USB opening is gone.
- Added an independently adjustable pressure shoe for each male connector, driven by an M3 screw through a captive nut in the upper shell. Each shoe bears on a soft pad over the housing's flat surface. These are friction clamps, not a groove/flange interlock.
- Added two outer M2.5 enclosure fasteners. The full enclosure uses six; the rear gauge includes four, so its ends remain secured while testing the male clamps.
- Preserved the female seat dimensions, the male seat clearances, and the four nominal port centres. The new lower rear gauge has additional fastener holes and no light passage, so use the new matched gauge pair for the retention test.

The old flimsy PCB coupon and clearance-only gauge should not be used to judge this revision's retention.

## Print these next

| File | Quantity | Purpose |
|---|---:|---|
| `BoardFitCoupon.stl` | 1 | Revised rigid board cradle; about 36 × 27.5 mm footprint |
| `BoardKeeper.stl` | 1 | Fits the coupon and the full lower shell |
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

After the new coupon tests pass, print `LowerShell.stl`, `UpperShell.stl`, `BoardKeeper.stl`, four shoes, four soft pads, and optionally `LightWindow.stl` in translucent material. The window is 17.6 × 17.6 × 1.7 mm; a little removable adhesive around its perimeter may be needed.

Shell dimensions remain approximately 169 × 57.5 × 32 mm, excluding exposed connectors and clamp screw heads. Nominal port axes are X = −63.7, −36, +36, +63.7 mm; male nose Y = 7 + X²/1450 mm. Those values still require checking on the actual console. The modelled female fronts look solid because the supplied STEP files are housing envelopes without contact openings. They are not printed connector caps.

## Editable source and checks

Edit `parameters.json`, then run `build.FCMacro` in FreeCAD's Macro dialog. Keep `build.py` beside it and the supplied male/female STEP files in the parent directory. The FCStd contains named solid features and reference geometry, not a fully constrained Part Design sketch history. `DesignParameters` is a snapshot; changing it alone does not recompute geometry. Larger structural changes require editing `build.py`.

Connector clearance is unchanged: the union of housing copies translated ±0.22 mm on each axis. It is not a uniform surface offset; diagonal allowance is smaller. Do not change it solely to improve retention, since the tested seats fit well.

The build checks single-solid validity, housing/PCB interference, enclosure-half overlap, keeper interference and shoe/pad clearance from the enclosure. `validation.json` records these results. `mesh-validation.json` checks STL closure after welding coincident vertices at 0.0001 mm. `stl-dimensions.json` measures the exported mesh bounds. `revision-checks.json` compares the unchanged female coupon and checks the modelled male loading path. These are geometric checks, not physical load or electrical tests.

`assembled.png`, `interior.png`, `on-console.png`, `board-keeper.png` and `rear-gauge.png` are renders of the CAD. The last two are exploded assembly views. `preview.FCMacro` regenerates the previews in a temporary FreeCAD window and closes it.

## Wiring and sources

The interior allows the four straight-through controller connections and DATA taps on GPIO 13/12/11/10, plus the planned 3V3 and GND connections. The firmware repository remains unchanged. Its existing README describes USB-powered sniffing; console 3V3 power and simultaneous USB require checking the actual board's power path. A programmable ESP LED needs suitable firmware and may stay on under USB power when the console is off.

- [Wesk's N64 Console Scan](https://bitbuilt.net/forums/threads/n64-console-scan.5527/): reference-only shell scans with possible artifacts. Raw meshes are retained under `reference/`; reduced 75,000-triangle copies are embedded. Approximate translations: Bottom (0, 103.5, −29.3) mm; Top (0, 71.5, 2.2) mm, without rotation or scaling. This is not certified registration of installed sockets.
- [Supplied ESP32-S3 Super Mini reference](https://www.espboards.dev/esp32/esp32-s3-super-mini/): nominal 22.52 × 18 mm footprint. Thickness, components, USB and LED locations still use envelope assumptions.
- Supplied male STEP: 22 × 33.5 × 22 mm envelope. Supplied female STEP: 21 × 17.5 × 16.9 mm envelope. Both are approximate; physical seat fit has now been reported by the owner.
- Supplied prior enclosure STEP and `n64-input-sniffer` README/platform configuration provided layout and firmware context.

Keep the prototype outside the firmware repository until the fit and retention tests pass. Do not commit large raw scans; review the scan author's terms before redistribution.
