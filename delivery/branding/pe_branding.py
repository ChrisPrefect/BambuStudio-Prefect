"""Read-only PE version/icon verification using only Python's standard library.

Layouts: https://learn.microsoft.com/windows/win32/debug/pe-format
https://learn.microsoft.com/windows/win32/menurc/stringfileinfo
No executable is loaded or run; every file/RVA/resource read is bounds checked.
"""
from __future__ import annotations
import hashlib
import struct

DISPLAY_NAME = "Prefect Bambu Studio"


class BrandingError(ValueError):
    pass


def check(condition, message):
    if not condition:
        raise BrandingError(message)


def chunk(data, offset, size):
    check(0 <= offset <= len(data) and 0 <= size <= len(data) - offset, "Truncated resource data")
    return data[offset:offset + size]


def u16(data, offset):
    return struct.unpack("<H", chunk(data, offset, 2))[0]


def u32(data, offset):
    return struct.unpack("<I", chunk(data, offset, 4))[0]


def pe_resources(data):
    check(chunk(data, 0, 2) == b"MZ", "Missing DOS signature")
    pe = u32(data, 0x3C)
    check(chunk(data, pe, 4) == b"PE\0\0", "Missing PE signature")
    count, optional_size = u16(data, pe + 6), u16(data, pe + 20)
    check(0 < count <= 128, "Invalid PE section count")
    optional = pe + 24
    magic = u16(data, optional)
    check(magic in (0x10B, 0x20B), "Unsupported PE optional header")
    directory = optional + (96 if magic == 0x10B else 112)
    check(u32(data, directory - 4) >= 3 and directory + 24 <= optional + optional_size,
          "Missing PE resource directory")
    resource_rva, resource_size = u32(data, directory + 16), u32(data, directory + 20)
    check(resource_rva > 0 and resource_size >= 16, "Missing PE resources")
    sections = []
    for n in range(count):
        entry = optional + optional_size + 40 * n
        raw = chunk(data, entry, 40)
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", raw, 8)
        sections.append((virtual_address, max(virtual_size, raw_size), raw_offset, raw_size))

    def rva_offset(rva, size):
        for address, span, raw_offset, raw_size in sections:
            if address <= rva and rva - address < span:
                delta = rva - address
                check(delta + size <= raw_size, "Resource RVA points outside raw section")
                chunk(data, raw_offset + delta, size)
                return raw_offset + delta
        raise BrandingError("Resource RVA is unmapped")

    base = rva_offset(resource_rva, resource_size)
    resources = {}
    seen = set()

    def at(relative, size):
        check(0 <= relative <= resource_size and size <= resource_size - relative, "Resource tree offset outside directory")
        return base + relative

    def walk(relative, path):
        check(len(path) <= 3 and relative not in seen, "Cyclic or excessively deep resource tree")
        seen.add(relative)
        table = at(relative, 16)
        entries = u16(data, table + 12) + u16(data, table + 14)
        check(entries <= 4096, "Excessive resource entry count")
        at(relative + 16, entries * 8)
        for index in range(entries):
            entry = table + 16 + index * 8
            name, target = u32(data, entry), u32(data, entry + 4)
            if name & 0x80000000:
                name_offset = name & 0x7FFFFFFF
                string_offset = at(name_offset, 2)
                chars = u16(data, string_offset)
                name = chunk(data, at(name_offset + 2, chars * 2), chars * 2).decode("utf-16le")
            key = (*path, name)
            if target & 0x80000000:
                walk(target & 0x7FFFFFFF, key)
            else:
                leaf = at(target, 16)
                rva, size = u32(data, leaf), u32(data, leaf + 4)
                check(key not in resources, "Duplicate resource leaf")
                resources[key] = chunk(data, rva_offset(rva, size), size)
        seen.remove(relative)

    walk(0, ())
    return resources


