# Two-port enclosure

**Physically verified on 2026-11-27.** The owner printed the two-port enclosure with the lengthened ESP32 guides and confirmed that the print fits and works well. This release removes the unused capacitor cup from the lower shell. CAD comparison confirmed that the change is confined to the cup.

This enclosure fits N64 controller ports **1 and 2**, the two on the left when facing the console. The case is **75.5 × 58.1 × 28.2 mm** (width × depth × height), excluding connector projections. It is about 55% narrower and 3.8 mm lower than the four-port v1.4 enclosure.

[FreeCAD model](Enclosure-two-port.FCStd) · [OrcaSlicer project](Enclosure-two-port-Orca-complete.3mf)

The male mating projections, lower capture geometry and separate port keepers use the physically verified [v1.4 reference](../Enclosure-v1.4.FCStd) at the original console coordinates. The ESP32-S3 Super Mini slides vertically into a **24.92 mm** pocket on the side nearest port 3. The USB-C opening faces the console beside the male port 2 plug. The console covers it when the adapter is seated. The board’s component side faces a **15.3 × 14.4 mm** translucent side window for the RGB status LED.

## Assembly

1. Use the v1.4 connector types and reuse male keepers **1 and 2** and two female keepers if available. Install the ports using eight 2 mm × 8 mm countersunk screws suitable for plastic.
2. Set the board into its lower guides with USB-C toward the console and the component side toward the inner sidewall. With the lid off, slide the translucent window down into the sidewall slot. The upper shell captures the board at its corners and retains the window. Press BOOT with the lid removed.
3. Place the 100 µF decoupling capacitor close to the ESP32 with short leads. Wire controller data to GPIO 13 and GPIO 12 for ports 1 and 2, following the existing [wiring instructions](../../../README.md#setup).
4. Close the shell with three M2 × 20 mm countersunk machine screws. Check that the adapter seats evenly on both console ports and that controllers can still plug directly into ports 3 and 4.
5. Check that the RGB LED is visible through the window when the N64 powers the board. Verify with an unpowered USB-C cable that the console blocks access when the adapter is seated and that the cable mates when the adapter is detached.

Disconnect the adapter from both console ports before connecting USB-C, following the same power precaution as the four-port enclosure.

## Printing

Plate 1 contains both shells and four keepers in PLA. Plate 2 contains the status window, face down, for translucent PETG. The OrcaSlicer project uses the v1.4 Bambu Lab P1S 0.4 mm profile, with 0.16 mm layers and a 0.20 mm first layer. Insert **three M2 nuts** into the roof-down upper shell at the pause before layer 82 (Z = 13.16 mm). All three caps start on layer 83 in the supplied slice. Plate 2 has no pause. OrcaSlicer estimates 2 h 26 min for the PLA parts and 10 min for the window. If the slice settings change, check the pause against the new pocket caps.

CAD checks confirmed the v1.4 port seats, lid and PCB insertion, and window retention. The N64 reference scan places the console face about 2.6–3.2 mm from the USB-C receptacle, inside the space occupied by the slim plug used in the check.

## Regeneration

Run the build with FreeCAD's Python interpreter and the project packager with NumPy. Run these commands from the repository root.

```sh
python cad/Enclosure/TwoPort/build.py --print-directory cad/Enclosure/print/two-port
python cad/Enclosure/TwoPort/make_project.py cad/Enclosure/print/two-port cad/Enclosure/print/two-port/TwoPort-Orca-input.3mf
```

The build reads v1.4 in the original assembly coordinates and exports all seven parts in their bed orientation. The project packager writes an unsliced Orca project with the three-nut pause configured.
