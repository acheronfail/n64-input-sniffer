"""Package the generated two-port meshes with the v1.4 OrcaSlicer profile."""

import argparse
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

import numpy as np

HERE = Path(__file__).resolve().parent
PROFILE = HERE.parent / "Enclosure-full-enclosure-v1.4-Orca-complete.3mf"
CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
TITLE = "N64 input sniffer – two-port enclosure"
PARTS = {
    "LowerShell": (74, 84),
    "UpperShell": (176, 84),
    "MalePortKeeper1": (65, 157),
    "MalePortKeeper2": (105, 157),
    "FemalePortKeeper1": (145, 157),
    "FemalePortKeeper2": (185, 157),
    "LEDWindow": (128, 128),
}
PLATE_OFFSET = 307.2
STL_TRIANGLE = np.dtype([("normal", "<f4", 3), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")])


def metadata(parent, key, value):
    return ET.SubElement(parent, "metadata", key=key, value=str(value))


def core(parent, tag, **attrs):
    return ET.SubElement(parent, f"{{{CORE}}}{tag}", **attrs)


def xml(element):
    return ET.tostring(element, encoding="utf-8", xml_declaration=True)


def make_project(mesh_directory, output):
    with zipfile.ZipFile(PROFILE) as source:
        settings = json.loads(source.read("Metadata/project_settings.config"))
    settings["project_name"] = TITLE
    assert settings["initial_layer_print_height"] == "0.2" and settings["layer_height"] == "0.16"
    assert settings["print_sequence"] == "by layer"

    ET.register_namespace("", CORE)
    model = ET.Element(f"{{{CORE}}}model", unit="millimeter")
    core(model, "metadata", name="Application").text = "OrcaSlicer-2.4.2"
    core(model, "metadata", name="BambuStudio:3mfVersion").text = "1"
    core(model, "metadata", name="Title").text = TITLE
    resources = core(model, "resources")
    build = core(model, "build")

    config = ET.Element("config")
    plates = []
    for number, plate_name in enumerate(("Enclosure – insert 3 M2 nuts at pause",
                                         "Status LED window – translucent PETG"), 1):
        plate = ET.Element("plate")
        for key, value in {
            "plater_id": number, "plater_name": plate_name,
            "locked": "false", "bed_type": settings["curr_bed_type"],
            "filament_map_mode": "Auto For Flush", "gcode_file": "",
        }.items():
            metadata(plate, key, value)
        plates.append(plate)

    for obj_id, (name, (x, y)) in enumerate(PARTS.items(), 1):
        translucent = name == "LEDWindow"
        if translucent:
            x += PLATE_OFFSET
        filename = f"{name}.stl"
        raw = np.fromfile(mesh_directory / filename, dtype=STL_TRIANGLE, offset=84)
        points, indices = np.unique(raw["vertices"].reshape(-1, 3), axis=0, return_inverse=True)
        obj = core(resources, "object", id=str(obj_id), type="model", name=name)
        mesh = core(obj, "mesh")
        vertices = core(mesh, "vertices")
        for vx, vy, vz in points:
            core(vertices, "vertex", x=f"{vx:.9g}", y=f"{vy:.9g}", z=f"{vz:.9g}")
        faces = core(mesh, "triangles")
        for a, b, c in indices.reshape(-1, 3):
            core(faces, "triangle", v1=str(a), v2=str(b), v3=str(c))
        core(build, "item", objectid=str(obj_id), transform=f"1 0 0 0 1 0 0 0 1 {x} {y} 0")

        part_config = ET.SubElement(config, "object", id=str(obj_id))
        metadata(part_config, "name", name)
        metadata(part_config, "extruder", 3 if translucent else 5)
        part = ET.SubElement(part_config, "part", id=str(obj_id), subtype="normal_part")
        metadata(part, "name", name)
        metadata(part, "source_file", filename)
        instance = ET.SubElement(plates[int(translucent)], "model_instance")
        for key, value in {"object_id": obj_id, "instance_id": 0, "identify_id": 100 + obj_id}.items():
            metadata(instance, key, value)
    config.extend(plates)

    pauses = ET.Element("custom_gcodes_per_layer")
    pause_plate = ET.SubElement(pauses, "plate")
    ET.SubElement(pause_plate, "plate_info", id="1")
    # Roof-down pocket is 11.1–13.1 mm above the bed. At the pause, 1.9 mm
    # is available above the pocket floor and the cap has yet to print.
    ET.SubElement(pause_plate, "layer", top_z="13.16", type="1", extruder="1", color="",
                  extra="Insert three M2 nuts fully into the upper-shell pockets and resume.",
                  gcode=settings["machine_pause_gcode"])
    ET.SubElement(pause_plate, "mode", value="SingleExtruder")

    types = ET.Element("Types", xmlns="http://schemas.openxmlformats.org/package/2006/content-types")
    for ext, media in (("model", "application/vnd.ms-package.3dmanufacturing-3dmodel+xml"),
                       ("rels", "application/vnd.openxmlformats-package.relationships+xml"),
                       ("config", "application/octet-stream"), ("xml", "application/xml")):
        ET.SubElement(types, "Default", Extension=ext, ContentType=media)
    relationships = ET.Element("Relationships", xmlns=REL)
    ET.SubElement(relationships, "Relationship", Target="/3D/3dmodel.model", Id="rel-1",
                  Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as project:
        for filename, element in {
            "[Content_Types].xml": types,
            "_rels/.rels": relationships,
            "3D/3dmodel.model": model,
            "Metadata/model_settings.config": config,
            "Metadata/custom_gcode_per_layer.xml": pauses,
        }.items():
            project.writestr(filename, xml(element))
        project.writestr("Metadata/project_settings.config", json.dumps(settings, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesh_directory", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    make_project(args.mesh_directory, args.output)
