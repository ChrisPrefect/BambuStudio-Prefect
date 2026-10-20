# Optional accelerator. A changed dependency tree/compiler always builds from source.
$ErrorActionPreference = 'Stop'
$expectedDepsTree = 'ff281d41e59773ecd48419d60b101529790735fa'
$expectedCmakeTree = '476b31db07057c30ba134d4e1f488524888a81c8'
$depsTree = git rev-parse 'HEAD:deps'
$cmakeTree = git rev-parse 'HEAD:cmake'
if ($env:PREFECT_VS_MAJOR -ne '18' -or $depsTree -ne $expectedDepsTree -or $cmakeTree -ne $expectedCmakeTree) {
    Write-Host 'Compiler or dependency sources differ; building dependencies from source.'
    exit 0
}
$download = Join-Path $PWD 'out/prefect-upstream-deps'
New-Item -ItemType Directory -Force -Path $download | Out-Null
$outer = Join-Path $download 'artifact.zip'
try {
    # Official bambulab/BambuStudio artifact 9220135690, master 9a530f77c23d8c3430d1dbef02e103cd8bd6480e.
    # Despite its historical filename, these libraries use the vc145 / VS 2026 ABI.
    Invoke-WebRequest -Uri 'https://api.github.com/repos/bambulab/BambuStudio/actions/artifacts/9220135690/zip' -Headers @{
        Authorization = "Bearer $env:GH_TOKEN"
        Accept = 'application/vnd.github+json'
        'X-GitHub-Api-Version' = '2022-11-28'
    } -OutFile $outer
} catch {
    Write-Warning "Official dependency artifact unavailable; building from source. $($_.Exception.Message)"
    exit 0
}
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $outer).Hash -ne '55A5FC5B55A3424ED358E31639000FC726D4E4964B524BAB128989EAA87754B5') {
    throw 'Official dependency artifact checksum mismatch.'
}
Expand-Archive -LiteralPath $outer -DestinationPath (Join-Path $download 'outer') -Force
$inner = Join-Path $download 'outer/BambuStudio_dep_win64_20260814_vs2022.zip'
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $inner).Hash -ne '50DABBD4E85D30307C9D4B818697E8DB0461D2752701076BEC2AAE87ACADCC34') {
    throw 'Official dependency payload checksum mismatch.'
}
Expand-Archive -LiteralPath $inner -DestinationPath (Join-Path $PWD 'out/prefect-deps-stage') -Force
if (-not (Test-Path 'out/prefect-deps-stage/usr/local/include/boost-1_84/boost/version.hpp') -or
    -not (Test-Path 'out/prefect-deps-stage/usr/local/OpenCVConfig.cmake')) {
    throw 'Unexpected official dependency layout.'
}
'PREFECT_DEPS_RESTORED=true' >> $env:GITHUB_ENV
Write-Host 'Verified matching upstream dependency and CMake trees, both ZIP hashes, and vc145 compiler.'
