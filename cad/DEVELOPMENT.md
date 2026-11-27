# CAD development

The versioned FreeCAD models and print-ready 3MF files are the retained releases.
Enclosure builds write v1.4 models, working meshes and reports. They preserve the verified v1.0–v1.3 releases.
Soldering jig builds write v1.3 and preserve v1.1.
The enclosure's generated male connector STEP also stays in its own folder.
The v1.3 copy is retained as `n64-input-ControllerPortMale-stripped-v1.3.step`.
Keep versioned stripped references separate from the original full-housing references.

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
python cad/Enclosure/check_side_closure.py
python cad/Enclosure/check_gap_fills.py
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

`package_print.py` produces STL files in their print orientation, a manifest, and an assembly README in `Enclosure/print/full-enclosure-v1.4/`.
It also produces a ZIP.
`create_3mf.py` reads profiles from the retained v1.0 3MF and builds a new unsliced project from the new meshes.
It does not reuse old toolpaths.

Run the slicer and slice checks:

```sh
mkdir -p cad/Enclosure/slice/v1.4
orca-slicer --slice 0 --outputdir cad/Enclosure/slice/v1.4 --export-3mf Enclosure-full-enclosure-v1.4-Orca-complete.3mf cad/Enclosure/Enclosure-v1.4-Orca-input.3mf
python cad/Enclosure/check_nut_pause.py
python cad/Enclosure/verify_print.py
```

The two slice checks default to `Enclosure/slice/v1.4/`.
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

## Two-port enclosure

Build from the v1.4 model with FreeCAD's Python interpreter. Package the seven exported parts with Python and NumPy to create an unsliced OrcaSlicer project with the three-nut pause.

```sh
python cad/Enclosure/TwoPort/build.py --output cad/Enclosure/print/two-port/Enclosure-two-port.FCStd --print-directory cad/Enclosure/print/two-port
python cad/Enclosure/TwoPort/make_project.py cad/Enclosure/print/two-port cad/Enclosure/print/two-port/TwoPort-Orca-input.3mf
```

## Optional male fit tests

The verified v1.3 design has `male_pressure_pad_enabled=false`: the small central tier is omitted and the wider step remains. Its disabled parameters and construction reference are retained for reproducible geometry checks. The cradle has 1.5 mm extra depth, side-tab pockets remain open underneath, and the 22.8 mm internal shoulder pocket leaves nominal 1.9 mm side walls.

Fit-test outputs are disposable working files and are not retained releases. Regenerate them only when needed.

After building, checking, and packaging the current enclosure meshes, run:

```sh
python cad/Enclosure/create_3mf.py --fit-test
mkdir -p cad/Enclosure/slice/v1.4-fit-test
orca-slicer --slice 0 --outputdir cad/Enclosure/slice/v1.4-fit-test --export-3mf Enclosure-v1.4-fit-test-Orca-complete.3mf cad/Enclosure/Enclosure-v1.4-fit-test-Orca-input.3mf
python cad/Enclosure/verify_print.py --fit-test
```

This creates one plate containing the lower alignment gauge and four production keepers, with no supports or pauses.
The verification checks the exact meshes, their placement, all five expected part identities, and the exported G-code.
Promote the checked 3MF from the slice directory to `Enclosure/`.
Regenerate the full-enclosure 3MF too whenever a keeper changes, so both projects use the same parts.

For a compact assembled clamping test, extract one complete production seat and pair it with keeper 2:

```sh
python cad/Enclosure/build_single_port.py
python cad/Enclosure/check_mesh.py
python cad/Enclosure/package_print.py
python cad/Enclosure/create_3mf.py --single-port
mkdir -p cad/Enclosure/slice/v1.4-single-port
orca-slicer --slice 0 --outputdir cad/Enclosure/slice/v1.4-single-port --export-3mf Enclosure-v1.4-single-port-Orca-complete.3mf cad/Enclosure/Enclosure-v1.4-single-port-Orca-input.3mf
python cad/Enclosure/verify_print.py --single-port
```

The extraction checks complete post and collar coverage, connector/keeper clearances, vertical installation, axial/lift retention, and absence of the disabled pad tier.
It also saves `Enclosure-single-port-v1.4.FCStd`. Regenerate the test base after changes to the enclosure; print verification checks its source model hash.

For a contour check only, generate and verify production keeper 2 without its seat:

```sh
python cad/Enclosure/create_3mf.py --single-keeper
mkdir -p cad/Enclosure/slice/v1.4-single-keeper
orca-slicer --slice 0 --outputdir cad/Enclosure/slice/v1.4-single-keeper --export-3mf Enclosure-v1.4-single-keeper-Orca-complete.3mf cad/Enclosure/Enclosure-v1.4-single-keeper-Orca-input.3mf
python cad/Enclosure/verify_print.py --single-keeper
```

