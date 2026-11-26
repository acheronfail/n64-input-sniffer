"""Build the ports 1–2 enclosure from the physically verified v1.4 solids."""

import argparse
from itertools import combinations
from pathlib import Path
import json
import math

import FreeCAD as App
import Mesh
import Part

V = App.Vector
HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent / "Enclosure-v1.4.FCStd"

# N64 console datum from v1.4. +Y faces the console, +X faces port 3.
SIDE_X = -8.8
JOIN_X = -21.6
BOTTOM, FLOOR = -13.1, -11.02
ROOF, TOP = 13.05, 15.1
SEAM = 0.16
SCREWS = ((-79.5, -13.8), (-49.9, -39.0), (-13.0, -37.0))
BOARD_X = -18.3  # back face of the PCB, with the components toward +X
BOARD_Y = 6.50  # USB-side edge of the PCB
BOARD_LENGTH = 24.52
BOARD_END_CLEARANCE = 0.20
WINDOW_Y = -8.2
WINDOW_Z = -0.3
EPSILON = 0.005

SHELL = (0.25, 0.29, 0.36)
LID = (0.36, 0.42, 0.51)
MALE_KEEPER = (0.30, 0.58, 0.78)
FEMALE_KEEPER = (0.32, 0.66, 0.65)
CONNECTOR = (0.17, 0.18, 0.21)
PCB = (0.14, 0.48, 0.35)
METAL = (0.74, 0.76, 0.79)


def box(xmin, xmax, ymin, ymax, zmin, zmax):
    return Part.makeBox(xmax - xmin, ymax - ymin, zmax - zmin, V(xmin, ymin, zmin))


def band(zmin, zmax, xmin=-100, xmax=0):
    return box(xmin, xmax, -70, 35, zmin, zmax)


def fuse(*shapes):
    return shapes[0].multiFuse(shapes[1:]).removeSplitter()


def volume(shape):
    return 0.0 if shape.isNull() or not shape.Solids else shape.Volume


def assert_clear(name, a, b):
    overlap = volume(a.common(b))
    assert overlap < EPSILON, f"{name}: {overlap:.4f} mm³ of interference"


def assert_solid(name, shape):
    assert len(shape.Solids) == 1 and shape.isValid(), f"{name} is not one valid solid"


def vertical_cylinder(x, y, zmin, zmax, radius):
    return Part.makeCylinder(radius, zmax - zmin, V(x, y, zmin))


def cap_outline(right, front, rear, radius, z):
    """Keep the inherited left contour and round the corners at the new end."""
    points = [
        V(-100, -65, z), V(right - radius, -65, z), V(right - radius, front, z),
        V(right, front + radius, z), V(right, rear - radius, z),
        V(right - radius, rear, z), V(right - radius, 25, z), V(-100, 25, z),
    ]
    d = radius / math.sqrt(2)
    mid = {
        2: V(right - radius + d, front + radius - d, z),
        4: V(right - radius + d, rear - radius + d, z),
    }
    edges = [
        Part.Arc(a, mid[i], b).toShape() if i in mid else Part.makeLine(a, b)
        for i, (a, b) in enumerate(zip(points, points[1:] + points[:1]))
    ]
    return Part.Wire(edges)


def shell_stock(reference):
    old_outer = reference.OuterContourLoft.Shape
    old_inner = reference.InteriorLoft.Shape
    # Relocate the original ruled-loft profiles while preserving the original
    # connector-facing profile between the bevels.
    profiles = []
    for old_z, new_z in ((-16, BOTTOM), (-13.5, BOTTOM + 2.5),
                         (13, TOP - 3), (16, TOP)):
        if old_z == -16:
            wire = next(f.OuterWire for f in old_outer.Faces if abs(f.BoundBox.ZMax + 16) < 1e-6)
        else:
            wire, = old_outer.slice(V(0, 0, 1), old_z)
        profiles.append(wire.translated(V(0, 0, new_z - old_z)))
    outline = Part.makeLoft(profiles, True, True)
    limit = Part.makeLoft([
        cap_outline(x, -44.70, 9.35, 4.5, z)
        for x, z in [(SIDE_X - 1.8, BOTTOM), (SIDE_X, BOTTOM + 2.5),
                     (SIDE_X, TOP - 2.5), (SIDE_X - 1.8, TOP)]
    ], True, True)
    outer = outline.common(limit).removeSplitter()
    inner_profile = cap_outline(SIDE_X - 2.4, -42.30, 6.95, 2.1, FLOOR)
    inner_limit = Part.Face(inner_profile).extrude(V(0, 0, ROOF - FLOOR))
    inner = old_inner.common(inner_limit)
    return outer, outer.cut(inner).removeSplitter()


