"""Byte-accurate resource fixtures; reject old strings/icons and malformed PE data."""
import struct
import unittest

import pe_branding as p


def align(data, multiple=4):
    return data + b"\0" * ((-len(data)) % multiple)


def version_block(key, value=b"", *, kind=1, children=()):
    value_length = len(value) // 2 if kind else len(value)
    block = align(struct.pack("<HHH", 0, value_length, kind) + key.encode("utf-16le") + b"\0\0")
    block = align(block + value)
    for child in children:
        block = align(block) + child
    return struct.pack("<H", len(block)) + block[2:]


def version(name, description=None):
    values = [version_block(k, (value + "\0").encode("utf-16le")) for k, value in (
        ("ProductName", name), ("FileDescription", name if description is None else description))]
    table = version_block("040904E4", children=values)
    strings = version_block("StringFileInfo", children=[table])
    return version_block("VS_VERSION_INFO", kind=0, children=[strings])


def fixture(name=p.DISPLAY_NAME, icon_payload=b"image fixture bytes", description=None):
    ico = struct.pack("<HHH", 0, 1, 1) + struct.pack("<BBBBHHII", 16, 16, 0, 0, 1, 32, len(icon_payload), 22) + icon_payload
    group = struct.pack("<HHH", 0, 1, 1) + struct.pack("<BBBBHHIH", 16, 16, 0, 0, 1, 32, len(icon_payload), 1)
    tree = {3: {1: {1033: icon_payload}}, 14: {2: {1033: group}}, 16: {1: {1033: version(name, description)}}}
    resource = bytearray()

    def directory(entries):
        offset = len(resource)
        resource.extend(b"\0" * (16 + 8 * len(entries)))
        struct.pack_into("<H", resource, offset + 14, len(entries))
        for index, (key, value) in enumerate(sorted(entries.items())):
            if isinstance(value, dict):
                target = directory(value) | 0x80000000
            else:
                target = len(resource)
                resource.extend(b"\0" * 16)
                payload_offset = len(resource)
                resource.extend(align(value))
                struct.pack_into("<IIII", resource, target, 0x1000 + payload_offset, len(value), 0, 0)
            struct.pack_into("<II", resource, offset + 16 + 8 * index, key, target)
        return offset

    directory(tree)
    exe = bytearray(512)
    exe[:2] = b"MZ"
    struct.pack_into("<I", exe, 0x3C, 0x80)
    exe[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<H", exe, 0x80 + 6, 1)
    struct.pack_into("<H", exe, 0x80 + 20, 240)
    optional = 0x80 + 24
    struct.pack_into("<H", exe, optional, 0x20B)
    struct.pack_into("<I", exe, optional + 108, 16)
    struct.pack_into("<II", exe, optional + 112 + 16, 0x1000, len(resource))
    section = optional + 240
    exe[section:section + 8] = b".rsrc\0\0\0"
    raw_resource = align(bytes(resource), 512)
    struct.pack_into("<IIII", exe, section + 8, len(resource), 0x1000, len(raw_resource), 512)
    return bytes(exe) + raw_resource, ico


class BrandingTests(unittest.TestCase):
    def test_real_resource_layout_checks_version_and_exact_embedded_icon(self):
        exe, ico = fixture()
        proof = p.verify_pe_branding(exe, ico)
        self.assertEqual(proof["display_name"], "Prefect Bambu Studio")
        self.assertEqual(proof["embedded_icon_frames"], 1)
        self.assertTrue(proof["all_embedded_frame_bytes_match"])

    def test_old_bambustudio_version_strings_reject(self):
        exe, ico = fixture(name="BambuStudio")
        with self.assertRaisesRegex(p.BrandingError, "ProductName"):
            p.verify_pe_branding(exe, ico)

    def test_different_embedded_icon_rejects_even_with_same_metadata(self):
        exe, _ = fixture(icon_payload=b"old image")
        _, new_ico = fixture(icon_payload=b"new image")
        with self.assertRaisesRegex(p.BrandingError, "frame bytes"):
            p.verify_pe_branding(exe, new_ico)

    def test_old_file_description_rejects_even_when_product_name_is_new(self):
        exe, ico = fixture(description="BambuStudio")
        with self.assertRaisesRegex(p.BrandingError, "FileDescription"):
            p.verify_pe_branding(exe, ico)

    def test_missing_or_truncated_resources_reject(self):
        exe, ico = fixture()
        for bad in (b"MZ", exe[:200], exe[:520], b"wrong" + exe[5:]):
            with self.subTest(size=len(bad)), self.assertRaises((p.BrandingError, UnicodeDecodeError)):
                p.verify_pe_branding(bad, ico)

    def test_unmapped_resource_rva_rejects(self):
        exe, ico = fixture()
        bad = bytearray(exe)
        struct.pack_into("<I", bad, 0x80 + 24 + 112 + 16, 0xDEAD0000)
        with self.assertRaisesRegex(p.BrandingError, "unmapped"):
            p.verify_pe_branding(bytes(bad), ico)

    def test_invalid_ico_offsets_reject(self):
        exe, ico = fixture()
        bad = bytearray(ico)
        struct.pack_into("<I", bad, 18, 0xFFFFFFFF)
        with self.assertRaisesRegex(p.BrandingError, "Truncated"):
            p.verify_pe_branding(exe, bytes(bad))


if __name__ == "__main__":
    unittest.main()
