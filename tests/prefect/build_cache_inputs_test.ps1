#Requires -Version 7.2
[CmdletBinding()]
param([string]$HelperPath=(Join-Path $PSScriptRoot '../../scripts/prefect/Build-CacheInputs.ps1'))
$ErrorActionPreference='Stop'
$HelperPath=[IO.Path]::GetFullPath($HelperPath)
$base=if($env:RUNNER_TEMP){$env:RUNNER_TEMP}else{[IO.Path]::GetTempPath()}
$fixture=Join-Path $base ('prefect-cache-inputs-fixture-'+[Guid]::NewGuid().ToString('N'))
$null=New-Item -ItemType Directory -Path $fixture
function Assert($Condition,[string]$Message){if(!$Condition){throw $Message}}
function Invoke-FixtureGit([string[]]$Arguments){& git -C $fixture @Arguments;if($LASTEXITCODE -ne 0){throw 'Fixture Git failed'}}
Invoke-FixtureGit -Arguments @('init','-q')
Invoke-FixtureGit -Arguments @('config','core.autocrlf','false')
$null=New-Item -ItemType Directory -Path (Join-Path $fixture 'include'),(Join-Path $fixture 'out/prefect-deps-stage/include'),(Join-Path $fixture 'out/prefect-app')
$source=Join-Path $fixture 'source.cpp';$header=Join-Path $fixture 'include/ü name.hpp';$dependency=Join-Path $fixture 'out/prefect-deps-stage/include/dep.hpp'
[IO.File]::WriteAllText($source,'int unchanged = 1;')
[IO.File]::WriteAllText($header,'#define VALUE 1')
[IO.File]::WriteAllText($dependency,'#define DEPENDENCY 1')
Invoke-FixtureGit -Arguments @('add','--','source.cpp','include')
$old=[DateTime]::UtcNow.AddHours(-2)
foreach($file in @($source,$header,$dependency)){[IO.File]::SetLastWriteTimeUtc($file,$old)}
# A real MSBuild target proves timestamp restoration changes incremental scheduling.
$msbuildCommand=Get-Command MSBuild.exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
$msbuild=if($msbuildCommand){$msbuildCommand.Source}else{Join-Path $env:WINDIR 'Microsoft.NET/Framework64/v4.0.30319/MSBuild.exe'}
Assert (Test-Path -LiteralPath $msbuild -PathType Leaf) 'MSBuild required for the incremental fixture'
$project=Join-Path $fixture 'incremental.proj';$stamp=Join-Path $fixture 'out/prefect-app/incremental.stamp';$runs=Join-Path $fixture 'runs.log'
$xml='<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003"><Target Name="Build" Inputs="source.cpp;include/ü name.hpp;out/prefect-deps-stage/include/dep.hpp" Outputs="out/prefect-app/incremental.stamp"><WriteLinesToFile File="runs.log" Lines="ran" Overwrite="false"/><Touch Files="out/prefect-app/incremental.stamp" AlwaysCreate="true"/></Target></Project>'
[IO.File]::WriteAllText($project,$xml,[Text.UTF8Encoding]::new($false))
& $msbuild $project /nologo /v:minimal
Assert ($LASTEXITCODE -eq 0) 'Initial MSBuild fixture failed'
[IO.File]::SetLastWriteTimeUtc($stamp,$old.AddMinutes(30))
Assert (@(Get-Content -LiteralPath $runs).Count -eq 1) 'Initial target did not execute once'
$fingerprint='test-compiler-sdk-workspace-deps-flags'
& $HelperPath -Mode Capture -Workspace $fixture -Fingerprint $fingerprint
$manifestPath=Join-Path $fixture 'out/prefect-app/.prefect-build-inputs.json'
$original=[IO.File]::ReadAllText($manifestPath)
$manifest=$original | ConvertFrom-Json
Assert ($manifest.files.Count -eq 3) 'Expected both Git inputs and dependency input'
$new=$old.AddHours(1)
foreach($file in @($source,$header,$dependency)){[IO.File]::SetLastWriteTimeUtc($file,$new)}
& $HelperPath -Mode Restore -Workspace $fixture -Fingerprint $fingerprint
foreach($file in @($source,$header,$dependency)){Assert ((Get-Item -LiteralPath $file).LastWriteTimeUtc.Ticks -eq $old.Ticks) ('Identical input timestamp not restored: '+$file)}
& $msbuild $project /nologo /v:minimal
Assert ($LASTEXITCODE -eq 0) 'Restored MSBuild fixture failed'
Assert (@(Get-Content -LiteralPath $runs).Count -eq 1) 'Identical source restoration did not skip the cached MSBuild target'
# Same Git blob but dirty bytes must stay fresh; changed dependency bytes too.
[IO.File]::WriteAllText($source,'int unchanged = 2;');[IO.File]::SetLastWriteTimeUtc($source,$new)
[IO.File]::WriteAllText($dependency,'#define DEPENDENCY 2');[IO.File]::SetLastWriteTimeUtc($dependency,$new)
& $HelperPath -Mode Restore -Workspace $fixture -Fingerprint $fingerprint
Assert ((Get-Item -LiteralPath $source).LastWriteTimeUtc.Ticks -ge $new.Ticks) 'Dirty content was backdated'
Assert ((Get-Item -LiteralPath $dependency).LastWriteTimeUtc.Ticks -ge $new.Ticks) 'Changed dependency was backdated'
& $msbuild $project /nologo /v:minimal
Assert ($LASTEXITCODE -eq 0) 'Changed-input MSBuild fixture failed'
Assert (@(Get-Content -LiteralPath $runs).Count -eq 2) 'Changed inputs did not rebuild the MSBuild target'
# A changed staged blob is also never backdated, even with bytes matching old capture.
[IO.File]::WriteAllText($source,'int staged = 99;');Invoke-FixtureGit -Arguments @('add','--','source.cpp')
[IO.File]::WriteAllText($source,'int unchanged = 1;');[IO.File]::SetLastWriteTimeUtc($source,$new)
& $HelperPath -Mode Restore -Workspace $fixture -Fingerprint $fingerprint
Assert ((Get-Item -LiteralPath $source).LastWriteTimeUtc.Ticks -ge $new.Ticks) 'Changed Git blob was backdated'
# Wrong ABI/root and traversal reject before any timestamp change.
$rejected=$false
try {& $HelperPath -Mode Restore -Workspace $fixture -Fingerprint 'wrong-ABI'} catch {$rejected=$true}
Assert $rejected 'Wrong fingerprint was accepted'
$manifest.files[0].path='../outside.cpp'
[IO.File]::WriteAllText($manifestPath,($manifest | ConvertTo-Json -Depth 8))
$rejected=$false
try {& $HelperPath -Mode Restore -Workspace $fixture -Fingerprint $fingerprint} catch {$rejected=$true}
Assert $rejected 'Traversal was accepted'
Assert ((Get-Item -LiteralPath $source).LastWriteTimeUtc.Ticks -ge $new.Ticks) 'Traversal test changed source timestamp'
[IO.File]::WriteAllText($manifestPath,$original)
# Restoring missing files is harmless; no replacement file is created.
$missing=Join-Path $fixture 'include/missing.hpp'
$manifest=$original | ConvertFrom-Json
($manifest.files | Where-Object { $_.path -eq 'include/ü name.hpp' }).path='include/missing.hpp'
[IO.File]::WriteAllText($manifestPath,($manifest | ConvertTo-Json -Depth 8))
& $HelperPath -Mode Restore -Workspace $fixture -Fingerprint $fingerprint
Assert (!(Test-Path -LiteralPath $missing)) 'Missing input was recreated'
Write-Host "Build input cache fixture: PASS (unchanged/dirty/blob/deps/Unicode/ABI/traversal/missing; native MSBuild skip/rebuild); fixture retained: $fixture"