This uses the unchanged production mesh and checks that exactly one keeper is present, with no supports or pauses.
It tests contour fit; an assembled clamping test also requires the lower seat.

## Soldering jig

The jig's fixture dimensions are in [SolderingJig/build.py](SolderingJig/build.py).
It reads the stripped male body and plug dimensions from `Enclosure/parameters.json` and uses the original female STEP.
Both builds generate the male D profile with its flat up; no stripped-body scan is required.

Run the build, checks, and slicer in this order:

```sh
python cad/SolderingJig/build.py
python cad/SolderingJig/check_fit.py
python cad/SolderingJig/create_3mf.py
mkdir -p cad/SolderingJig/slice/v1.3
orca-slicer --slice 0 --outputdir cad/SolderingJig/slice/v1.3 --export-3mf N64-Soldering-Jig-v1.3.3mf cad/SolderingJig/N64-Soldering-Jig-v1.3-input.3mf
python cad/SolderingJig/verify_print.py
```

The build and fit check cover solid validity, assembly interference, connector retention and rotation, clamp insertion, and terminal access.
The print check covers mesh geometry, layout, watertightness, and the absence of supports or pauses.
It accepts `--slice-dir PATH`, as the enclosure print check does.

## References and releases

The parent female connector STEP is the only external construction geometry for the current enclosure.
The enclosure build copies the optional embedded console display meshes from the retained release, including their original placements.
It needs no historical scans, measurement reports, or revision folders.
This overlay is approximate.
It does not give a new console-clearance check after design changes.

Git ignores working STL/STEP exports, ZIPs, input 3MFs, reports, and slice directories.
The project retains named FreeCAD release models and sliced 3MFs.

To make a release:

1. Review the geometry and sliced project.
2. Mark the release as a fit prototype until its physical changes have been tested.
3. Explicitly save a new named FreeCAD release.
4. Promote its checked sliced 3MF.
5. Update versioned filenames in the scripts and documentation.

New parameters saved in a FreeCAD document alone do not regenerate the solids.

## v1.3 release record and cleanup

The owner confirmed the full enclosure print on 2026-09-25. The exact retained model and 3MF hashes are in [V1.3-VALIDATION.md](V1.3-VALIDATION.md). The owner also marked soldering jig v1.3 verified on the same date.

The fit history established the side-tab pockets, 7 mm axial shoulder relief, stronger keeper side walls and 1.5 mm deeper cradle. Removing the small central tier gave the successful clamping fit. Those final dimensions remain in the source; intermediate fit2/fit3/fit4 projects and previews are discarded.

Keep release FreeCAD models, sliced 3MFs, source, parameters, reference STEP files and documentation. Remove generated STL/STEP exports, unsliced projects, test fixtures, logs, backups, reports, ZIPs and `print/` / `slice/` directories after recording release evidence. Preserve previously retained releases.

Build and check scripts deliberately describe newly generated geometry as unverified; a code check cannot establish physical fit. The prototype status embedded in the retained v1.3 model predates its successful test. Do not rebuild or reslice a verified file merely to change its status label. Geometry changes need a new version and physical test.

## v1.4 side closure placement

The outer closure fasteners move from Y = 2 to Y = −13.8 mm at X = ±79.5 mm. The side outline at each bolt's X position spans Y ≈ −40.90 to +13.36 mm, giving a midpoint of −13.77 mm. The rounded placement is within 0.05 mm of that midpoint. `check_side_closure.py` verifies the centring, open bores, filled old underside holes, unchanged hardware references and changes restricted to the old/new fastener regions and upper-shell gap additions.

The new boss position changes local clearance around the outer male keepers. Verify the complete assembly and nut pause after generating the new slice; do not overwrite the verified v1.3 files. The soldering jig remains at verified v1.3.

### Upper-shell collar gap fill

`inter_port_gap_fill=true` joins the paired collar wall skins across unused 0.84 mm male-row and 1.30 mm female-row slots. `gap_fills.py` supplies four upper-shell bridges, two in each row. They overlap the existing wall skins by 0.05 mm and are clipped to the outer shell. The final nominal ribs are 1.0 mm and 1.66 mm wide; the keeper service openings retain their original dimensions. `check_gap_fills.py` verifies solid ribs, unchanged exterior and clear keeper removal paths. The base and separate printed parts do not change in this tweak.

## v1.4 release record

The owner confirmed v1.4 as verified on 2026-09-25, including the relocated side fasteners and filled upper-shell ribs. The exact retained model and sliced project hashes are recorded in [V1.4-VALIDATION.md](V1.4-VALIDATION.md). Working exports, previews, reports, backups and slice folders were removed using the same release layout as v1.3.

The saved model’s prototype label predates physical confirmation. Keep the tested files unchanged; build/check status describes newly generated geometry rather than certifying future edits. The verified soldering jig remains v1.3.
