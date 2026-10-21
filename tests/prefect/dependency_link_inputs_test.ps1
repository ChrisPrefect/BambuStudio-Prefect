#Requires -Version 7.2
[CmdletBinding()]
param([string] $TemporaryRoot = [IO.Path]::GetTempPath())

$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$restore = Join-Path $repo 'scripts/prefect/Restore-UpstreamDependencies.ps1'
$preflight = Join-Path $repo 'scripts/prefect/Test-DependencyLinkInputs.ps1'
$parent = [IO.Path]::GetFullPath($TemporaryRoot).TrimEnd('\', '/')
$testRoot = Join-Path $parent ('prefect dependency regression ' + [guid]::NewGuid().ToString('N'))
$origin = 'D:/a/BambuStudio/BambuStudio/deps/build/BambuStudio_dep/usr/local'
$utf8 = [Text.UTF8Encoding]::new($false)
$savedGitHubEnv = $env:GITHUB_ENV
# Synthetic stages must never advertise themselves as the real workflow stage.
Remove-Item Env:GITHUB_ENV -ErrorAction SilentlyContinue

function Require([bool] $Condition, [string] $Message) {
    if (-not $Condition) { throw $Message }
}
function Write-Text([string] $Path, [string] $Text) {
    [void] [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Path))
    [IO.File]::WriteAllText($Path, $Text, $utf8)
}
function Expect-Failure([scriptblock] $Action, [string] $Message) {
    $failed = $false
    try { & $Action } catch {
        $failed = $true
        Require ($_.Exception.Message.Contains($Message)) ('Unexpected failure: ' + $_.Exception.Message)
    }
    Require $failed ('Expected failure was not detected: ' + $Message)
}

