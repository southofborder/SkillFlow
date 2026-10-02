$ErrorActionPreference = 'Stop'
$repositoryRoot = [IO.Path]::GetFullPath('D:\projects\SkillFlow')
$resultRoot = [IO.Path]::GetFullPath((Join-Path $repositoryRoot 'result'))
$deliveryStage = [IO.Path]::GetFullPath((Join-Path $repositoryRoot 'tmp\full-pipeline-v4-20260918-rerun-failed\staging'))
$priorDelivery = [IO.Path]::GetFullPath((Join-Path $repositoryRoot 'tmp\full-pipeline-v4-20260918-rerun-failed\published-prior'))

function Assert-NoReparseAncestors([string] $path) {
    $current = [IO.Path]::GetFullPath($path)
    if ($current -ne $repositoryRoot -and -not $current.StartsWith($repositoryRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Publication path escaped the explicitly authorized workspace'
    }
    while ($true) {
        if (Test-Path -LiteralPath $current) {
            if ((Get-Item -LiteralPath $current -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Publication refuses a linked path or ancestor: $current"
            }
        }
        if ($current -eq $repositoryRoot) { break }
        $current = [IO.Path]::GetDirectoryName($current)
    }
}

function Get-CheckedFiles([string] $directory) {
    # Enumerate one level at a time: reject a reparse point before descending.
    Assert-NoReparseAncestors $directory
    $pending = [Collections.Generic.Stack[string]]::new()
    $pending.Push($directory)
    while ($pending.Count -gt 0) {
        $current = $pending.Pop()
        foreach ($item in @(Get-ChildItem -LiteralPath $current -Force)) {
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Publication refuses a linked child: $($item.FullName)"
            }
            if ($item.PSIsContainer) { $pending.Push($item.FullName) }
            else { $item }
        }
    }
}

$verificationPath = Join-Path $deliveryStage 'review\verification.json'
Assert-NoReparseAncestors $verificationPath
Assert-NoReparseAncestors $resultRoot
Assert-NoReparseAncestors $priorDelivery
if (-not (Test-Path -LiteralPath $verificationPath -PathType Leaf)) { throw 'Final verification is missing' }
$verification = Get-Content -LiteralPath $verificationPath -Raw -Encoding utf8 | ConvertFrom-Json
if ($verification.status -ne 'passed' -or $verification.cases -ne 30) { throw 'Final verification is not complete' }
if ($null -eq $verification.files -or $verification.files -isnot [pscustomobject]) { throw 'Final verification has no file digest mapping' }
if (Test-Path -LiteralPath $priorDelivery) { throw 'Publication backup already exists; do not overwrite a prior publication' }
$foldersToPublish = @('ir-IPP', 'suggestions', 'security-profiles', 'review')
$actions = @()
foreach ($folderName in $foldersToPublish) {
    $sourceDirectory = [IO.Path]::GetFullPath((Join-Path $deliveryStage $folderName))
    $targetDirectory = [IO.Path]::GetFullPath((Join-Path $resultRoot $folderName))
    $backupDirectory = [IO.Path]::GetFullPath((Join-Path $priorDelivery $folderName))
    if ([IO.Path]::GetDirectoryName($sourceDirectory) -ne $deliveryStage -or
        [IO.Path]::GetDirectoryName($targetDirectory) -ne $resultRoot -or
        [IO.Path]::GetDirectoryName($backupDirectory) -ne $priorDelivery -or
        -not $targetDirectory.StartsWith($repositoryRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Publication path escaped the explicitly authorized workspace directories'
    }
    if (-not (Test-Path -LiteralPath $sourceDirectory -PathType Container)) { throw "Missing staged directory: $folderName" }
    Assert-NoReparseAncestors $sourceDirectory
    Assert-NoReparseAncestors $targetDirectory
    Assert-NoReparseAncestors $backupDirectory
    foreach ($existingPath in @($sourceDirectory, $targetDirectory)) {
        if (Test-Path -LiteralPath $existingPath) {
            if ((Get-Item -LiteralPath $existingPath).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Publication refuses linked directories' }
        }
    }
    $actions += [pscustomobject]@{ Source = $sourceDirectory; Target = $targetDirectory; Backup = $backupDirectory }
}

# Bind publication to the exact reviewed bytes, not just to a passed status.
$expectedFiles = [Collections.Generic.Dictionary[string,string]]::new([StringComparer]::Ordinal)
foreach ($property in $verification.files.PSObject.Properties) {
    $relative = $property.Name
    if ($relative -notmatch '^(ir-IPP|suggestions|security-profiles|review)/' -or
        $relative -eq 'review/verification.json' -or $relative.Contains('\') -or
        $relative.Contains(':') -or $relative.Contains('//') -or
        ($relative.Split('/') | Where-Object { $_ -eq '.' -or $_ -eq '..' -or $_ -eq '' }).Count -gt 0 -or
        $property.Value -isnot [string] -or $property.Value -notmatch '^[0-9a-fA-F]{64}$') {
        throw "Invalid reviewed file mapping: $relative"
    }
    $expectedFiles.Add($relative, $property.Value.ToLowerInvariant())
}
if ($expectedFiles.Count -eq 0) { throw 'Reviewed file mapping is empty' }
$actualFiles = [Collections.Generic.Dictionary[string,string]]::new([StringComparer]::Ordinal)
foreach ($action in $actions) {
    foreach ($file in @(Get-CheckedFiles $action.Source)) {
        $relative = [IO.Path]::GetRelativePath($deliveryStage, $file.FullName).Replace('\', '/')
        if ($relative -eq 'review/verification.json') { continue }
        $actualFiles.Add($relative, (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant())
    }
    # The old directory will be moved wholesale, never through a linked child.
    if (Test-Path -LiteralPath $action.Target) { $null = @(Get-CheckedFiles $action.Target) }
}
if ($actualFiles.Count -ne $expectedFiles.Count) { throw 'Staging file inventory differs from final verification' }
foreach ($relative in $expectedFiles.Keys) {
    if (-not $actualFiles.ContainsKey($relative) -or $actualFiles[$relative] -ne $expectedFiles[$relative]) {
        throw "Staging file missing or changed after verification: $relative"
    }
}

New-Item -ItemType Directory -Path $priorDelivery | Out-Null
New-Item -ItemType Directory -Path $resultRoot -Force | Out-Null
foreach ($action in $actions) {
    # All absolute move targets were checked above; no cross-shell file operations.
    if (Test-Path -LiteralPath $action.Target) { Move-Item -LiteralPath $action.Target -Destination $action.Backup }
    Copy-Item -LiteralPath $action.Source -Destination $action.Target -Recurse
    $sourceFiles = @(Get-CheckedFiles $action.Source)
    $targetFiles = @(Get-CheckedFiles $action.Target)
    if ($sourceFiles.Count -ne $targetFiles.Count) { throw "Published file count differs: $($action.Target)" }
    foreach ($sourceFile in $sourceFiles) {
        $relativeName = [IO.Path]::GetRelativePath($action.Source, $sourceFile.FullName)
        $targetFile = Join-Path $action.Target $relativeName
        if ((Get-FileHash -LiteralPath $sourceFile.FullName -Algorithm SHA256).Hash -ne
            (Get-FileHash -LiteralPath $targetFile -Algorithm SHA256).Hash) { throw "Published file differs: $relativeName" }
    }
}
[pscustomobject]@{ Status = 'published'; Backup = $priorDelivery; Folders = $foldersToPublish } | ConvertTo-Json
