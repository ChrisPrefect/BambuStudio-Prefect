"""Append fork translations to PO and overlay MO without external dependencies.

The upstream binary catalog may contain translations not in the checked-in PO.
Preserve its original message bytes (including contexts/plurals) instead of
recompiling an unrelated upstream catalog as part of the small fork patch.
"""
import gettext
import io
import json
from pathlib import Path
import struct


def overlay_mo(data, translations):
    byte_order = "<" if data[:4] == b"\xde\x12\x04\x95" else ">"
    magic, revision, count, originals, translated, _, _ = struct.unpack_from(byte_order + "7I", data)
    if magic != 0x950412DE or revision >> 16 > 1:
        raise ValueError("Unsupported MO catalog")
    catalog = {}
    for index in range(count):
        key_len, key_pos = struct.unpack_from(byte_order + "2I", data, originals + 8 * index)
        val_len, val_pos = struct.unpack_from(byte_order + "2I", data, translated + 8 * index)
        catalog[data[key_pos:key_pos + key_len]] = data[val_pos:val_pos + val_len]
    catalog.update({key.encode("utf-8"): value.encode("utf-8") for key, value in translations.items()})
    entries = sorted(catalog.items())
    offset = 28 + 16 * len(entries)
    keys = bytearray()
    vals = bytearray()
    key_table = []
    val_table = []
    for key, _ in entries:
        key_table.append((len(key), offset + len(keys)))
        keys.extend(key + b"\0")
    val_start = offset + len(keys)
    for _, value in entries:
        val_table.append((len(value), val_start + len(vals)))
        vals.extend(value + b"\0")
    result = bytearray(struct.pack("<7I", 0x950412DE, 0, len(entries), 28, 28 + 8 * len(entries), 0, 0))
    for table in (key_table, val_table):
        for length, position in table:
            result.extend(struct.pack("<2I", length, position))
    result.extend(keys)
    result.extend(vals)
    check = gettext.GNUTranslations(io.BytesIO(result))
    for key, value in translations.items():
        assert check.gettext(key) == value, key
    return bytes(result)


def main():
    root = Path(__file__).resolve().parents[2]
    translations = json.loads(Path(__file__).with_name("translations-de.json").read_text(encoding="utf-8"))
    source = root / "bbl/i18n/de/BambuStudio_de.po"
    content = source.read_text(encoding="utf-8")
    for key, value in translations.items():
        quoted_key = json.dumps(key, ensure_ascii=False)
        if f"msgid {quoted_key}\n" not in content:
            content += "\n#. Prefect workflow\nmsgid " + quoted_key + "\nmsgstr " + json.dumps(value, ensure_ascii=False) + "\n"
    source.write_text(content, encoding="utf-8", newline="\n")
    binary = root / "resources/i18n/de/BambuStudio.mo"
    binary.write_bytes(overlay_mo(binary.read_bytes(), translations))
    print(f"German catalog: {len(translations)} fork messages verified")


if __name__ == "__main__":
    main()
