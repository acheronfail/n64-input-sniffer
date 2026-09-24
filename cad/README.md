# CAD release v1.3

**Status: enclosure and soldering jig physically verified.** The owner printed the complete v1.3 enclosure, confirmed that everything worked perfectly, and marked the v1.3 jig verified on 2026-09-25.

- [v1.3 FreeCAD model](Enclosure/Enclosure-v1.3.FCStd)
- [v1.3 print-ready 3MF](Enclosure/Enclosure-full-enclosure-v1.3-Orca-complete.3mf)
- [Printing and assembly](Enclosure/README.md)
- [Release validation](V1.3-VALIDATION.md)
- [Development and regeneration](DEVELOPMENT.md)

v1.3 captures the stripped male connector body and reduces enclosure depth by 15.5 mm, to approximately 58.1 mm. It retains the existing wiring gap and console port positions. The final keepers have side-tab clearances, an enclosed shoulder pocket and a wider internal contact step. The small central pad tier is removed. The cradle is 1.5 mm deeper than the initial fit design.

The measured male body is 18.5 mm in diameter, 14.3 mm from flat to opposite arc, and 18 mm long. Overall length is 29.9 mm, including the 11.9 mm mating projection.

The release retains the exact model and sliced project used for the successful full test. Intermediate fit-test projects, previews, backups, meshes, bundles and slicing outputs have been removed. The source can regenerate working files when needed.

## Soldering jig

The [v1.3 soldering jig](SolderingJig/README.md) holds a stripped male connector and female connector for wiring. The owner also confirmed this jig as verified on 2026-09-25. Its exact model and print project are retained alongside the earlier verified v1.1 jig.

## Retained releases and references

The verified v1.0, v1.1 and v1.2 enclosure releases remain unchanged. The [v1.2 model](Enclosure/Enclosure-v1.2.FCStd) and [v1.2 print project](Enclosure/Enclosure-full-enclosure-v1.2-Orca-complete.3mf) were verified on 2026-09-15.

The original [female](n64-input-ControllerPortFemale.step), [full male](n64-input-ControllerPortMale.step) and [male housing](n64-input-ControllerPortMale-housing.step) references remain for earlier releases. The [stripped male reference](n64-input-ControllerPortMale-stripped-v1.3.step) is retained separately for v1.3.

FreeCAD documents embed their geometry and approximate console display meshes. They contain saved solids, not a constrained-sketch history. Changing their parameter snapshot alone does not regenerate the model. Build-time prototype labels inside saved documents predate the physical test; this release record identifies the verified files.

See the [repository README](../README.md) for wiring and firmware.
