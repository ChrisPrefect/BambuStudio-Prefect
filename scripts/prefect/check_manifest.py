"""Validate the documented patch inventory without GUI/build dependencies."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
manifest = json.loads((root / "doc/prefect/changes.json").read_text(encoding="utf-8"))
expected = {f"F{index:02d}" for index in range(1, 10)}
assert {change["id"] for change in manifest["changes"]} == expected
assert len(manifest["changes"]) == len(expected)
assert manifest["upstream_commit"] == "926a7192574bcb9b3a732e1ec59a46d79cb45466"
for change in manifest["changes"]:
    assert (root / change["documentation"]).is_file(), change["id"]
    for entry in change["anchors"]:
        content = (root / entry["file"]).read_text(encoding="utf-8-sig")
        assert entry["text"] in content, (change["id"], entry)
    for test in change.get("tests", []):
        assert (root / test).is_file(), (change["id"], test)
print("Manifest: all 9 features have documentation and matching source anchors")
