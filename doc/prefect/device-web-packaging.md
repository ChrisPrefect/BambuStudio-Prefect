# DeviceWeb bundle: cached stamp and portable-package verification

The Windows Filament Manager is enabled by default (`AppConfig.cpp`,
`studio_enable_fila_manager`). `MainFrame` creates a lazy `DeviceWebPage`, which
loads `resources/web/device_page/dist/index.html#/filament_manager` in public
builds. A successful application start does not establish that this tab works.
The native Device and Multi-device pages are separate.

## Reproduced failure

Source `ac0d8686993821d3feb521c9f27ffe1c22eaeba9`, build run `40191409698`,
completed successfully but produced a ZIP missing all 13 generated DeviceWeb
files. The workflow restored the application cache from the previous release.
`src/slic3r/GUI/DeviceWeb/CMakeLists.txt` declares only
`${CMAKE_CURRENT_BINARY_DIR}/device_page.stamp` as a custom-command output.
The actual generated bundle and its resource copy are in the fresh source
checkout, outside the cached `out/prefect-app` tree. A restored current stamp
therefore suppresses the custom command even when the generated outputs are
absent. CMake's resources-directory install silently omits the absent bundle.

## Targeted CI correction

After configure and before compiling/installing, `device_web_assets.py repair`
checks both the generated bundle and its resource copy. When incomplete it
removes only the resolved regular
`out/prefect-app/src/slic3r/GUI/DeviceWeb/device_page.stamp`. It preserves native
objects and PCH files. CI then invokes the existing CMake `device_page_build`
target, which runs upstream's pnpm install/build/copy sequence, and verifies
the resulting output. No old release bundle is copied into the new package.

The verifier requires a nonempty HTML entry point, its JavaScript and stylesheet
dependencies, local CSS subresources, and all source `public` files with exact
hashes. Generated and resource trees must match completely. After install it
independently checks the packaged tree and requires the same complete inventory
and hashes before artifact upload. The existing optional `/vite.svg` favicon
reference and optional developer source maps are not treated as runtime entry
dependencies; if a source map is generated, inventory comparison still requires
the same map to be installed.

Only workflow/helper/tests/docs change. CMake inputs, release flags and the
application source timestamp calculation remain unchanged. Cache compatibility
still depends on the existing toolchain/dependency fingerprint; reuse must be
confirmed from each actual build, not assumed.

## Updating upstream

Review the `DEVICE_PAGE_BUILD_STAMP`, `DEVICE_PAGE_DIST_DIR`,
`DEVICE_PAGE_TARGET_DIR` and `device_page_build` definitions first. If upstream
starts declaring and restoring all generated outputs reliably, reassess the
repair step. Keep the postinstall check while the portable package contains
this UI. If the target/layout changes, update the helper constants and workflow
target together. When Vite changes its entry/runtime dependencies, update the
validator and fixtures rather than bypassing failures.

Run `python -B tests/prefect/device_web_assets_test.py`. The native incremental
fixture uses CMake where installed and Windows MSBuild otherwise. It proves a
current stamp skips the target after outputs disappear, then proves targeted
stamp removal restores all bundle files without touching an unrelated native
object. Other cases cover missing/changed JS, CSS, public assets, resource and
installed copies, nested CSS, URL query/fragments, favicon/source-map exceptions,
traversal rejection and command failure before upload.
