# CAD release

The v1.2 enclosure moves the ESP and its supports 2 mm toward the USB-C wall.
**Status: verified.** The owner printed v1.2 and marked it verified on 2026-09-15.
The v1.1 release stays available.

- [v1.2 FreeCAD model](Enclosure/Enclosure-v1.2.FCStd)
- [v1.2 print project](Enclosure/Enclosure-full-enclosure-v1.2-Orca-complete.3mf)

The tested **v1.1** enclosure leaves at least 2 mm between opposing keeper towers.
It moves the ESP window 4 mm toward the N64 edge and moves four closure bolts toward that edge.
The matching jig has an 18.1 mm connector gap.
**Status: verified.** The owner confirmed that both printed v1.1 parts work on 2026-09-15.
Physical verification applies to the retained v1.1 release files.
Generated reports describe digital checks only. Future geometry changes need new physical tests.

The physically tested [v1.0 enclosure](Enclosure/Enclosure-v1.0.FCStd) and [v1.0 print project](Enclosure/Enclosure-full-enclosure-v1.0-Orca-complete.3mf) remain unchanged.

- [Enclosure FreeCAD model](Enclosure/Enclosure-v1.1.FCStd)
- [Enclosure print-ready OrcaSlicer 3MF](Enclosure/Enclosure-full-enclosure-v1.1-Orca-complete.3mf)
- [Enclosure print and assembly instructions](Enclosure/README.md)
- [Soldering jig model, print project, and instructions](SolderingJig/README.md)
- Latest [female connector](n64-input-ControllerPortFemale.step) and [male connector](n64-input-ControllerPortMale.step) STEP models
- [Male housing-only reference](n64-input-ControllerPortMale-housing.step), the seating datum for the enclosure and jig

Both FreeCAD documents embed their shapes and references.
You need no external scans or build scripts to open them.
These documents contain saved solid models, not a history of constrained sketches.
Changes to the embedded parameter snapshot alone do not regenerate geometry.

The current Python build, geometry checks, and print export scripts remain beside each model.
See the [development instructions](DEVELOPMENT.md) to regenerate and revise the models.
Historical revisions and duplicate generated exports are omitted.

The enclosure contains reduced display meshes from [Wesk's N64 console scan](https://bitbuilt.net/forums/threads/n64-console-scan.5527/).
Their alignment is approximate.

See the [repository README](../README.md) for wiring and firmware.
