[CmdletBinding()]
param(
    [string]$ExecutablePath,
    [string]$ProfileDirectory = (Join-Path $env:APPDATA 'BambuStudio-Prefect'),
    [switch]$ImportStockProfile
)
$ErrorActionPreference = 'Stop'

if (-not $ExecutablePath) {
    $candidates = @(Get-ChildItem -LiteralPath $PSScriptRoot -Filter 'bambu-studio.exe' -File -Recurse -Depth 3)
    if ($candidates.Count -ne 1) {
        throw 'Bitte -ExecutablePath mit dem Pfad zur selbst gebauten bambu-studio.exe angeben.'
    }
    $ExecutablePath = $candidates[0].FullName
}
$ExecutablePath = (Resolve-Path -LiteralPath $ExecutablePath).Path
$ProfileDirectory = [IO.Path]::GetFullPath($ProfileDirectory)
$stockDirectory = [IO.Path]::GetFullPath((Join-Path $env:APPDATA 'BambuStudio'))
if ($ProfileDirectory.TrimEnd('\') -eq $stockDirectory.TrimEnd('\')) {
    throw 'Der Fork benötigt ein separates Profilverzeichnis.'
}
if ($ImportStockProfile) {
    if (Test-Path -LiteralPath $ProfileDirectory) {
        throw 'Profilimport nur in ein neues Verzeichnis möglich; vorhandene Daten werden nicht überschrieben.'
    }
    New-Item -ItemType Directory -Path $ProfileDirectory | Out-Null
    foreach ($name in @('BambuStudio.conf', 'user', 'system')) {
        $source = Join-Path $stockDirectory $name
        if (Test-Path -LiteralPath $source) {
            Copy-Item -LiteralPath $source -Destination $ProfileDirectory -Recurse
        }
    }
} elseif (-not (Test-Path -LiteralPath $ProfileDirectory)) {
    New-Item -ItemType Directory -Path $ProfileDirectory | Out-Null
}

# Native argument passing preserves spaces. The application stays interactive.
& $ExecutablePath '--datadir' $ProfileDirectory
exit $LASTEXITCODE