def rounded_opening(center, axis, depth, width, height, radius):
    """A rounded Y/Z or X/Z profile extruded along X or Y."""
    along_x = axis.x > 0
    u = V(0, 1, 0) if along_x else V(1, 0, 0)
    w, h = width / 2, height / 2
    diag = radius / math.sqrt(2)
    z = V(0, 0, 1)

    def point(a, b):
        return center + u * a + z * b

    corners = [
        (-w + radius, -h), (w - radius, -h), (w, -h + radius), (w, h - radius),
        (w - radius, h), (-w + radius, h), (-w, h - radius), (-w, -h + radius),
    ]
    midpoints = {
        1: (w - radius + diag, -h + radius - diag),
        3: (w - radius + diag, h - radius + diag),
        5: (-w + radius - diag, h - radius + diag),
        7: (-w + radius - diag, -h + radius - diag),
    }
    ends = [point(*p) for p in corners]
    edges = [
        Part.Arc(a, point(*midpoints[i]), b).toShape() if i in midpoints else Part.makeLine(a, b)
        for i, (a, b) in enumerate(zip(ends, ends[1:] + ends[:1]))
    ]
    return Part.Face(Part.Wire(edges)).extrude(axis * depth)


def board_shapes():
    """Keep the USB and LED positions while allowing for the longer board."""
    def pcb_box(xmin, xmax, near, far, zmin, zmax):
        return box(BOARD_X + xmin, BOARD_X + xmax, BOARD_Y - far, BOARD_Y - near, zmin, zmax)

    board = pcb_box(0, 1.6, 0, BOARD_LENGTH, -9, 9)
    components = pcb_box(1.6, 4.6, 7, 19, -6.5, 6.5)
    usb = pcb_box(1.6, 4.8, -1.7, 5.7, -4.6, 4.6)

    # A top-loaded pocket contacts the corners and the ends, leaving the
    # component side and solder-pad rows open with the upper shell removed.
    corners = [(-1.25, 1.55), (BOARD_LENGTH - 1.55, BOARD_LENGTH + 1.38)]
    near = -BOARD_END_CLEARANCE
    far = BOARD_LENGTH + BOARD_END_CLEARANCE
    low_slot = pcb_box(-0.20, 1.80, near, far, -9, 0)
    high_slot = pcb_box(-0.20, 1.80, near, far, 4, 9.25)
    blocks = [
        pcb_box(-3.0, 3.2, a, b, FLOOR - 0.12, -6.85).cut(low_slot)
        for a, b in corners
    ]
    stops = [
        pcb_box(-2.9, 3.2, a, b, 7.2, ROOF + 0.16).cut(high_slot)
        for a, b in corners
    ]

    opening = rounded_opening(V(BOARD_X + 3.2, 5.8, 0), V(0, 1, 0), 6.0, 4.4, 10.2, 0.7)
    return board, components, usb, blocks, stops, opening


def led_window():
    """A shallow flanged diffuser captured in the sidewall by the two shell halves."""
    def profile(x, depth, width, height, radius):
        return rounded_opening(V(x, WINDOW_Y, WINDOW_Z), V(1, 0, 0), depth, width, height, radius)

    rim = profile(SIDE_X - 3.4, 1.6, 19.2, 18.3, 2.75)
    aperture = profile(SIDE_X - 1.8, 2.8, 15.3, 14.4, 1.7)
    recess = profile(SIDE_X - 2.65, 1.10, 17.5, 16.6, 2.4)
    bore = profile(SIDE_X - 4.0, 1.65, 14.0, 13.1, 1.55)
    # The outside sits slightly recessed and has clearance from the printed shell.
    flange = profile(SIDE_X - 2.35, 0.65, 17.05, 16.15, 2.2)
    face = profile(SIDE_X - 1.75, 1.60, 14.88, 13.98, 1.5)
    return rim, fuse(aperture, recess, bore), fuse(flange, face)


