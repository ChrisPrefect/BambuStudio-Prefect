#Requires -Version 7.2
[CmdletBinding()]
param(
    [string] $DependencyPrefix = (Join-Path $PWD 'out/prefect-deps-stage/usr/local'),
    [switch] $RelocateOnly
)

# Optional accelerator. A changed dependency tree/compiler builds from source.
$ErrorActionPreference = 'Stop'
$originPrefix = 'D:/a/BambuStudio/BambuStudio/deps/build/BambuStudio_dep/usr/local'

function Test-DependencyLayout([string] $Prefix) {
    return ((Test-Path -LiteralPath (Join-Path $Prefix 'include/boost-1_84/boost/version.hpp') -PathType Leaf) -and
            (Test-Path -LiteralPath (Join-Path $Prefix 'OpenCVConfig.cmake') -PathType Leaf) -and
            (Test-Path -LiteralPath (Join-Path $Prefix 'lib') -PathType Container))
}

function Get-PrefixPattern([string] $Prefix) {
    # Match forward, native Windows, and CMake-escaped Windows separators.
    $escaped = [regex]::Escape($Prefix.Replace('\', '/').TrimEnd('/'))
    return $escaped.Replace('/', '(?:/|\\{1,2})') + '(?=$|[/\\\s;"''<>])(?<tail>(?:[/\\]+[^\\/\s;"''<>]+)*)'
}

function Read-Metadata([string] $Path) {
    $bytes = [IO.File]::ReadAllBytes($Path)
    $encoding = [Text.UTF8Encoding]::new($false, $true)
    if ($bytes.Length -ge 2 -and $bytes[0] -eq 0xff -and $bytes[1] -eq 0xfe) {
        $encoding = [Text.UnicodeEncoding]::new($false, $false, $true)
    } elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xfe -and $bytes[1] -eq 0xff) {
        $encoding = [Text.UnicodeEncoding]::new($true, $false, $true)
    }
    # Decoding the entire stream retains an existing BOM as U+FEFF. GetBytes
    # therefore preserves it, as well as all original newline characters.
    $text = $encoding.GetString($bytes)
    if ($text.Contains([char]0)) { throw "Unsupported metadata encoding: $Path" }
    return @{ Text = $text; Encoding = $encoding }
}

function Invoke-DependencyRelocation([string] $Prefix) {
    $prefixPath = [IO.Path]::GetFullPath($Prefix).TrimEnd('\', '/')
    $normalized = $prefixPath.Replace('\', '/')
    if ($normalized -match '[;"$\r\n]') { throw 'Dependency prefix contains unsupported CMake path characters.' }
    $statePath = Join-Path $prefixPath 'prefect-relocation.json'
    $sourcePrefixes = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    [void] $sourcePrefixes.Add($originPrefix)
    if (Test-Path -LiteralPath $statePath -PathType Leaf) {
        $state = Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json
        if ($state.format_version -ne 1) { throw 'Unknown dependency relocation state version.' }
        foreach ($previous in @($state.dependency_prefix) + @($state.retired_prefixes)) {
            if ($previous -and $previous -ne $normalized) { [void] $sourcePrefixes.Add([string]$previous) }
        }
    }
    [void] $sourcePrefixes.Remove($normalized)
    $patterns = @($sourcePrefixes | ForEach-Object { Get-PrefixPattern $_ })
    $metadata = @([IO.Directory]::EnumerateFiles($prefixPath, '*', [IO.SearchOption]::AllDirectories) |
        Where-Object { [IO.Path]::GetExtension($_) -in @('.cmake', '.pc', '.prl', '.la', '.xml', '.props', '.targets') -or
                       [IO.Path]::GetFileName($_) -eq 'CMakeCache.txt' })
    $changed = 0
    $references = 0
    foreach ($path in $metadata) {
        $document = Read-Metadata $path
        $updated = $document.Text
        foreach ($pattern in $patterns) {
            $matches = [regex]::Matches($updated, $pattern, [Text.RegularExpressions.RegexOptions]::IgnoreCase)
            $references += $matches.Count
            if ($matches.Count) {
                $updated = [regex]::Replace($updated, $pattern, [Text.RegularExpressions.MatchEvaluator] {
                    param($match)
                    return $normalized + [regex]::Replace($match.Groups['tail'].Value, '\\+', '/')
                }, [Text.RegularExpressions.RegexOptions]::IgnoreCase)
            }
        }
        if ($updated -cne $document.Text) {
            $temporary = $path + '.prefect-relocating'
            [IO.File]::WriteAllBytes($temporary, $document.Encoding.GetBytes($updated))
            [IO.File]::Move($temporary, $path, $true)
            $changed++
        }
    }
    # Scan the resulting bytes again before advertising this stage as usable.
    foreach ($path in $metadata) {
        $text = (Read-Metadata $path).Text
        foreach ($pattern in $patterns) {
            if ([regex]::IsMatch($text, $pattern, [Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
                throw "Unrelocated dependency origin in $path"
            }
        }
    }
    $newState = [ordered]@{
        format_version = 1
        dependency_prefix = $normalized
        retired_prefixes = @($sourcePrefixes | Sort-Object)
    } | ConvertTo-Json -Depth 3
    [IO.File]::WriteAllText($statePath, $newState + "`n", [Text.UTF8Encoding]::new($false))
    if ($env:GITHUB_ENV) { 'PREFECT_DEPS_RESTORED=true' >> $env:GITHUB_ENV }
    Write-Host "Dependency metadata verified: $($metadata.Count) files; $references references relocated in $changed files."
}

# Cache keys are bound to the dependency sources, compiler and this helper.
# A cached stage still needs normalization if its absolute workspace changed.
if (Test-DependencyLayout $DependencyPrefix) {
    Invoke-DependencyRelocation $DependencyPrefix
    return
}
if ($RelocateOnly) { throw 'No complete dependency stage found for relocation.' }
if ([IO.Path]::GetFullPath($DependencyPrefix) -ne [IO.Path]::GetFullPath((Join-Path $PWD 'out/prefect-deps-stage/usr/local'))) {
    throw 'A custom DependencyPrefix supports existing stages only; fresh download uses out/prefect-deps-stage/usr/local.'
}

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
if (-not (Test-DependencyLayout $DependencyPrefix)) {
    throw 'Unexpected official dependency layout.'
}
Invoke-DependencyRelocation $DependencyPrefix
Write-Host 'Verified matching upstream dependency and CMake trees, both ZIP hashes, and vc145 compiler.'
