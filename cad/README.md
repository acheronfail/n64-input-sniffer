# CAD release

The enclosure **v1.0** is the physically tested v0.16 design, renamed without changing the FreeCAD or 3MF contents. The owner confirmed successful testing on 2026-09-13. Internal document and slicer labels retain the original N64InputMod/v0.16 names to preserve the tested file contents.

- [Enclosure FreeCAD model](Enclosure/Enclosure-v1.0.FCStd)
- [Enclosure print-ready OrcaSlicer 3MF](Enclosure/Enclosure-full-enclosure-v1.0-Orca-complete.3mf)
- [Enclosure printing and assembly](Enclosure/README.md)
- [Soldering jig model, print project and instructions](SolderingJig/README.md)
- Latest [female connector](n64-input-ControllerPortFemale.step) and [male connector](n64-input-ControllerPortMale.step) STEP models
- [Male housing-only reference](n64-input-ControllerPortMale-housing.step), the seating datum used by the enclosure and jig

Both FreeCAD documents embed their shapes and references; no external scans or build scripts are needed to open them. These are saved solid models, not a constrained sketch history; changing the embedded parameter snapshot alone does not regenerate geometry. The current Python build, geometry checks and print export scripts are retained alongside each model. See [development instructions](DEVELOPMENT.md) to regenerate and iterate. Historical revisions and redundant generated exports are omitted.

The enclosure contains reduced display meshes from [Wesk's N64 console scan](https://bitbuilt.net/forums/threads/n64-console-scan.5527/). Their alignment is approximate.

See the [repository README](../README.md) for wiring and firmware.
