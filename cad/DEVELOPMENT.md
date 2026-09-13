# Iterating on the CAD

The versioned FreeCAD and print-ready 3MF files are the retained releases. Builds write unversioned working models, meshes and reports, leaving the tested files intact. The enclosure's generated male connector STEP also stays in its own folder; promote it to the parent reference deliberately if the connector design changes.

## Runtime

Use FreeCAD's Python runtime for the geometry scripts (`FreeCAD`, `Part` and `Mesh` modules), Python with NumPy for packaging and validation, and OrcaSlicer for slicing. The saved print projects were sliced with OrcaSlicer 2.4.2. The layout and pause checks assume the saved P1S 0.4 mm profile and its 0.16 mm layers / 0.20 mm first layer.

In the commands below, `python` means the FreeCAD-capable Python interpreter, and `orca-slicer` means the OrcaSlicer executable. Run from the repository root. For the macOS application bundles, for example:

```sh
export PYTHONPATH="/Applications/FreeCAD.app/Contents/Resources/lib${PYTHONPATH:+:$PYTHONPATH}"
alias python='/Applications/FreeCAD.app/Contents/Resources/bin/python'
alias orca-slicer='/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer'
```

Alternatively, open the relevant `build.FCMacro` in FreeCAD and run it. The macro resolves `build.py` relative to itself. Other geometry checks can be executed in FreeCAD's Python console with `exec(compile(...))` and `__file__` set to the script's absolute path.

## Enclosure

Edit [Enclosure/parameters.json](Enclosure/parameters.json) for dimensions, or [Enclosure/build.py](Enclosure/build.py) for construction changes. Parameters are read on every build. Some construction dimensions and fit checks remain fixed in the source; adjust those deliberately when changing the design.

```sh
python cad/Enclosure/build.py
python cad/Enclosure/check_fit.py
python cad/Enclosure/check_nut_seats.py
python cad/Enclosure/check_retention.py
python cad/Enclosure/check_mesh.py
python cad/Enclosure/package_print.py
python cad/Enclosure/create_3mf.py
```

The build checks valid single solids and assembled interference. Additional checks cover terminal passages, male projection orientation, keeper installation/retention, lid removal, USB access, nut walls and insertion, and mesh closure. They check the current geometry without loading discarded revisions. Generated iterations require their own physical fit testing.

`package_print.py` produces bed-oriented STLs, a manifest and an assembly README in `Enclosure/print/full-enclosure-v1.0/`, plus a ZIP. `create_3mf.py` reads profiles from the retained v1.0 3MF and builds a fresh unsliced project from the new meshes; it does not reuse old toolpaths.

```sh
mkdir -p cad/Enclosure/slice
orca-slicer --slice 0 --outputdir cad/Enclosure/slice --export-3mf Enclosure-full-enclosure-v1.0-Orca-complete.3mf cad/Enclosure/Enclosure-v1.0-Orca-input.3mf
python cad/Enclosure/check_nut_pause.py
python cad/Enclosure/verify_print.py
```

The two slice checks default to `Enclosure/slice/`; pass `--slice-dir PATH` to check another Orca CLI output directory containing the exported 3MF and plate G-code files, plus `result.json` when Orca emits it. Orca 2.4.0 is supported using embedded slice metadata; use `--allow-newer-file` when it asks to open the 2.4.2 project. They check geometry against generated STLs, plate placement, new slice warnings and the exact nut pause/cap extrusion ordering. Existing profile warnings are reported separately: the retained enclosure project already contains `bed_temperature_too_high_than_filament`. Check the bed/filament temperatures before printing; restoring the pipeline does not alter the tested project settings. Checks intentionally fail if changed dimensions or settings invalidate the fixed layout, 14.12 mm pause height or layer 88; update the layout and pause validation together and inspect the reslice.

## Soldering jig

The jig's dimensions currently live in [SolderingJig/build.py](SolderingJig/build.py). It uses the female and housing-only male STEP references directly and builds its own mating projection.

```sh
python cad/SolderingJig/build.py
python cad/SolderingJig/check_fit.py
python cad/SolderingJig/create_3mf.py
mkdir -p cad/SolderingJig/slice
orca-slicer --slice 0 --outputdir cad/SolderingJig/slice --export-3mf N64-Soldering-Jig-v1.3mf cad/SolderingJig/N64-Soldering-Jig-v1-input.3mf
python cad/SolderingJig/verify_print.py
```

The build and fit check cover solid validity, assembly interference, connector retention and rotation, clamp insertion and terminal access. The print verifier checks mesh geometry, layout, watertightness and the absence of supports or pauses. It accepts `--slice-dir PATH` like the enclosure verifier.

## References and releases

The parent connector STEP files are the only external construction geometry. The enclosure build copies the optional embedded console display meshes from the retained release, including their original placements. No historical scans, measurement reports or revision folders are required. This overlay is approximate and is not a new console-clearance check after design changes.

Generated models, STL/STEP exports, ZIPs, input 3MFs, reports and slice directories are ignored by Git. Review geometry and the sliced project, test the physical changes, then explicitly save a new named FreeCAD release and promote its verified sliced 3MF. Update versioned filenames in the scripts and documentation when making that release. Saving new parameters in a FreeCAD document alone does not regenerate the solids.
