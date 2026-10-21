#!/usr/bin/env python3
"""Generate and validate small, deterministic STL fixtures using only the stdlib."""

import argparse
from collections import defaultdict, deque
import hashlib
import json
import math
from pathlib import Path
import struct


TOWER_NAME = "prefect_progress_tower_80x80x150.stl"
EXPECTED_SHA256 = {
    "prefect_cube_A.stl": "5FA22B3FED7383F25032A1B666F5CEE1EA62BD3C215B4AED8798605A2C3E4FFD",
    "prefect_cube_B.stl": "706D2555F81895164EF0F67FAAE8487F40477C6A288E48940F1FC0EE1839C69A",
    TOWER_NAME: "94D3A32A466575781A43C532B951B1D9C2E6BC6F3D8F52A3C4DA73CF2AAFEC45",
}
BOX_FACES = (
    (0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
    (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
    (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7),
)


def require(condition, message):
    """Keep validation active even when Python is invoked with -O."""
    if not condition:
        raise ValueError(message)


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def length(vector):
    return math.sqrt(dot(vector, vector))


def box_vertices(x0, x1, y0, y1, height):
    return ((x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0),
            (x0, y0, height), (x1, y0, height),
            (x1, y1, height), (x0, y1, height))


def cube_bytes(name):
    vertices = box_vertices(0, 20, 0, 20, 20)
    lines = ["solid " + name]
    for face in BOX_FACES:
        # Preserve the original acceptance cubes, including their unspecified normals.
        lines.extend(("facet normal 0 0 0", "outer loop"))
        lines.extend("vertex " + " ".join(map(str, vertices[index])) for index in face)
        lines.extend(("endloop", "endfacet"))
    lines.append("endsolid " + name)
    # Explicit bytes preserve the Windows originals on every host OS.
    return ("\r\n".join(lines) + "\r\n").encode("ascii")


def tower_bytes():
    coordinates = (0, 5, 15, 20, 30, 35, 45, 50, 60, 65, 75, 80)
    cells = {(i, j) for i in range(11) for j in range(11)
             if not (i % 2 == 1 and j % 2 == 1)}
    triangles = []
    for i, j in sorted(cells):
        vertices = box_vertices(*coordinates[i:i + 2], *coordinates[j:j + 2], 150)
        faces = list(BOX_FACES[:4])
        sides = (((i, j - 1), BOX_FACES[4:6]),
                 ((i + 1, j), BOX_FACES[6:8]),
                 ((i, j + 1), BOX_FACES[8:10]),
                 ((i - 1, j), BOX_FACES[10:12]))
        for neighbor, side in sides:
            if neighbor not in cells:
                faces.extend(side)
        triangles.extend(tuple(vertices[index] for index in face) for face in faces)
    header = b"Prefect offline progress tower 80x80x150 mm; 25 vertical holes"
    raw = bytearray(header.ljust(80, b" "))
    raw.extend(struct.pack("<I", len(triangles)))
    for a, b, c in triangles:
        normal = cross(subtract(b, a), subtract(c, a))
        normal = tuple(value / length(normal) for value in normal)
        raw.extend(struct.pack("<12fH", *normal, *a, *b, *c, 0))
    return bytes(raw)


def decode_cube(raw, name):
    lines = raw.decode("ascii").splitlines()
    require(len(lines) == 86, "Unexpected cube STL line count")
    require(lines[0] == "solid " + name and lines[-1] == "endsolid " + name,
            "Unexpected cube solid name")
    triangles, normals = [], []
    for index in range(1, len(lines) - 1, 7):
        block = lines[index:index + 7]
        require(block[0] == "facet normal 0 0 0" and block[1] == "outer loop"
                and block[5:] == ["endloop", "endfacet"], "Invalid cube facet syntax")
        require(all(line.startswith("vertex ") for line in block[2:5]),
                "Invalid cube vertex syntax")
        triangle = tuple(tuple(map(float, line.split()[1:])) for line in block[2:5])
        require(all(len(vertex) == 3 for vertex in triangle), "Invalid vertex dimensions")
        triangles.append(triangle)
        normals.append((0.0, 0.0, 0.0))
    return triangles, normals


def decode_tower(raw):
    require(len(raw) >= 84, "Truncated binary STL")
    count = struct.unpack_from("<I", raw, 80)[0]
    require(count == 672 and len(raw) == 84 + 50 * count, "Invalid binary STL size")
    triangles, normals = [], []
    for index in range(count):
        record = struct.unpack_from("<12fH", raw, 84 + 50 * index)
        require(record[-1] == 0, "Unexpected STL attribute data")
        normals.append(record[:3])
        triangles.append(tuple(tuple(record[i:i + 3]) for i in (3, 6, 9)))
    return triangles, normals


def section_areas(triangles, height):
    """Intersect decoded triangles independently, then trace every closed contour."""
    graph = defaultdict(set)
    for triangle in triangles:
        points = []
        for a, b in zip(triangle, triangle[1:] + triangle[:1]):
            if min(a[2], b[2]) < height < max(a[2], b[2]):
                fraction = (height - a[2]) / (b[2] - a[2])
                points.append(tuple(a[k] + fraction * (b[k] - a[k]) for k in (0, 1)))
        if points:
            require(len(points) == 2 and points[0] != points[1], "Invalid section segment")
            a, b = points
            graph[a].add(b)
            graph[b].add(a)
    require(graph and all(len(neighbors) == 2 for neighbors in graph.values()),
            "Section is not a collection of closed contours")
    visited, areas = set(), []
    for start in sorted(graph):
        if start in visited:
            continue
        loop, previous, current = [], None, start
        while current not in visited:
            visited.add(current)
            loop.append(current)
            following = next(point for point in sorted(graph[current]) if point != previous)
            previous, current = current, following
        require(current == start, "Section contour does not close")
        areas.append(abs(sum(a[0] * b[1] - b[0] * a[1]
                             for a, b in zip(loop, loop[1:] + loop[:1])) / 2))
    return sorted(areas)


def validate(raw, filename):
    is_tower = filename == TOWER_NAME
    triangles, normals = (decode_tower(raw) if is_tower
                          else decode_cube(raw, Path(filename).stem))
    edges, vertices, unique_faces = defaultdict(list), set(), set()
    area, volume, zero_normals = 0.0, 0.0, 0
    for index, (triangle, normal) in enumerate(zip(triangles, normals)):
        a, b, c = triangle
        require(all(math.isfinite(value) for vertex in triangle for value in vertex)
                and all(math.isfinite(value) for value in normal), "Non-finite STL value")
        geometric_normal = cross(subtract(b, a), subtract(c, a))
        magnitude = length(geometric_normal)
        require(magnitude > 0, "Degenerate triangle")
        if length(normal) == 0:
            require(not is_tower, "Tower facet has no normal")
            zero_normals += 1
        else:
            require(abs(length(normal) - 1) < 1e-7 and
                    max(abs(normal[k] - geometric_normal[k] / magnitude)
                        for k in range(3)) < 1e-7, "Incorrect outward facet normal")
        key = tuple(sorted(triangle))
        require(key not in unique_faces, "Duplicate triangle")
        unique_faces.add(key)
        vertices.update(triangle)
        area += magnitude / 2
        volume += dot(a, cross(b, c)) / 6
        for u, v in zip(triangle, triangle[1:] + triangle[:1]):
            edges[tuple(sorted((u, v)))].append((index, u, v))
    adjacency = defaultdict(set)
    for uses in edges.values():
        require(len(uses) == 2, "Non-manifold or open edge")
        a, b = uses
        require(a[1] == b[2] and a[2] == b[1], "Inconsistent surface orientation")
        adjacency[a[0]].add(b[0])
        adjacency[b[0]].add(a[0])
    visited, queue = {0}, deque([0])
    while queue:
        for neighbor in adjacency[queue.popleft()]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    require(len(visited) == len(triangles), "Disconnected mesh")
    bbox = [[min(vertex[k] for vertex in vertices) for k in range(3)],
            [max(vertex[k] for vertex in vertices) for k in range(3)]]
    expected_bbox = [[0, 0, 0], [80, 80, 150] if is_tower else [20, 20, 20]]
    counts = (len(vertices), len(edges), len(triangles))
    require(bbox == expected_bbox, "Unexpected bounding box")
    require(counts == ((288, 1008, 672) if is_tower else (8, 18, 12)),
            "Unexpected mesh counts")
    require(abs(volume - (585000 if is_tower else 8000)) < 1e-6,
            "Unexpected volume or inward orientation")
    require(abs(area - (205800 if is_tower else 2400)) < 1e-6, "Unexpected surface area")
    euler = counts[0] - counts[1] + counts[2]
    require(euler == (-48 if is_tower else 2), "Unexpected Euler characteristic")
    areas = section_areas(triangles, 75 if is_tower else 10)
    require(areas == ([100.0] * 25 + [6400.0] if is_tower else [400.0]),
            "Unexpected midplane contours")
    digest = hashlib.sha256(raw).hexdigest().upper()
    require(digest == EXPECTED_SHA256[filename], "Fixture bytes differ from acceptance reference")
    return {"file": filename, "bytes": len(raw), "sha256": digest,
            "bbox_mm": [[int(value) for value in corner] for corner in bbox],
            "vertices": counts[0], "edges": counts[1], "facets": counts[2],
            "connected_components": 1, "watertight": True, "outward_orientation": True,
            "unspecified_zero_normals": zero_normals, "volume_mm3": round(volume, 6),
            "surface_area_mm2": round(area, 6), "euler_characteristic": euler,
            "genus": (2 - euler) // 2, "midplane_closed_contours": len(areas)}


def write_identical_or_new(path, raw):
    if path.exists():
        require(path.is_file() and path.read_bytes() == raw,
                "Existing file differs; choose another --output-dir: " + str(path))
    else:
        path.write_bytes(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path,
                        help="Destination for three STL files and their deterministic manifest")
    args = parser.parse_args()
    fixtures = {name + ".stl": cube_bytes(name)
                for name in ("prefect_cube_A", "prefect_cube_B")}
    fixtures[TOWER_NAME] = tower_bytes()
    reports = [validate(raw, name) for name, raw in fixtures.items()]
    manifest = (json.dumps({"format_version": 1, "units": "mm", "fixtures": reports},
                           indent=2, sort_keys=True) + "\n").encode("utf-8")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = dict(fixtures)
    outputs["gui-fixtures.json"] = manifest
    # Preflight every path so a conflicting output does not leave a partial set.
    for name, raw in outputs.items():
        path = args.output_dir / name
        require(not path.exists() or (path.is_file() and path.read_bytes() == raw),
                "Existing file differs; choose another --output-dir: " + str(path))
    for name, raw in outputs.items():
        path = args.output_dir / name
        write_identical_or_new(path, raw)
        require(path.read_bytes() == raw, "Output readback mismatch: " + str(path))
    for report in reports:
        print("{file}: {bytes} bytes, {facets} facets, SHA256 {sha256}".format(**report))
    print("Manifest: " + str(args.output_dir / "gui-fixtures.json"))


if __name__ == "__main__":
    main()
