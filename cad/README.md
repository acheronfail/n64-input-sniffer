# CAD workspace

The current version is **v0.16**. Open [N64InputMod/N64InputMod-v0.16.FCStd](N64InputMod/N64InputMod-v0.16.FCStd). The unversioned `N64InputMod.FCStd` contains the same model data at this commit (the archive metadata differs).

See [model notes](N64InputMod/README.md) for dimensions, validation, regeneration and assembly, and [v0.16 print instructions](N64InputMod/print/full-enclosure-v0.16/PRINT-AND-ASSEMBLE.md). The versioned Orca-complete 3MF includes the saved slicer project and sliced plates.

## Working on the next iteration

Keep connector STEP references here, one level above `N64InputMod/`. Edit `N64InputMod/parameters.json` and run `N64InputMod/build.FCMacro` in FreeCAD to regenerate; retain the scripts, macros and reference geometry with the model. See the model notes before rebuilding because building writes the current model and exports.

Full-resolution console scans are stored losslessly as gzip files to keep individual Git files below 100 MiB. Before running `prepare_reference.py` or full-resolution scan checks, unpack from the repository root:

```sh
gzip -dk cad/N64InputMod/reference/Top.stl.gz
gzip -dk cad/N64InputMod/reference/Bottom.stl.gz
```

The unpacked originals already exist in the migrated workspace and are ignored. The aligned display meshes are tracked directly.

Save named FreeCAD and 3MF versions, refresh the applicable print exports and assembly notes, review `git status` and the diff, then commit each iteration. v0.16 is the baseline for continued work. Existing versioned models, print packages, previews, validation reports and `revisions/` snapshots preserve the earlier iteration history in this initial import. Historical snapshots are preserved as recorded and may contain old absolute paths; use the current scripts for ongoing work.

Backups, caches, logs and temporary completion/error markers remain local and ignored. STEP/STL geometry, FCStd models, 3MF projects, ZIP print packages, parameters, scripts, macros, documentation and saved validation reports are tracked.

## Soldering jig

The separate [one-pair soldering jig](SolderingJig/README.md) holds a male and female connector with their terminals facing an open central area. Its three-part [print-ready 3MF](SolderingJig/N64-Soldering-Jig-v1.3mf) needs four 2 mm × 8 mm countersunk plastic screws and no supports or pauses.
