# N64InputMod v0.6 — full enclosure print set

The owner confirmed the board mount/keeper, USB opening and connector seat fits, and chose to proceed without a separate male-clamp retention test. Revision v0.6 moves the front seam through the USB opening; the accepted board mount, keeper and connector seats are unchanged. These STL copies are rotated/translated for printing; the original CAD/STLs retain assembly coordinates.

## Print quantities

| File | Print now | Material |
|---|---:|---|
| LowerShell.stl | 1 | Same rigid material used for the successful coupon |
| UpperShell.stl | 1 | Same rigid material |
| MaleClampShoe.stl | 4 | Same rigid material |
| MaleClampPad.stl | 4 | Flexible TPU, or substitute soft rubber sheet |
| LightWindow.stl | 1, optional | Translucent material |
| BoardKeeper.stl | 1 | Same rigid material |

Soft pad dimensions: **12 × 8 × 0.8 mm** each. Do not substitute rigid material for the soft pads if using the adjustable clamps. If using the owner's proposed adhesive fallback, the shoes/pads/clamp hardware may be omitted; that bond has not been designed or load-tested here. Keep adhesive away from mating ends and contacts.

## OrcaSlicer setup

- Import the parts and keep **100% scale**. Use the nozzle, filament and profile that produced the successful coupon.
- Files already have their intended bed face at Z = 0. The lower shell is floor-down; the upper shell is roof-down. The other pieces lie flat. Do not flip the upper shell back into assembly orientation.
- When importing STLs, duplicate the shoe and pad to four copies each. The complete 3MF already contains all 12 parts, including the keeper.
- Print rigid parts, soft pads and the translucent window in separate material jobs as appropriate. The 3MF includes P1S 0.4 mm settings; choose your actual filament profiles before slicing. No G-code is included.
- Inspect the sliced preview, particularly supports/bridges around connector openings, internal nut pockets. Preserve the fit surfaces when removing supports.

The shell is approximately 169 × 57.5 mm in plan, within the P1S bed. Each STL contains one part. The manifest records dimensions, part counts and checksums. Existing source meshes passed closure checks; the print preparation only applies rigid rotations and translations, preserving their topology and dimensions.

## Hardware

| Hardware | Full enclosure quantity |
|---|---:|
| M2 × 8 mm screws suitable for plastic pilot holes | 2 — reuse from the keeper test |
| M2.5 × 20 mm screws suitable for plastic pilot holes | **6** |
| M3 × 8 mm clamp-adjustment screws | 4 |
| Ordinary M3 hex nuts | 4 |
| Actual male N64 connectors | 4 |
| Actual female N64 connectors | 4 |
| ESP32-S3 Super Mini | 1 |

The six M2.5 screws close the enclosure. The four M3 screws adjust male-housing grip; these are separate functions. The enclosure has plastic pilot holes for the M2/M2.5 fasteners and captive metal nuts for the M3 adjustment screws.

## Assembly

1. Seat the board in the lower shell with its USB connector through the front opening. Fit the U-shaped keeper: open end toward USB, fingers over the PCB corners. Attach it using the two M2 screws, seating the keeper on its bosses.
2. Lay the female connectors into their front seats and male connectors into the rear seats from above. Male mating ends face the console; their modelled flat upper housing surfaces face up. Route the straight-through wiring and passive DATA taps through the common interior, clear of the screw bosses and clamp pockets.
3. Place one soft pad and one rigid pressure shoe on each male housing. The shoe underside bears on the pad. Insert the four M3 nuts from underneath the upper shell into the hex pockets above the shoe guides. Adjustment screws can hold the nuts temporarily; leave their tips retracted during closure.
4. Place the upper shell over the assembly, ensuring the shoes enter their guides and no wiring is trapped. Close it with **six M2.5 screws inserted from underneath**.
5. Gently adjust the four M3 screws until the male housings resist sliding. Their heads need not bottom out on the roof. These clamps provide friction retention, not a groove/flange interlock. The owner's adhesive fallback remains an option if grip proves insufficient.
6. Fit the optional translucent window into the top recess; use a little removable adhesive around its perimeter if needed.
7. Connect the assembly to the console and check even plug engagement, controller/USB cable insertion and LED visibility. Full-assembly fit and cable-load behaviour remain to be established on this first complete print.

Electrical connections follow the project wiring, with DATA taps on GPIO 13/12/11/10. The existing CAD work does not establish USB/console power-source isolation; retain the project's intended electrical implementation.


USB seam revision: the upper front tongue meets the lower shell through the USB opening. Both notches are open in their print orientations. A board keeper is included in this complete set.


Revision v0.6 extends the female connector bases to the floor, braces the alignment pads, and tapers beneath the LED-window ledge while retaining a 0.6 mm seating land. The USB split seam is retained. Check the sliced preview for remaining support needs; this revision is not physically print-tested.


Raised-board prototype: the PCB underside is now Z=7.0 mm, 15.6 mm higher than v0.5. The existing keeper is translated upward without changing its shape. The local lower-shell tongue is wider and rises to the USB centre at Z=10.2 mm. The 10 x 4 mm USB opening and shared seam are retained. Board-to-window clearance is improved, but the actual LED position and brightness remain unverified.