def nut_hexagon(index, x, y, z, height, across_flats=4.3):
    radius = across_flats / math.sqrt(3)
    angle = math.pi / 2 if index == 1 else 0
    corners = [
        V(x + radius * math.cos(angle + k * math.pi / 3),
          y + radius * math.sin(angle + k * math.pi / 3), z)
        for k in range(6)
    ]
    return Part.Face(Part.makePolygon(corners + corners[:1])).extrude(V(0, 0, height))


def closure(lower, upper, outer):
    for index, (x, y) in enumerate(SCREWS):
        if index:
            # Full-height pillars, clipped to the original-fit outside shape.
            boss = vertical_cylinder(x, y, BOTTOM, TOP, 4.2).common(outer)
            if index == 1:
                boss = boss.common(band(BOTTOM - 1, TOP + 1, x - 3.15, x + 3.15))
            lower = fuse(lower, boss.common(band(BOTTOM - 1, 0)))
            upper = fuse(upper, boss.common(band(SEAM, TOP + 1)))
        # The same 4.3 mm nut pocket as v1.4. A 20 mm screw ends at Z=6.9.
        lower = lower.cut(vertical_cylinder(x, y, BOTTOM - 1, 0.10, 1.1))
        lower = lower.cut(Part.makeCone(2.1, 1.1, 1.0, V(x, y, BOTTOM)))
        upper = upper.cut(vertical_cylinder(x, y, 0, 7.5, 1.1))
        upper = upper.cut(nut_hexagon(index, x, y, 2, 2))

    # The left registration pin is inherited. The right pin locates the board-side seam.
    x, y = SIDE_X - 2.45, -20.0
    pad = vertical_cylinder(x, y, -3.1, 3.0, 2.1)
    lower = fuse(lower, pad.common(band(-3.2, 0)),
                 vertical_cylinder(x, y, -0.1, 2.4, 0.95))
    upper = fuse(upper, pad.common(band(SEAM, 3.1)))
    upper = upper.cut(vertical_cylinder(x, y, 0, 2.6, 1.15))
    return lower.removeSplitter(), upper.removeSplitter()


