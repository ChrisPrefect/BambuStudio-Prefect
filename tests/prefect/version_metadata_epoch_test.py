"""Real Git-history regression tests for version date and source independence."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[2] / "scripts/prefect/version_metadata_epoch.py"
SPEC = importlib.util.spec_from_file_location("version_metadata_epoch", HELPER)
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)


class VersionMetadataEpochTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="prefect-version-epoch-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Version Epoch Fixture")
        self.git("config", "user.email", "version-epoch-fixture@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.autocrlf", "false")
        for path in policy.VERSION_INPUTS:
            self.write(path, "metadata baseline\n")
        self.write("src/slic3r/GUI/GUI_App.cpp", "int gui_body = 1;\n")
        self.baseline = self.commit(1000000000)

    def git(self, *args, root=None):
        return subprocess.run(["git", "-C", str(root or self.root), *args], check=True,
                              capture_output=True, text=True, encoding="utf-8").stdout.strip()

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")

    def commit(self, epoch):
        self.git("add", "--all")
        env = dict(os.environ, GIT_AUTHOR_DATE=f"{epoch} +0000", GIT_COMMITTER_DATE=f"{epoch} +0000")
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "Synthetic epoch fixture"],
                       check=True, capture_output=True, env=env)
        return self.git("rev-parse", "HEAD")

    def test_gui_body_edit_preserves_epoch_but_changes_real_source_and_blob(self):
        original = policy.select_epoch(self.root)
        blob = self.git("rev-parse", "HEAD:src/slic3r/GUI/GUI_App.cpp")
        self.write("src/slic3r/GUI/GUI_App.cpp", "int gui_body = 2;\n")
        actual_head = self.commit(1000000100)
        result = policy.select_epoch(self.root, revision=actual_head)
        self.assertEqual(result["version_metadata_epoch"], original["version_metadata_epoch"])
        self.assertEqual(result["version_metadata_commit"], self.baseline)
        self.assertEqual(result["source_commit"], actual_head)
        self.assertNotEqual(blob, self.git("rev-parse", "HEAD:src/slic3r/GUI/GUI_App.cpp"))

    def test_each_metadata_input_advances_epoch(self):
        for number, path in enumerate(policy.VERSION_INPUTS, 1):
            with self.subTest(path=path):
                self.write(path, f"metadata revision {number}\n")
                epoch = 1000000200 + number
                head = self.commit(epoch)
                result = policy.select_epoch(self.root)
                self.assertEqual(result["version_metadata_commit"], head)
                self.assertEqual(result["version_metadata_epoch"], epoch)

    def test_ci_docs_and_unrelated_dependency_edits_preserve_epoch(self):
        for path in (".github/workflows/build.yml", "doc/release.md", "deps/source.cpp"):
            self.write(path, "ordinary change\n")
        self.commit(1000000300)
        self.assertEqual(policy.select_epoch(self.root)["version_metadata_commit"], self.baseline)

    def test_dirty_metadata_is_refused_but_dirty_gui_is_not_backdated(self):
        gui = self.root / "src/slic3r/GUI/GUI_App.cpp"
        self.write("src/slic3r/GUI/GUI_App.cpp", "dirty GUI body\n")
        timestamp, content = gui.stat().st_mtime_ns, gui.read_bytes()
        self.assertEqual(policy.select_epoch(self.root)["version_metadata_commit"], self.baseline)
        self.assertEqual((gui.stat().st_mtime_ns, gui.read_bytes()), (timestamp, content))
        self.write(policy.VERSION_INPUTS[0], "dirty version\n")
        with self.assertRaisesRegex(ValueError, "must match"):
            policy.select_epoch(self.root)

    def test_wrong_source_revision_and_unpinned_fetch_are_refused(self):
        with self.assertRaisesRegex(ValueError, "differs"):
            policy.select_epoch(self.root, revision="f" * 40)
        with self.assertRaisesRegex(ValueError, "requires"):
            policy.select_epoch(self.root, deepen=True)

    def test_shallow_boundary_requires_history_and_local_deepening_finds_real_date(self):
        self.write("src/slic3r/GUI/GUI_App.cpp", "later GUI body\n")
        head = self.commit(1000000400)
        clone = Path(self.temp.name) / "shallow"
        subprocess.run(["git", "clone", "--quiet", "--depth=1", self.root.as_uri(), str(clone)],
                       check=True, capture_output=True)
        with self.assertRaisesRegex(ValueError, "shallow boundary"):
            policy.select_epoch(clone)
        result = policy.select_epoch(clone, revision=head, deepen=True)
        self.assertEqual(result["version_metadata_commit"], self.baseline)
        self.assertEqual(result["version_metadata_epoch"], 1000000000)
        self.assertEqual(self.git("rev-parse", "HEAD", root=clone), head)

    def test_cli_exports_metadata_date_without_replacing_source_identity(self):
        env_file = Path(self.temp.name) / "github-env"
        output = subprocess.run([sys.executable, "-B", str(HELPER), "--workspace", str(self.root),
                                 "--revision", self.baseline, "--github-env", str(env_file)],
                                check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(output.stdout)["source_commit"], self.baseline)
        lines = env_file.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines, [f"VERSION_METADATA_COMMIT={self.baseline}",
                                 "VERSION_METADATA_EPOCH=1000000000", "SOURCE_DATE_EPOCH=1000000000"])
        self.assertFalse(any(line.startswith("GITHUB_SHA=") for line in lines))

    def test_real_cmake_header_bytes_stay_stable_for_gui_edit_and_change_for_version(self):
        cmake = shutil.which("cmake")
        if not cmake:
            self.skipTest("CMake not locally installed; Ubuntu policy CI runs this native fixture")
        self.write("version.inc", 'set(SLIC3R_VERSION "1.0")\n')
        self.write("src/libslic3r/libslic3r_version.h.in", '#define VERSION "@SLIC3R_VERSION@"\n#define BUILD_TIME "@SLIC3R_BUILD_TIME@"\n')
        self.write("CMakeLists.txt", '''cmake_minimum_required(VERSION 3.16)
project(VersionMetadataFixture NONE)
include(version.inc)
string(TIMESTAMP SLIC3R_BUILD_TIME %Y%m%d-%H%M%S)
configure_file(src/libslic3r/libslic3r_version.h.in version.h @ONLY)
''')
        self.commit(1000000500)
        build = Path(self.temp.name) / "cmake-build"

        def configure():
            result = policy.select_epoch(self.root)
            env = dict(os.environ, SOURCE_DATE_EPOCH=str(result["version_metadata_epoch"]))
            subprocess.run([cmake, "-S", str(self.root), "-B", str(build)], env=env,
                           check=True, capture_output=True)
            return (build / "version.h").read_bytes()

        first = configure()
        self.write("src/slic3r/GUI/GUI_App.cpp", "new GUI body\n")
        self.commit(1000000600)
        self.assertEqual(configure(), first)
        self.write("version.inc", 'set(SLIC3R_VERSION "1.1")\n')
        self.commit(1000000700)
        self.assertNotEqual(configure(), first)


if __name__ == "__main__":
    unittest.main()
