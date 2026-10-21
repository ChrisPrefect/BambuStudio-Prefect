#Requires -Version 7.2
[CmdletBinding()]
param(
    [string] $BuildDirectory = (Join-Path $PWD 'out/prefect-app'),
    [string] $DependencyPrefix = (Join-Path $PWD 'out/prefect-deps-stage/usr/local'),
    [string] $Configuration = 'Release',
    [string] $Platform = 'x64'
)

# Inspect generated link inputs before the expensive application compilation.
# Build products under BuildDirectory need not exist yet. Dependency libraries do.
$ErrorActionPreference = 'Stop'
$buildRoot = [IO.Path]::GetFullPath($BuildDirectory).TrimEnd('\', '/')
$dependencyRoot = [IO.Path]::GetFullPath($DependencyPrefix).TrimEnd('\', '/')
if (-not (Test-Path -LiteralPath $buildRoot -PathType Container) -or
    -not (Test-Path -LiteralPath $dependencyRoot -PathType Container)) {
    throw 'Build directory and dependency prefix must exist before link preflight.'
}
$origins = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
[void] $origins.Add('D:/a/BambuStudio/BambuStudio/deps/build/BambuStudio_dep/usr/local')
$statePath = Join-Path $dependencyRoot 'prefect-relocation.json'
if (Test-Path -LiteralPath $statePath -PathType Leaf) {
    $state = Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json
    foreach ($prefix in @($state.retired_prefixes)) {
        if ($prefix) { [void] $origins.Add([string] $prefix) }
    }
}
$originPatterns = @($origins | ForEach-Object {
    [regex]::Escape($_.Replace('\', '/').TrimEnd('/')).Replace('/', '(?:/|\\{1,2})') + '(?=$|[/\\\s;"''<>])'
})
$problems = [Collections.Generic.List[string]]::new()
$checkedLibraries = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$checkedDirectories = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)

function Test-UnderDirectory([string] $Path, [string] $Directory) {
    return $Path.Replace('\', '/').StartsWith($Directory.Replace('\', '/') + '/', [StringComparison]::OrdinalIgnoreCase)
}

function Expand-ProjectVariables([string] $Value, [string] $ProjectDirectory) {
    $properties = @{
        Configuration = $Configuration
        Platform = $Platform
        ProjectDir = $ProjectDirectory.TrimEnd('\', '/') + '/'
        MSBuildProjectDirectory = $ProjectDirectory
        SolutionDir = $buildRoot + '/'
    }
    foreach ($name in $properties.Keys) {
        $Value = $Value.Replace('$(' + $name + ')', $properties[$name], [StringComparison]::OrdinalIgnoreCase)
    }
    return $Value
}

function Test-SelectedConfiguration($Node, [string] $ProjectDirectory) {
    while ($Node -is [Xml.XmlElement]) {
        $condition = Expand-ProjectVariables $Node.GetAttribute('Condition') $ProjectDirectory
        if ($condition -match '^\s*[''"](?<left>.*?)[''"]\s*(?<operator>==|!=)\s*[''"](?<right>.*?)[''"]\s*$') {
            $equal = $Matches.left -eq $Matches.right
            if (($Matches.operator -eq '==' -and -not $equal) -or
                ($Matches.operator -eq '!=' -and $equal)) { return $false }
        }
        $Node = $Node.ParentNode
    }
    return $true
}

function Test-OriginReferences([string] $Text, [string] $Source) {
    foreach ($pattern in $originPatterns) {
        if ([regex]::IsMatch($Text, $pattern, [Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
            $problems.Add("Stale dependency origin in $Source")
        }
    }
}

function Test-LinkPath([string] $Value, [string] $ProjectDirectory, [string] $Source, [switch] $Directory) {
    $value = (Expand-ProjectVariables $Value $ProjectDirectory).Trim().Trim('"')
    if (-not $value -or $value.StartsWith('%(')) { return }
    if ($value -match '^(?:/|-)(?:DEFAULTLIB|WHOLEARCHIVE|LIBPATH):(?<path>.*)$') {
        $value = $Matches.path.Trim('"')
    }
    if (-not [IO.Path]::IsPathFullyQualified($value)) { return }
    # Canonicalize ordinary absolute paths, retaining the boundary at the prefix.
    $path = [IO.Path]::GetFullPath($value)
    if (Test-UnderDirectory $path $buildRoot) { return }
    if (-not (Test-UnderDirectory $path $dependencyRoot)) { return }
    if ($path.Contains('$(') -or $path.Contains('%(')) {
        $problems.Add("Unresolved property in dependency link input from ${Source}: $path")
        return
    }
    if ($Directory) {
        if ($checkedDirectories.Add($path) -and -not (Test-Path -LiteralPath $path -PathType Container)) {
            $problems.Add("Missing dependency library directory from ${Source}: $path")
        }
    } elseif ([IO.Path]::GetExtension($path) -eq '.lib') {
        if ($checkedLibraries.Add($path) -and -not (Test-Path -LiteralPath $path -PathType Leaf)) {
            $problems.Add("Missing dependency library from ${Source}: $path")
        }
    }
}

$projects = @([IO.Directory]::EnumerateFiles($buildRoot, '*.vcxproj', [IO.SearchOption]::AllDirectories))
foreach ($project in $projects) {
    $text = [IO.File]::ReadAllText($project)
    Test-OriginReferences $text $project
    [xml] $xml = $text
    $projectDirectory = [IO.Path]::GetDirectoryName($project)
    $nodes = $xml.SelectNodes("//*[local-name()='AdditionalDependencies' or local-name()='AdditionalLibraryDirectories']")
    foreach ($node in $nodes) {
        if (-not (Test-SelectedConfiguration $node $projectDirectory)) { continue }
        foreach ($entry in $node.InnerText.Split(';')) {
            Test-LinkPath $entry $projectDirectory $project -Directory:($node.LocalName -eq 'AdditionalLibraryDirectories')
        }
    }
}

$responses = @([IO.Directory]::EnumerateFiles($buildRoot, '*.rsp', [IO.SearchOption]::AllDirectories))
foreach ($response in $responses) {
    $text = [IO.File]::ReadAllText($response)
    Test-OriginReferences $text $response
    # Windows linker arguments can contain a quoted portion after /LIBPATH:.
    foreach ($token in [regex]::Matches($text, '(?:[^\s"]+|"[^"]*")+')) {
        $argument = $token.Value.Replace('"', '')
        $isDirectory = $argument -match '^(?:/|-)LIBPATH:'
        Test-LinkPath $argument ([IO.Path]::GetDirectoryName($response)) $response -Directory:$isDirectory
    }
}
if (-not $projects.Count -and -not $responses.Count) {
    throw 'No generated Visual Studio projects or existing linker response files found.'
}
if ($problems.Count) {
    throw ("Dependency link preflight failed before compilation:`n" + (($problems | Select-Object -Unique) -join "`n"))
}
Write-Host "Dependency link preflight passed: $($projects.Count) projects, $($responses.Count) response files, $($checkedLibraries.Count) dependency libraries ($Configuration|$Platform)."