def build(doc, reference):
    def group(name, label):
        obj = doc.addObject("App::DocumentObjectGroup", name)
        obj.Label = label
        return obj

    print_parts = group("PrintParts", "01 · Print parts")
    hardware = group("Hardware", "02 · Ports and electronics")
    console = group("Console", "03 · N64 display scan (approximate)")

    def feature(target, name, label, shape, color):
        obj = doc.addObject("Part::Feature", name)
        obj.Label = label
        obj.Shape = shape
        target.addObject(obj)
        if App.GuiUp:
            obj.ViewObject.ShapeColor = color
            obj.ViewObject.LineColor = (0.10, 0.12, 0.15)
            obj.ViewObject.DisplayMode = "Flat Lines"
        return obj

    outer, skin = shell_stock(reference)
    # Only the two verified port bays are inherited. Remove the sliver of the
    # old centre fastener pillars that protrudes into the cropped region.
    old_bosses = [vertical_cylinder(-18, y, -17, 17, 4.3) for y in (-32.7, 3)]
    lower_ports = reference.LowerShell.Shape.cut(old_bosses).common(band(-20, 18, xmax=JOIN_X))
    upper_ports = reference.UpperShell.Shape.cut(old_bosses).common(band(-20, 18, xmax=JOIN_X))
    lower = fuse(lower_ports.common(outer), skin.common(band(BOTTOM - 1, FLOOR + 0.11)),
                 skin.common(band(BOTTOM - 1, 0, xmin=JOIN_X - 0.25)))
    upper = fuse(upper_ports.common(outer), skin.common(band(ROOF - 0.07, TOP + 1)),
                 skin.common(band(SEAM, TOP + 1, xmin=JOIN_X - 0.25)))

    board, components, usb, blocks, stops, opening = board_shapes()
    # Reference envelope for the decoupling capacitor and wiring clearance.
    cap = vertical_cylinder(-16.45, -26.1, -10.72, 5.28, 5.0)
    window_rim, window_cut, window = led_window()
    lower = fuse(lower, *blocks, window_rim.common(band(BOTTOM, 0))).common(outer)
    upper = fuse(upper, *stops, window_rim.common(band(SEAM, TOP))).common(outer)
    lower = lower.cut([opening, window_cut])
    upper = upper.cut([opening, window_cut])
    lower, upper = closure(lower, upper, outer)
    lower = lower.cut([reference.MaleCradleDepthRelief1.Shape,
                       reference.MaleCradleDepthRelief2.Shape]).removeSplitter()

    feature(print_parts, "LowerShell", "Lower shell · ports 1–2", lower, SHELL)
    feature(print_parts, "UpperShell", "Upper shell · ports 1–2", upper, LID)
    feature(print_parts, "LEDWindow", "Translucent side window · print face down", window, (0.50, 0.80, 0.76))
    for i in (1, 2):
        for prefix, color in (("Male", MALE_KEEPER), ("Female", FEMALE_KEEPER)):
            keeper = reference.getObject(f"{prefix}PortKeeper{i}")
            feature(print_parts, keeper.Name, f"{prefix} keeper · port {i}", keeper.Shape, color)
            connector = reference.getObject(f"{prefix}Port{i}")
            feature(hardware, connector.Name, f"{prefix} connector · port {i}", connector.Shape, CONNECTOR)
        tip = reference.getObject(f"MaleMatingProjection{i}")
        feature(hardware, tip.Name, f"N64 mating tip · port {i}", tip.Shape, CONNECTOR)

    feature(hardware, "ESP32Board", "ESP32-S3 Super Mini · vertical mount", board, PCB)
    feature(hardware, "ESP32Components", "ESP32 components · keep-out", components, (0.22, 0.24, 0.25))
    feature(hardware, "USBC", "USB-C receptacle", usb, METAL)

    capacitor = feature(hardware, "CapacitorEnvelope", "100 µF capacitor · Ø10 × 16 mm design envelope", cap,
                        (0.31, 0.34, 0.40))
    if App.GuiUp:
        capacitor.Visibility = False
    for name in ("ConsoleTop", "ConsoleBottom"):
        old = reference.getObject(name)
        obj = doc.addObject("Mesh::Feature", name)
        obj.Mesh = old.Mesh.copy()
        obj.Placement = old.Placement
        console.addObject(obj)
        if App.GuiUp:
            obj.ViewObject.ShapeColor = (0.48, 0.49, 0.53)
            obj.ViewObject.DisplayMode = "Flat Lines"
            obj.Visibility = False


def validate_usb(doc, shell):
    usb = doc.USBC.Shape.optimalBoundingBox()
    x, y = usb.Center.x, usb.YMax
    tip_path = box(x - 1.25, x + 1.25, y, 40, -4.3, 4.3)
    # The shell admits the metal tip and leaves room for a slim cable housing
    # when detached. The seated console occupies that same plug housing space.
    boot_start = y + 1.6
    boot = box(x - 3.2, x + 3.2, boot_start, boot_start + 4, -5.2, 5.2)
    assert_clear("USB plug tip, enclosure detached", shell, tip_path)
    assert_clear("USB plug housing, enclosure detached", shell, boot)

    surface_depths = []
    for dx in (-2, 0, 2):
        for z in (-4, -2, 2, 4):
            hits = [
                point[1]
                for console_half in doc.Console.Group
                for point in console_half.Mesh.nearestFacetOnRay(V(x + dx, y, z), V(0, 1, 0)).values()
            ]
            first = min(hits, default=math.inf)
            assert boot_start < first < boot_start + 4, (
                f"Console reference does not block the slim USB plug at X={x + dx}, Z={z}"
            )
            surface_depths.append(first - y)
    return [round(min(surface_depths), 2), round(max(surface_depths), 2)]


