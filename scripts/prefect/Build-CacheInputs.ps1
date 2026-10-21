#Requires -Version 7.2
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('Capture','Restore')][string]$Mode,
    [Parameter(Mandatory)][string]$Workspace,
    [string]$BuildDirectory = 'out/prefect-app',
    [string]$DependencyDirectory = 'out/prefect-deps-stage',
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$Fingerprint
)
# Preserve timestamps only for byte-identical inputs. Never modify source contents or Git state.
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath($Workspace).TrimEnd([IO.Path]::DirectorySeparatorChar,[IO.Path]::AltDirectorySeparatorChar)
if ($root -eq [IO.Path]::GetPathRoot($root).TrimEnd('\','/')) { throw 'Workspace cannot be a filesystem root.' }
if (!(Test-Path -LiteralPath $root -PathType Container)) { throw 'Workspace directory is missing.' }
$comparison=if($IsWindows){[StringComparison]::OrdinalIgnoreCase}else{[StringComparison]::Ordinal}
$separator=[IO.Path]::DirectorySeparatorChar
$prefix=$root+$separator
$validatedDirectories=[Collections.Generic.HashSet[string]]::new($(if($IsWindows){[StringComparer]::OrdinalIgnoreCase}else{[StringComparer]::Ordinal}))
function Safe-Path([string]$Relative) {
    if ([IO.Path]::IsPathRooted($Relative) -or $Relative -match '(^|[\\/])\.\.([\\/]|$)') { throw "Unsafe relative input path: $Relative" }
    $full=[IO.Path]::GetFullPath((Join-Path $root $Relative))
    if (!$full.StartsWith($prefix,$comparison)) { throw "Input escaped workspace: $Relative" }
    $walk=$full
    while ($walk -and $walk.Length -ge $root.Length) {
        if ($walk -ne $full -and $validatedDirectories.Contains($walk)) { break }
        if (Test-Path -LiteralPath $walk) {
            if (((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse point refused: $walk" }
        }
        if (Test-Path -LiteralPath $walk -PathType Container) {$null=$validatedDirectories.Add($walk)}
        if ($walk.Equals($root,$comparison)) { break }
        $walk=[IO.Path]::GetDirectoryName($walk)
    }
    return $full
}
function Git-Text([string[]]$Arguments) {
    $start=[Diagnostics.ProcessStartInfo]::new('git')
    $start.UseShellExecute=$false; $start.RedirectStandardOutput=$true; $start.RedirectStandardError=$true
    $start.StandardOutputEncoding=[Text.UTF8Encoding]::new($false,$true)
    $start.ArgumentList.Add('-C');$start.ArgumentList.Add($root)
    foreach($argument in $Arguments){$start.ArgumentList.Add($argument)}
    $start.Environment['GIT_OPTIONAL_LOCKS']='0';$start.Environment['GIT_NO_LAZY_FETCH']='1'
    $process=[Diagnostics.Process]::new();$process.StartInfo=$start
    try {
        $null=$process.Start();$stdout=$process.StandardOutput.ReadToEndAsync();$stderr=$process.StandardError.ReadToEndAsync()
        $process.WaitForExit();$output=$stdout.GetAwaiter().GetResult();$errorText=$stderr.GetAwaiter().GetResult()
        if($process.ExitCode -ne 0){throw "Read-only Git command failed: $errorText"}
        return $output
    } finally {$process.Dispose()}
}
function Mark-Changed([string]$Path) {
    $current=[IO.File]::GetLastWriteTimeUtc($Path)
    if($current -lt [DateTime]::UtcNow){[IO.File]::SetLastWriteTimeUtc($Path,[DateTime]::UtcNow)}
}
function Relative-Path([string]$Path) { return [IO.Path]::GetRelativePath($root,$Path).Replace('\','/') }
function Hash-File([string]$Path) {
    $stream=[IO.FileStream]::new($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete,1048576,[IO.FileOptions]::SequentialScan)
    try {return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($stream)).ToLowerInvariant()}
    finally {$stream.Dispose()}
}
$gitRoot=[IO.Path]::GetFullPath((Git-Text -Arguments @('rev-parse','--show-toplevel')).Trim()).TrimEnd('\','/')
if (!$root.Equals($gitRoot,$comparison)) {throw 'Workspace must equal the actual Git checkout root.'}
$build=Safe-Path $BuildDirectory
$dependencies=Safe-Path $DependencyDirectory
if($build.Equals($dependencies,$comparison) -or $build.StartsWith($dependencies+$separator,$comparison) -or $dependencies.StartsWith($build+$separator,$comparison)) {throw 'Build and dependency directories must be disjoint.'}
$manifestPath=Join-Path $build '.prefect-build-inputs.json'
$tracked=[Collections.Generic.Dictionary[string,string]]::new([StringComparer]::Ordinal)
$skippedGitEntries=0
foreach($record in (Git-Text -Arguments @('ls-files','--stage','-z')).Split([char]0,[StringSplitOptions]::RemoveEmptyEntries)) {
    if($record -notmatch '^(\d+) ([a-f0-9]{40,64}) ([0-3])\t([\s\S]+)$'){throw 'Unexpected Git index record.'}
    if($Matches[3] -ne '0'){throw 'Unmerged Git index cannot be cached.'}
    if($Matches[1] -notin @('100644','100755')){$skippedGitEntries++;continue}
    $tracked.Add($Matches[4],$Matches[2])
}
if($Mode -eq 'Restore') {
    if(!(Test-Path -LiteralPath $manifestPath -PathType Leaf)){Write-Host 'No build input manifest; inputs retain checkout timestamps.';return}
    $manifest=Get-Content -LiteralPath $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json -Depth 12
    if($manifest.schema -ne 1 -or !$root.Equals([string]$manifest.workspace,$comparison) -or $manifest.fingerprint -cne $Fingerprint -or
        $manifest.build_directory -cne (Relative-Path $build) -or $manifest.dependency_directory -cne (Relative-Path $dependencies)) {throw 'Cached input manifest does not match workspace, layout or build fingerprint.'}
    $restored=0;$changed=0;$missing=0;$seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    # Validate the entire cached path list before changing the first timestamp.
    foreach($entry in $manifest.files) {
        if(!$seen.Add([string]$entry.path)){throw 'Duplicate cached input path.'}
        $null=Safe-Path ([string]$entry.path)
        if($entry.kind -notin @('git','dependency') -or $entry.sha256 -notmatch '^[a-f0-9]{64}$' -or [long]$entry.ticks -le 0 -or [long]$entry.bytes -lt 0){throw 'Malformed cached input metadata.'}
        if($entry.kind -eq 'dependency') {
            $full=Safe-Path ([string]$entry.path)
            if(!$full.StartsWith($dependencies+$separator,$comparison)){throw 'Dependency input is outside dependency staging.'}
        }
    }
    foreach($entry in $manifest.files) {
        $full=Safe-Path ([string]$entry.path)
        if(!(Test-Path -LiteralPath $full -PathType Leaf)){$missing++;continue}
        if($entry.kind -eq 'git' -and (!$tracked.ContainsKey([string]$entry.path) -or $tracked[[string]$entry.path] -cne $entry.blob)){Mark-Changed $full;$changed++;continue}
        $before=Get-Item -LiteralPath $full -Force
        if($before.Length -ne [long]$entry.bytes -or (Hash-File $full) -cne $entry.sha256){Mark-Changed $full;$changed++;continue}
        $after=Get-Item -LiteralPath $full -Force
        if($after.Length -ne $before.Length -or $after.LastWriteTimeUtc.Ticks -ne $before.LastWriteTimeUtc.Ticks){Mark-Changed $full;$changed++;continue}
        [IO.File]::SetLastWriteTimeUtc($full,[DateTime]::new([long]$entry.ticks,[DateTimeKind]::Utc));$restored++
    }
    Write-Host "Build inputs: restored $restored identical timestamps; changed $changed; missing $missing."
    return
}
$candidates=[Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
foreach($pair in $tracked.GetEnumerator()) {
    $full=Safe-Path $pair.Key
    if(Test-Path -LiteralPath $full -PathType Leaf){$candidates.Add($pair.Key,[pscustomobject]@{path=$pair.Key;kind='git';blob=$pair.Value})}
}
if(Test-Path -LiteralPath $dependencies -PathType Container) {
    $pending=[Collections.Generic.Stack[string]]::new();$pending.Push($dependencies)
    while($pending.Count) {
        foreach($item in Get-ChildItem -LiteralPath $pending.Pop() -Force) {
            if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'Reparse point in dependency staging.'}
            if($item.PSIsContainer){$pending.Push($item.FullName);continue}
            $relative=Relative-Path $item.FullName
            if(!$candidates.ContainsKey($relative)){$candidates.Add($relative,[pscustomobject]@{path=$relative;kind='dependency';blob=$null})}
        }
    }
}
$files=[Collections.Generic.List[object]]::new();$unstable=0
foreach($candidate in ($candidates.Values | Sort-Object path)) {
    $full=Safe-Path $candidate.path;$before=Get-Item -LiteralPath $full -Force;$hash=Hash-File $full;$after=Get-Item -LiteralPath $full -Force
    if($before.Length -ne $after.Length -or $before.LastWriteTimeUtc.Ticks -ne $after.LastWriteTimeUtc.Ticks){$unstable++;continue}
    $files.Add([pscustomobject]@{path=$candidate.path;kind=$candidate.kind;blob=$candidate.blob;bytes=$after.Length;sha256=$hash;ticks=$after.LastWriteTimeUtc.Ticks})
}
$manifest=[ordered]@{schema=1;workspace=$root;fingerprint=$Fingerprint;build_directory=(Relative-Path $build);dependency_directory=(Relative-Path $dependencies);files=$files;unstable_files_skipped=$unstable;unsupported_git_entries_skipped=$skippedGitEntries}
[IO.Directory]::CreateDirectory($build) | Out-Null
$temp=Join-Path $build ('.prefect-inputs-'+[Guid]::NewGuid().ToString('N')+'.tmp')
[IO.File]::WriteAllText($temp,($manifest | ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
[IO.File]::Move($temp,$manifestPath,$true)
Write-Host "Captured $($files.Count) hashed Git/dependency inputs; unstable files skipped $unstable. Manifest: $manifestPath"