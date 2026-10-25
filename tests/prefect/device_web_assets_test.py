"""Regression: cached stamp must not hide missing DeviceWeb runtime outputs."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


HELPER = Path(__file__).resolve().parents[2] / "scripts/prefect/device_web_assets.py"
SPEC = importlib.util.spec_from_file_location("device_web_assets", HELPER)
assets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(assets)


class DeviceWebAssetsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="prefect-device-web-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.public = self.root / assets.PAGE / "public"
        self.public.mkdir(parents=True)
        (self.public / "logo.svg").write_text("<svg/>")
        self.dist = self.root / assets.PAGE / "dist"
        self.resource = self.root / assets.RESOURCE
        self.stamp = self.root / "out/prefect-app" / assets.STAMP
        self.stamp.parent.mkdir(parents=True)
        self.stamp.write_text("cached")
        self.unrelated = self.stamp.parent / "native.obj"
        self.unrelated.write_bytes(b"unchanged native object")
        self.make_bundle(self.dist)
        shutil.copytree(self.dist, self.resource)

    def make_bundle(self, target):
        (target / "assets").mkdir(parents=True)
        (target / "index.html").write_text(
            '<link rel="icon" href="/vite.svg"><link rel="stylesheet" '
            'href="./assets/index.css?v=1#ok"><script src="./assets/index.js"></script>', encoding="utf-8")
        (target / "assets/index.js").write_text("console.log('runtime');//# sourceMappingURL=optional.map")
        (target / "assets/index.css").write_text('body{background:url(data:image/png;base64,abc)}')
        (target / "logo.svg").write_text("<svg/>")

    def test_complete_outputs_preserve_cached_stamp_and_native_object(self):
        stamp_time = self.stamp.stat().st_mtime_ns
        self.assertEqual(assets.repair(self.root, "out/prefect-app"), {"stamp_removed": False, "files": 4})
        self.assertEqual(stamp_time, self.stamp.stat().st_mtime_ns)
        self.assertEqual(self.unrelated.read_bytes(), b"unchanged native object")

    def test_missing_generated_output_invalidates_only_stamp(self):
        shutil.rmtree(self.dist)
        self.assertTrue(assets.repair(self.root, "out/prefect-app")["stamp_removed"])
        self.assertFalse(self.stamp.exists())
        self.assertTrue(self.unrelated.is_file())

    def test_missing_resource_copy_invalidates_stamp(self):
        shutil.rmtree(self.resource)
        self.assertTrue(assets.repair(self.root, "out/prefect-app")["stamp_removed"])

    def test_missing_js_css_or_public_asset_is_rejected(self):
        for name in ("assets/index.js", "assets/index.css", "logo.svg"):
            with self.subTest(name=name):
                path = self.dist / name
                content = path.read_bytes()
                path.unlink()
                with self.assertRaises(assets.AssetError):
                    assets.verify(self.root)
                path.write_bytes(content)

    def test_mismatched_copies_are_rejected(self):
        (self.resource / "assets/index.js").write_text("stale cached bundle")
        with self.assertRaisesRegex(assets.AssetError, "differ"):
            assets.verify(self.root)

    def test_changed_public_asset_is_rejected(self):
        (self.dist / "logo.svg").write_text("stale public copy")
        with self.assertRaisesRegex(assets.AssetError, "public asset"):
            assets.verify(self.root)

    def test_installed_runtime_is_independently_verified(self):
        installed = self.root / "out/portable" / assets.RESOURCE
        shutil.copytree(self.resource, installed)
        self.assertTrue(assets.verify(self.root, "out/portable")["installed"])
        (installed / "assets/index.js").unlink()
        with self.assertRaises(assets.AssetError):
            assets.verify(self.root, "out/portable")

    def test_nested_css_runtime_dependency_is_required(self):
        (self.dist / "assets/index.css").write_text('@import "./theme.css";')
        with self.assertRaisesRegex(assets.AssetError, "runtime asset"):
            assets.verify(self.root)

    def test_traversal_cannot_invalidate_outside_stamp(self):
        with self.assertRaises(assets.AssetError):
            assets.repair(self.root, "../outside")
        self.assertTrue(self.stamp.is_file())
        (self.dist / "assets/index.css").write_text('a{background:url(../../../../outside.svg)}')
        with self.assertRaisesRegex(assets.AssetError, "escapes"):
            assets.verify(self.root)

    def test_cli_failure_gates_upload(self):
        (self.resource / "index.html").unlink()
        result = subprocess.run([sys.executable, "-B", str(HELPER), "verify", "--workspace", str(self.root)], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"Missing runtime entry point", result.stderr)

    def test_stamp_symlink_cannot_delete_native_object(self):
        self.stamp.unlink()
        try:
            self.stamp.symlink_to(self.unrelated)
        except OSError:
            self.skipTest("Creating symbolic links requires host permission")
        shutil.rmtree(self.dist)
        with self.assertRaisesRegex(assets.AssetError, "Reparse point"):
            assets.repair(self.root, "out/prefect-app")
        self.assertEqual(self.unrelated.read_bytes(), b"unchanged native object")

    def test_build_parent_reparse_attribute_refuses_stamp_deletion(self):
        # Exercise the Windows junction attribute branch without administrator
        # symlink rights. The walk must inspect the original build path.
        build = self.root / "out/prefect-app"
        original_lstat = Path.lstat

        def reparse_attribute(path, *args, **kwargs):
            result = original_lstat(path, *args, **kwargs)
            if path == build:
                return SimpleNamespace(st_mode=result.st_mode, st_file_attributes=0x400)
            return result

        with patch.object(Path, "lstat", reparse_attribute):
            with self.assertRaisesRegex(assets.AssetError, "Reparse point"):
                assets.repair(self.root, "out/prefect-app")
        self.assertTrue(self.stamp.is_file())
        self.assertEqual(self.unrelated.read_bytes(), b"unchanged native object")

    def test_native_incremental_target_rebuilds_after_stamp_repair(self):
        """Real MSBuild (Windows) / CMake scheduling reproduces the cache bug."""
        template = self.root / "template"
        shutil.copytree(self.dist, template)
        trigger = self.root / "input.txt"
        trigger.write_text("unchanged source")
        os.utime(trigger, (1000000000, 1000000000))
        self.stamp.unlink()
        cmake = shutil.which("cmake")
        msbuild = Path(os.environ.get("WINDIR", "C:/Windows")) / "Microsoft.NET/Framework64/v4.0.30319/MSBuild.exe"
        if cmake:
            source = self.root / "fixture-source"
            source.mkdir()
            (source / "CMakeLists.txt").write_text('''cmake_minimum_required(VERSION 3.16)
project(DeviceWebCacheFixture NONE)
add_custom_command(OUTPUT "${STAMP}"
 COMMAND "${CMAKE_COMMAND}" -E copy_directory "${TEMPLATE}" "${GENERATED}"
 COMMAND "${CMAKE_COMMAND}" -E copy_directory "${TEMPLATE}" "${RESOURCES}"
 COMMAND "${CMAKE_COMMAND}" -E touch "${STAMP}"
 DEPENDS "${INPUT}")
add_custom_target(device_page_build DEPENDS "${STAMP}")
''')
            configure = [cmake, "-S", str(source), "-B", str(self.root / "fixture-build")]
            for key, value in {"STAMP": self.stamp, "TEMPLATE": template, "GENERATED": self.dist, "RESOURCES": self.resource, "INPUT": trigger}.items():
                configure.append(f"-D{key}={value.as_posix()}")
            subprocess.run(configure, check=True, capture_output=True)
            command = [cmake, "--build", str(self.root / "fixture-build"), "--target", "device_page_build"]
        elif msbuild.is_file():
            project = self.root / "fixture.proj"
            from xml.sax.saxutils import escape
            items = "".join(f'<Asset Include="{escape(str(path))}"><Relative>{escape(path.relative_to(template).as_posix())}</Relative></Asset>' for path in template.rglob("*") if path.is_file())
            project.write_text(f'''<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
<ItemGroup>{items}</ItemGroup><Target Name="Build" Inputs="{trigger}" Outputs="{self.stamp}">
<Copy SourceFiles="@(Asset)" DestinationFiles="@(Asset->'{self.dist}/%(Relative)')"/>
<Copy SourceFiles="@(Asset)" DestinationFiles="@(Asset->'{self.resource}/%(Relative)')"/>
<Touch Files="{self.stamp}" AlwaysCreate="true"/></Target></Project>''', encoding="utf-8")
            command = [str(msbuild), str(project), "/nologo", "/v:minimal"]
        else:
            self.skipTest("Native CMake or MSBuild needed for incremental scheduling fixture")
        subprocess.run(command, check=True, capture_output=True)
        first_stamp = self.stamp.stat().st_mtime_ns
        shutil.rmtree(self.dist)
        shutil.rmtree(self.resource)
        subprocess.run(command, check=True, capture_output=True)
        self.assertEqual(first_stamp, self.stamp.stat().st_mtime_ns)
        with self.assertRaises(assets.AssetError):
            assets.verify(self.root)
        self.assertTrue(assets.repair(self.root, "out/prefect-app")["stamp_removed"])
        subprocess.run(command, check=True, capture_output=True)
        self.assertEqual(assets.verify(self.root)["verified_files"], 4)
        self.assertEqual(self.unrelated.read_bytes(), b"unchanged native object")


if __name__ == "__main__":
    unittest.main()