def validate(doc, reference):
    lower, upper = doc.LowerShell.Shape, doc.UpperShell.Shape
    assembled = fuse(lower, upper)
    old = fuse(reference.LowerShell.Shape, reference.UpperShell.Shape)
    measured = assembled.optimalBoundingBox()
    old_size = old.optimalBoundingBox()
    for part in doc.PrintParts.Group:
        assert_solid(part.Name, part.Shape)
        for component in doc.Hardware.Group:
            assert_clear(f"{part.Name} / {component.Name}", part.Shape, component.Shape)
    for a, b in combinations(doc.PrintParts.Group, 2):
        assert_clear(f"{a.Name} / {b.Name}", a.Shape, b.Shape)

    service = [o.Shape for o in doc.PrintParts.Group if o != doc.UpperShell] + [
        doc.ESP32Board.Shape, doc.ESP32Components.Shape, doc.USBC.Shape
    ]
    for height in (0.1, 0.25, 0.75, 1.5, 3, 8, 16, 25):
        lifted = upper.translated(V(0, 0, height))
        for i, fixed in enumerate(service):
            assert_clear(f"Lid lift {height:g} mm, item {i}", lifted, fixed)

    # Keep verified cradle, shoulder capture and female flange seats at both axes.
    # Check the seats and towers above the relocated outer bottom bevel.
    seat_checks = {}
    for port, xmin, xmax in [(1, -76.0, -51.3), (2, -48.6, -23.8)]:
        region = box(xmin, xmax, -46, 14, BOTTOM + 2.51, 11)
        before = reference.LowerShell.Shape.common(region)
        after = lower.common(region)
        missing = volume(before.cut(after))
        assert missing < EPSILON, f"Port {port} has {missing:.4f} mm³ missing from its seats"
        seat_checks[f"port_{port}_missing_seat_mm3"] = missing
        relief = reference.getObject(f"MaleCradleDepthRelief{port}").Shape
        assert_clear(f"Port {port} deep male cradle", lower, relief)
        male = doc.getObject(f"MalePort{port}").Shape.optimalBoundingBox()
        cx, y = male.Center.x, male.YMin
        male_path = box(cx - 6.25, cx + 6.25, y - 4.99, y - 0.01, -4.99, 4.99)
        assert_clear(f"Port {port} male wire path", lower, male_path)
        assert_clear(f"Port {port} male wire path / capacitor", doc.CapacitorEnvelope.Shape, male_path)
        for prefix, axial, movement in (("Male", 0.8, 0.8), ("Female", 0.5, 0.5)):
            keeper = doc.getObject(f"{prefix}PortKeeper{port}").Shape
            original = reference.getObject(f"{prefix}PortKeeper{port}").Shape
            assert volume(original.cut(keeper)) + volume(keeper.cut(original)) < EPSILON
            connector = doc.getObject(f"{prefix}Port{port}").Shape
            capture = fuse(lower, keeper)
            for direction in (V(0, axial, 0), V(0, -axial, 0), V(0, 0, movement)):
                assert volume(capture.common(connector.translated(direction))) > 0.01, (
                    f"{prefix} port {port} is loose in direction {direction}"
                )
        passage = box((-63.7, -36)[port - 1] - 6.39, (-63.7, -36)[port - 1] + 6.39,
                      -28.7, -17.2, -4.99, 4.99)
        assert_clear(f"Port {port} female wire path", lower, passage)
        assert_clear(f"Port {port} female wire path / capacitor", doc.CapacitorEnvelope.Shape, passage)

    for index, (x, y) in enumerate(SCREWS):
        pocket = nut_hexagon(index, x, y, 2.01, 1.98)
        assert_clear(f"Nut {index + 1} pocket", upper, pocket)
        rim = nut_hexagon(index, x, y, 2.01, 1.98, 6.25).cut(pocket)
        assert volume(rim.cut(upper)) < EPSILON, f"Nut {index + 1} side walls"
        for z in (1.24, 4.01):
            seat = nut_hexagon(index, x, y, z, 0.74).cut(
                vertical_cylinder(x, y, z - 0.01, z + 0.76, 1.11)
            )
            assert volume(seat.cut(upper)) < EPSILON, f"Nut {index + 1} bearing surface"
        screw = vertical_cylinder(x, y, BOTTOM, BOTTOM + 20, 1.0)
        assert_clear(f"Screw {index + 1} passage", assembled, screw)

    usb_scan_gap = validate_usb(doc, assembled)
    window = doc.LEDWindow.Shape
    for shift in (-0.65, 0.65):
        assert volume(window.translated(V(shift, 0, 0)).common(assembled)) > 0.1, (
            "LED window is not retained by the sidewall"
        )
    for height in (0, 0.25, 1, 3, 6, 10, 17):
        assert_clear(f"LED window seating {height:g} mm", lower, window.translated(V(0, 0, height)))
    light_path = rounded_opening(V(BOARD_X + 4.9, WINDOW_Y, WINDOW_Z), V(1, 0, 0), 7, 13.5, 12.6, 1.4)
    assert_clear("Status LED viewing aperture", assembled, light_path)

    # Rigid board can be inserted vertically with the lid removed.
    for dz in (0, 0.1, 0.5, 1, 3, 8, 16, 24):
        for item in (doc.ESP32Board, doc.ESP32Components, doc.USBC):
            assert_clear(f"{item.Name} insertion {dz} mm", lower, item.Shape.translated(V(0, 0, dz)))

    # Compare console-facing material outside v1.4 and verify that the next
    # connector's mating tip has a clear axial path to its original seat.
    console_zone = band(-20, 20).common(box(-100, 10, 5, 24, -20, 20))
    protrusion = volume(assembled.common(console_zone).cut(reference.OuterContourLoft.Shape))
    assert protrusion < EPSILON, f"{protrusion:.3f} mm³ beyond the verified console-side envelope"
    for delta in (0, -4, -12, -30, -60):
        assert_clear("Independent port 3 access", assembled,
                     reference.MaleMatingProjection3.Shape.translated(V(0, delta, 0)))

    return {
        "status": "CAD checks passed",
        "shell_size_mm": [round(n, 2) for n in (measured.XLength, measured.YLength, measured.ZLength)],
        "v1_4_shell_size_mm": [round(n, 2) for n in (old_size.XLength, old_size.YLength, old_size.ZLength)],
        "console_side_protrusion_mm3": protrusion,
        "usb_socket_to_console_scan_mm": usb_scan_gap,
        "seat_comparison": seat_checks,
        "printed_volume_cm3": round(sum(o.Shape.Volume for o in doc.PrintParts.Group) / 1000, 2),
    }


