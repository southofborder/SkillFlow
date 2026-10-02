$ErrorActionPreference = 'Stop'
$expectedRoot = 'D:\projects\SkillFlow\packages\skill-ir\experiments\propagation\runs\processing-v1-20260928-204710'
$targetRoot = (Resolve-Path -LiteralPath $expectedRoot).ProviderPath.TrimEnd('\')
if ($targetRoot -ne $expectedRoot) { throw 'Unexpected refresh target' }
$active = @(Get-CimInstance Win32_Process | Where-Object {
    $_.Name -match '^python(w)?\.exe$' -and $_.CommandLine -match 'run_runtime_pilot\.py|run_pilot\.py|run_full_pipeline\.py|skill_ir\.security_profile|skill_ir\.propagation'
})
if ($active.Count) { throw 'A potentially related runner is active; no files removed' }
$paths = @((Get-Item -LiteralPath $targetRoot)) + @(Get-ChildItem -LiteralPath $targetRoot -Force -Recurse)
foreach ($item in $paths) {
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse point in refresh target' }
    $resolved = (Resolve-Path -LiteralPath $item.FullName).ProviderPath
    if ($resolved -ne $targetRoot -and -not $resolved.StartsWith($targetRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Refresh path outside allowed directory'
    }
}
$pins = @{
    '001' = @('e4dc09d5e597c4ce87634343aa8e4aae9b0150a39122b584eb887ec3e94fcddc', '058005caac8f3069c7f0df3bb5353a534c3550215bfdba782382cb3cb0278c02')
    '010' = @('1812750e77d42599058579cc295595b237c2a390d93a7677d4f2bd32d1c3e58e', '365872ca9a9bde370a9db64ca024c7a77b51f20f15b6efa3a043427ddbcd72fe')
    '013' = @('0eec4c18ca72bef85f00366e598ebcefa0e53e0b0d32272d301def8efd4e5489', '806a44b5db93af9d89278638872d5cb542d8e2cc4c43690ad8a70ea6de59a757')
}
$caseRoot = Join-Path $targetRoot 'cases'
if (((Get-ChildItem -LiteralPath $caseRoot -Force).Name | Sort-Object) -join ',' -ne '001,010,013') { throw 'Unexpected case inventory' }
$protectedNames = @('selected-analysis.json', 'selection.json', 'cfg-review.md')
foreach ($number in $pins.Keys) {
    $base = Join-Path $caseRoot $number
    $names = @('selected-analysis.json','selection.json')
    for ($i=0; $i -lt 2; $i++) {
        if ((Get-FileHash -LiteralPath (Join-Path $base $names[$i]) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pins[$number][$i]) { throw 'Retained CFG/source selection hash mismatch' }
    }
}
$lock = [IO.File]::Open((Join-Path $targetRoot '.runner.lock'), [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
try {
    # Check nested call/run locks before removing any artifact.
    foreach ($item in ($paths | Where-Object { $_.Name -eq '.runner.lock' -and $_.DirectoryName -ne $targetRoot })) {
        $probe = [IO.File]::Open($item.FullName, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
        $probe.Dispose()
    }
    $targets = @()
    foreach ($number in $pins.Keys) {
        $targets += @(Get-ChildItem -LiteralPath (Join-Path $caseRoot $number) -Force | Where-Object { $_.Name -notin $protectedNames })
    }
    $targets += @(Get-ChildItem -LiteralPath $targetRoot -Force | Where-Object { $_.Name -notin @('cases','.runner.lock') })
    foreach ($item in $targets) {
        $resolved = (Resolve-Path -LiteralPath $item.FullName).ProviderPath
        if (-not $resolved.StartsWith($targetRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Deletion target outside allowed directory' }
        Remove-Item -LiteralPath $resolved -Force -Recurse
    }
    Write-Output ('Refreshed exact authorized directory; removed generated entries: ' + $targets.Count)
    Write-Output 'Retained all three selected CFGs, source selections and CFG views.'
} finally {
    $lock.Dispose()
}
