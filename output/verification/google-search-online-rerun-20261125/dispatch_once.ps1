$ErrorActionPreference = 'Stop'
$root = 'D:/Projects/SkillFlow'
$verify = $PSScriptRoot
$source = Join-Path $root 'output/verification/google-search-group-meeting-20261125/source-package'
$old = Join-Path $root 'experiments/doe/runs/document-guided-google-search-meeting-high-20261125-154844'
$run = Join-Path $root ('experiments/doe/runs/document-guided-google-search-retry-high-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$python = 'C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$env:PYTHONPATH = Join-Path $root 'src'
$env:SKILLFLOW_LEAN_RENDERER = 'C:/Users/admin/AppData/Local/skillflow/lean/win32-AMD64/d58f81f68e43b79b2587ad4cf283b45ae69e27be007787110bb461e4ed0a6af4/.lake/build/bin/skill_ir_retell.exe'
$cli = (Get-Command codex -ErrorAction Stop).Source

function Write-Once([string]$Path, $Record) {
    $file = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    $writer = [IO.StreamWriter]::new($file, [Text.UTF8Encoding]::new($false))
    try { $writer.WriteLine(($Record | ConvertTo-Json -Depth 8)) } finally { $writer.Dispose() }
}

if ((Test-Path (Join-Path $verify 'dispatch-intent.json')) -or (Test-Path -LiteralPath $run)) {
    throw 'The single rerun has already been claimed'
}
$previous = Get-Content -LiteralPath (Join-Path $old 'result.json') -Raw | ConvertFrom-Json
if ($previous.status -ne 'failed' -or $previous.selected_annotation) { throw 'Previous online run is not the expected closed failure' }
$sources = @(Get-ChildItem -LiteralPath $source -File -Recurse)
if ($sources.Count -ne 2) { throw 'Expected the two original Google Search source files' }
foreach ($relative in @('SKILL.md', 'scripts/search.py')) {
    $preparedFile = Join-Path $source $relative
    $previousFile = Join-Path (Join-Path $old 'source/inputs/package') $relative
    if ((Get-FileHash -LiteralPath $preparedFile).Hash -ne (Get-FileHash -LiteralPath $previousFile).Hash) {
        throw 'Source differs from the previous frozen package'
    }
}

& $python -m tools.doe.document_guided_pilot prepare --input $source --run-dir $run --effort high *> (Join-Path $verify 'prepare.log')
if ($LASTEXITCODE -ne 0) { throw 'Preparation failed; no online launch took place' }
$manifest = Get-Content -LiteralPath (Join-Path $run 'manifest.json') -Raw | ConvertFrom-Json
$verified = Get-Content -LiteralPath (Join-Path $verify 'offline-regression.json') -Raw | ConvertFrom-Json
if ($manifest.implementation.sha256 -ne $verified.implementation -or $verified.lean_roundtrip -ne 'passed') {
    throw 'Prepared implementation differs from the tested CFG recovery'
}
$claim = @{
    run_directory = $run; previous = $old; at = [DateTime]::UtcNow.ToString('o'); owner = '/root'
    implementation = $manifest.implementation.sha256; manifest_sha256 = $manifest.manifest_sha256
    config = $manifest.config; executable = $cli; executable_sha256 = (Get-FileHash -LiteralPath $cli).Hash.ToLowerInvariant()
    timeout = 2700; retries = 2; launches = 1
}
Write-Once (Join-Path $verify 'dispatch-intent.json') $claim
& $python -m tools.doe.document_guided_pilot run --run-dir $run --executable $cli --timeout 2700 --retries 2 *> (Join-Path $verify 'online-run.log')
$exitCode = $LASTEXITCODE
$resultPath = Join-Path $run 'result.json'
$result = if (Test-Path -LiteralPath $resultPath) { Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json } else { $null }
Write-Once (Join-Path $verify 'dispatch-terminal.json') @{
    run_directory = $run; at = [DateTime]::UtcNow.ToString('o'); exit_code = $exitCode
    status = $result.status; stage = $result.stage; stages = $result.stages
}
Get-Content -LiteralPath (Join-Path $verify 'online-run.log') -TotalCount 32
exit $exitCode