def print_mesh(part):
    shape = part.Shape
    if part.Name == "LEDWindow":
        shape = shape.rotated(V(0, 0, 0), V(0, 1, 0), 90)
    elif part.Name != "LowerShell":
        shape = shape.rotated(V(0, 0, 0), V(1, 0, 0), 180)
    b = shape.optimalBoundingBox()
    shape = shape.translated(V(-b.Center.x, -b.Center.y, -b.ZMin))
    mesh = Mesh.Mesh(shape.tessellate(0.045))
    assert mesh.isSolid() and mesh.countComponents() == 1, f"{part.Name} mesh must be closed and connected"
    return mesh


def main(output, print_directory=None):
    reference = App.openDocument(str(REFERENCE))
    doc = App.newDocument("TwoPortEnclosure")
    doc.Label = "N64 input sniffer · two-port enclosure"
    build(doc, reference)
    report = validate(doc, reference)
    if print_directory:
        print_directory.mkdir(parents=True, exist_ok=True)
        for obj in doc.PrintParts.Group:
            print_mesh(obj).write(str(print_directory / f"{obj.Name}.stl"))
        (print_directory / "validation.json").write_text(json.dumps(report, indent=2) + "\n")

    App.closeDocument(reference.Name)
    App.setActiveDocument(doc.Name)
    doc.recompute()
    if App.GuiUp:
        import FreeCADGui as Gui

        Gui.activeDocument().activeView().viewAxonometric()
        Gui.activeDocument().activeView().fitAll()
    doc.saveAs(str(output))
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "Enclosure-two-port.FCStd")
    parser.add_argument("--print-directory", type=Path)
    args = parser.parse_args()
    main(args.output, args.print_directory)