try {
    [void] [IO.Directory]::CreateDirectory($testRoot)
    $first = Join-Path $testRoot 'first/usr/local'
    Write-Text (Join-Path $first 'include/boost-1_84/boost/version.hpp') '// layout placeholder'
    Write-Text (Join-Path $first 'OpenCVConfig.cmake') '# layout placeholder'
    Write-Text (Join-Path $first 'lib/cmake/probe/forward.cmake') ('set(LIB "' + $origin + '/lib/freetype.lib")' + "`r`n")
    Write-Text (Join-Path $first 'lib/pkgconfig/probe.pc') ('prefix=' + $origin + "`n")
    Write-Text (Join-Path $first 'lib/probe.prl') ('LIB=' + $origin.Replace('/', '\') + '\lib\freetype.lib')
    Write-Text (Join-Path $first 'lib/cmake/probe/escaped.cmake') ('set(LIB "' + $origin.Replace('/', '\\') + '\\lib\\freetype.lib")')
    Write-Text (Join-Path $first 'lib/cmake/probe/relative.cmake') 'set(LIB "${_IMPORT_PREFIX}/lib/freetype.lib"); # C:/SDK/system.lib'
    $relativeHash = (Get-FileHash -LiteralPath (Join-Path $first 'lib/cmake/probe/relative.cmake')).Hash
    $wide = Join-Path $first 'lib/cmake/probe/wide.xml'
    [IO.File]::WriteAllText($wide, '<LIB>' + $origin + '/lib/freetype.lib</LIB>', [Text.UnicodeEncoding]::new($false, $true))
    # These are existence-check placeholders, not linker-compatible binaries.
    $binary = Join-Path $first 'lib/freetype.lib'
    [IO.File]::WriteAllBytes($binary, [byte[]]@(0, 1, 2, 3, 255))
    $binaryHash = (Get-FileHash -LiteralPath $binary).Hash
    & $restore -DependencyPrefix $first -RelocateOnly
    Require ((Get-FileHash -LiteralPath $binary).Hash -eq $binaryHash) 'Relocation modified a binary.'
    Require ((Get-FileHash -LiteralPath (Join-Path $first 'lib/cmake/probe/relative.cmake')).Hash -eq $relativeHash) 'Unrelated metadata changed.'
    foreach ($path in @('lib/cmake/probe/forward.cmake', 'lib/pkgconfig/probe.pc', 'lib/probe.prl', 'lib/cmake/probe/escaped.cmake', 'lib/cmake/probe/wide.xml')) {
        $text = [IO.File]::ReadAllText((Join-Path $first $path))
        Require ($text.Contains($first.Replace('\', '/'))) ('Prefix not relocated: ' + $path)
        Require (-not $text.Contains('D:/a/BambuStudio')) ('Origin remains: ' + $path)
    }
    Require ([IO.File]::ReadAllText((Join-Path $first 'lib/cmake/probe/forward.cmake')).EndsWith("`r`n")) 'CRLF was not preserved.'
    $wideBytes = [IO.File]::ReadAllBytes($wide)
    Require ($wideBytes[0] -eq 0xff -and $wideBytes[1] -eq 0xfe) 'UTF16 BOM was not preserved.'
    $hashes = @{}
    Get-ChildItem -LiteralPath $first -Recurse -File | ForEach-Object { $hashes[$_.FullName] = (Get-FileHash -LiteralPath $_.FullName).Hash }
    & $restore -DependencyPrefix $first -RelocateOnly
    foreach ($path in $hashes.Keys) { Require ((Get-FileHash -LiteralPath $path).Hash -eq $hashes[$path]) ('Relocation not idempotent: ' + $path) }
    $second = Join-Path $testRoot 'moved/usr/local'
    [void] [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($second))
    Copy-Item -LiteralPath $first -Destination $second -Recurse
    & $restore -DependencyPrefix $second -RelocateOnly
    Require ([IO.File]::ReadAllText((Join-Path $second 'lib/cmake/probe/forward.cmake')).Contains($second.Replace('\', '/'))) 'Cached stage was not relocated after a move.'
    $build = Join-Path $testRoot 'app build'
    [void] [IO.Directory]::CreateDirectory($build)
    $project = Join-Path $build 'probe.vcxproj'
    $good = (Join-Path $second 'lib/freetype.lib').Replace('\', '/')
    $missing = (Join-Path $second 'lib/missing.lib').Replace('\', '/')
    $own = (Join-Path $build 'Release/not-built.lib').Replace('\', '/')
    $goodProject = @"
<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemDefinitionGroup Condition="'`$(Configuration)|`$(Platform)'=='Release|x64'"><Link>
    <AdditionalDependencies>$good;$own;user32.lib;%(AdditionalDependencies)</AdditionalDependencies>
    <AdditionalLibraryDirectories>$($second.Replace('\','/'))/lib;%(AdditionalLibraryDirectories)</AdditionalLibraryDirectories>
  </Link></ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'`$(Configuration)|`$(Platform)'=='Debug|x64'"><Link><AdditionalDependencies>$missing</AdditionalDependencies></Link></ItemDefinitionGroup>
</Project>
"@
    Write-Text $project $goodProject
    $response = Join-Path $build 'probe.rsp'
    Write-Text $response ('/LIBPATH:"' + $second.Replace('\', '/') + '/lib" "' + $good + '" "' + $own + '"')
    & $preflight -BuildDirectory $build -DependencyPrefix $second
    Write-Text $project ($goodProject.Replace($good, $origin + '/lib/freetype.lib'))
    Expect-Failure { & $preflight -BuildDirectory $build -DependencyPrefix $second } 'Stale dependency origin'
    Write-Text $project ($goodProject.Replace($good, $missing))
    Expect-Failure { & $preflight -BuildDirectory $build -DependencyPrefix $second } 'Missing dependency library'
    Write-Text $project $goodProject
    Write-Text $response ('"' + $origin.Replace('/', '\') + '\lib\freetype.lib"')
    Expect-Failure { & $preflight -BuildDirectory $build -DependencyPrefix $second } 'Stale dependency origin'
    Write-Text $response ('"' + $missing + '"')
    Expect-Failure { & $preflight -BuildDirectory $build -DependencyPrefix $second } 'Missing dependency library'
    Write-Host 'Dependency relocation/link preflight regressions passed (synthetic metadata; no compile/link).'
} finally {
    if ($null -ne $savedGitHubEnv) { $env:GITHUB_ENV = $savedGitHubEnv }
    $resolved = [IO.Path]::GetFullPath($testRoot)
    if (-not $resolved.StartsWith($parent + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or
        [IO.Path]::GetFileName($resolved) -notmatch '^prefect dependency regression [0-9a-f]{32}$') {
        throw 'Refusing cleanup outside this test temporary directory.'
    }
    if (Test-Path -LiteralPath $resolved) { Remove-Item -LiteralPath $resolved -Recurse -Force }
}
