# CAD development

The versioned FreeCAD models and print-ready 3MF files are the retained releases.
Builds write v1.1 models, working meshes, and reports. They leave v1.0 files intact.
The enclosure's generated male connector STEP also stays in its own folder.
If the connector design changes, explicitly promote that STEP file to the parent reference.

## Runtime

The scripts need these tools:

- FreeCAD's Python runtime, with the `FreeCAD`, `Part`, and `Mesh` modules, for geometry scripts
- Python with NumPy for packaging and checks
- OrcaSlicer for slicing

The saved print projects use slices from OrcaSlicer 2.4.2.
The layout and pause checks assume the saved P1S 0.4 mm profile.
They also assume its 0.16 mm layers and 0.20 mm first layer.

In the commands below, `python` means the Python interpreter with FreeCAD support.
The name `orca-slicer` means the OrcaSlicer executable.
Run the commands from the repository root.
For example, use these paths for the macOS application bundles:

```sh
export PYTHONPATH="/Applications/FreeCAD.app/Contents/Resources/lib${PYTHONPATH:+:$PYTHONPATH}"
alias python='/Applications/FreeCAD.app/Contents/Resources/bin/python'
alias orca-slicer='/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer'
```

As an alternative, run the applicable `build.FCMacro` in FreeCAD.
The macro finds `build.py` relative to its own path.
You can run other geometry checks in FreeCAD's Python console:

1. Set `__file__` to the script's absolute path.
2. Run the script with `exec(compile(...))`.

## Enclosure

1. Edit [Enclosure/parameters.json](Enclosure/parameters.json) for dimensions, or [Enclosure/build.py](Enclosure/build.py) for construction changes.
2. If the design changes, adjust any applicable fixed construction dimensions and fit checks in the source.

Each build reads the parameters again.
Some construction dimensions and fit checks remain fixed in the source.

Run the build, checks, and packaging scripts in this order:

```sh
python cad/Enclosure/build.py
python cad/Enclosure/check_fit.py
python cad/Enclosure/check_nut_seats.py
python cad/Enclosure/check_retention.py
python cad/Enclosure/check_mesh.py
python cad/Enclosure/package_print.py
python cad/Enclosure/create_3mf.py
```

The build checks that each part is a valid single solid and checks interference in the assembly.
Other checks cover these features:

- Terminal passages and male projection orientation
- Keeper installation and retention
- Lid removal and USB access
- Nut walls and insertion
- Mesh closure

The checks use the current geometry without loading discarded revisions.
Each generated revision needs its own physical fit tests.

`package_print.py` produces STL files in their print orientation, a manifest, and an assembly README in `Enclosure/print/full-enclosure-v1.1/`.
It also produces a ZIP.
`create_3mf.py` reads profiles from the retained v1.0 3MF and builds a new unsliced project from the new meshes.
It does not reuse old toolpaths.

Run the slicer and slice checks:

```sh
mkdir -p cad/Enclosure/slice/v1.1
orca-slicer --slice 0 --outputdir cad/Enclosure/slice/v1.1 --export-3mf Enclosure-full-enclosure-v1.1-Orca-complete.3mf cad/Enclosure/Enclosure-v1.1-Orca-input.3mf
python cad/Enclosure/check_nut_pause.py
python cad/Enclosure/verify_print.py
```

The two slice checks default to `Enclosure/slice/v1.1/`.
To check another Orca command-line output directory, pass `--slice-dir PATH`.
That directory must contain the exported 3MF and plate G-code files, plus `result.json` when Orca writes it.
The checks support Orca 2.4.0 through embedded slice metadata.
If Orca asks to open the 2.4.2 project, use `--allow-newer-file`.

The slice checks compare geometry with the generated STL files.
They also check plate placement, new slice warnings, and the exact order of the nut pause and cap extrusion.
They report existing profile warnings separately.
The retained enclosure project already contains `bed_temperature_too_high_than_filament`.

Check the bed/filament temperatures before printing; restoring the pipeline does not alter the tested project settings.

The checks fail if changed dimensions or settings invalidate the fixed layout, 14.12 mm pause height, or layer 88.
If this occurs, update the layout and pause checks together.
Then inspect the new slice.

## Soldering jig

The jig's dimensions are in [SolderingJig/build.py](SolderingJig/build.py).
The build uses the female and housing-only male STEP references directly.
It builds its own mating projection.

Run the build, checks, and slicer in this order:

```sh
python cad/SolderingJig/build.py
python cad/SolderingJig/check_fit.py
python cad/SolderingJig/create_3mf.py
mkdir -p cad/SolderingJig/slice/v1.1
orca-slicer --slice 0 --outputdir cad/SolderingJig/slice/v1.1 --export-3mf N64-Soldering-Jig-v1.1.3mf cad/SolderingJig/N64-Soldering-Jig-v1.1-input.3mf
python cad/SolderingJig/verify_print.py
```

The build and fit check cover solid validity, assembly interference, connector retention and rotation, clamp insertion, and terminal access.
The print check covers mesh geometry, layout, watertightness, and the absence of supports or pauses.
It accepts `--slice-dir PATH`, as the enclosure print check does.

## References and releases

The parent connector STEP files are the only external construction geometry.
The enclosure build copies the optional embedded console display meshes from the retained release, including their original placements.
It needs no historical scans, measurement reports, or revision folders.
This overlay is approximate.
It does not give a new console-clearance check after design changes.

Git ignores working STL/STEP exports, ZIPs, input 3MFs, reports, and slice directories.
The project retains named FreeCAD release models and sliced 3MFs.

To make a release:

1. Review the geometry and sliced project.
2. Test the physical changes.
3. Explicitly save a new named FreeCAD release.
4. Promote its checked sliced 3MF.
5. Update versioned filenames in the scripts and documentation.

New parameters saved in a FreeCAD document alone do not regenerate the solids.