def version_strings(data):
    strings = {}

    def align(offset):
        return (offset + 3) & ~3

    def node(offset, limit, path):
        length, value_length, kind = u16(data, offset), u16(data, offset + 2), u16(data, offset + 4)
        check(length >= 8 and offset + length <= limit, "Invalid version block size")
        end = offset + length
        cursor = offset + 6
        key_start = cursor
        while u16(data, cursor):
            cursor += 2
            check(cursor + 2 <= end, "Unterminated version key")
        key = chunk(data, key_start, cursor - key_start).decode("utf-16le")
        cursor = align(cursor + 2)
        size = value_length * 2 if kind == 1 else value_length
        check(cursor + size <= end, "Version value exceeds block")
        if kind == 1 and value_length and "StringFileInfo" in path:
            value = chunk(data, cursor, size).decode("utf-16le").rstrip("\0")
            strings.setdefault(key, set()).add(value)
        cursor = align(cursor + size)
        while cursor + 6 <= end:
            if not u16(data, cursor):
                check(not any(chunk(data, cursor, end - cursor)), "Nonzero version padding")
                break
            cursor = align(node(cursor, end, (*path, key)))
        return end

    node(0, len(data), ())
    return strings


def ico_frames(data):
    check(u16(data, 0) == 0 and u16(data, 2) == 1, "Invalid ICO header")
    count = u16(data, 4)
    check(0 < count <= 256, "Invalid ICO frame count")
    chunk(data, 6, count * 16)
    frames = []
    for n in range(count):
        offset = 6 + n * 16
        width, height, colors, reserved, planes, bits, size, address = struct.unpack("<BBBBHHII", chunk(data, offset, 16))
        check(reserved == 0 and size > 0, "Invalid ICO frame")
        frames.append({"width": width or 256, "height": height or 256, "colors": colors,
                       "planes": planes, "bits": bits, "bytes": size,
                       "sha256": hashlib.sha256(chunk(data, address, size)).hexdigest()})
    return frames


def verify_pe_branding(executable, icon, *, display_name=DISPLAY_NAME):
    resources = pe_resources(executable)
    versions = [(path, value) for path, value in resources.items() if len(path) == 3 and path[0] == 16 and path[1] == 1]
    check(bool(versions), "Missing EXE version resource ID 1")
    for _path, value in versions:
        strings = version_strings(value)
        for field in ("ProductName", "FileDescription"):
            check(strings.get(field) == {display_name}, f"EXE {field} does not match Prefect branding")
    expected = ico_frames(icon)
    groups = [(path, value) for path, value in resources.items() if len(path) == 3 and path[0] == 14 and path[1] == 2]
    check(bool(groups), "Missing EXE group icon resource ID 2")
    for path, group in groups:
        check(u16(group, 0) == 0 and u16(group, 2) == 1 and u16(group, 4) == len(expected),
              "Embedded icon group does not match ICO")
        chunk(group, 6, len(expected) * 14)
        for n, frame in enumerate(expected):
            width, height, colors, reserved, planes, bits, size, icon_id = struct.unpack("<BBBBHHIH", chunk(group, 6 + n * 14, 14))
            actual = {"width": width or 256, "height": height or 256, "colors": colors,
                      "planes": planes, "bits": bits, "bytes": size}
            check(reserved == 0 and all(actual[key] == frame[key] for key in actual), "Embedded ICO frame metadata differs")
            payload = resources.get((3, icon_id, path[2]))
            check(payload is not None and len(payload) == size and hashlib.sha256(payload).hexdigest() == frame["sha256"],
                  "Embedded ICO frame bytes differ")
    return {"display_name": display_name, "version_resource_id": 1, "group_icon_resource_id": 2,
            "embedded_icon_frames": len(expected), "icon_sha256": hashlib.sha256(icon).hexdigest(),
            "frame_sizes": [[f["width"], f["height"]] for f in expected], "all_embedded_frame_bytes_match": True}
