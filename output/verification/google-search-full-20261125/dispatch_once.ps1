$ErrorActionPreference = 'Stop'
$root = 'D:/Projects/SkillFlow'
$verify = $PSScriptRoot
$source = Join-Path $root 'output/verification/google-search-group-meeting-20261125/source-package'
$previousRun = Join-Path $root 'experiments/doe/runs/document-guided-google-search-retry-high-20261125-161918'
$run = Join-Path $root ('experiments/doe/runs/document-guided-google-search-full-high-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$python = 'C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$env:PYTHONPATH = Join-Path $root 'src'
$env:SKILLFLOW_LEAN_RENDERER = 'C:/Users/admin/AppData/Local/skillflow/lean/win32-AMD64/d58f81f68e43b79b2587ad4cf283b45ae69e27be007787110bb461e4ed0a6af4/.lake/build/bin/skill_ir_retell.exe'
$cli = (Get-Command codex -ErrorAction Stop).Source

function Write-Receipt([string]$Name, $Record) {
    $file = [IO.File]::Open((Join-Path $verify $Name), [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    $writer = [IO.StreamWriter]::new($file, [Text.UTF8Encoding]::new($false))
    try { $writer.WriteLine(($Record | ConvertTo-Json -Depth 12)) } finally { $writer.Dispose() }
}

if ((Test-Path -LiteralPath (Join-Path $verify 'dispatch-intent.json')) -or (Test-Path -LiteralPath $run)) {
    throw 'This fresh run has already been claimed'
}
$old = Get-Content -LiteralPath (Join-Path $previousRun 'result.json') -Raw | ConvertFrom-Json
if ($old.status -ne 'failed' -or $old.stage -ne 'revision/review') { throw 'Previous run terminal record differs from the audited state' }
$preflight = Get-Content -LiteralPath (Join-Path $verify 'preflight.json') -Raw | ConvertFrom-Json
$paths = @($preflight.source.PSObject.Properties)
if ($paths.Count -ne 2 -or @(Get-ChildItem -LiteralPath $source -File -Recurse).Count -ne $paths.Count) {
    throw 'Unexpected source inventory'
}
foreach ($entry in $paths) {
    if ((Get-FileHash -LiteralPath (Join-Path $source $entry.Name)).Hash.ToLowerInvariant() -ne $entry.Value) {
        throw "Source digest differs for $($entry.Name)"
    }
}

& $python -m tools.doe.document_guided_pilot prepare --input $source --run-dir $run --effort high *> (Join-Path $verify 'prepare.log')
if ($LASTEXITCODE -ne 0) { throw 'Preparation failed before online dispatch' }
$manifest = Get-Content -LiteralPath (Join-Path $run 'manifest.json') -Raw | ConvertFrom-Json
if ($manifest.implementation.sha256 -ne $preflight.implementation) { throw 'Implementation differs from preflight' }
Write-Receipt 'dispatch-intent.json' @{
    run_directory = $run; at = [DateTime]::UtcNow.ToString('o'); owner = '/root'
    implementation = $manifest.implementation.sha256; manifest_sha256 = $manifest.manifest_sha256
    config = $manifest.config; executable = $cli; executable_sha256 = (Get-FileHash -LiteralPath $cli).Hash.ToLowerInvariant()
    renderer_sha256 = (Get-FileHash -LiteralPath $env:SKILLFLOW_LEAN_RENDERER).Hash.ToLowerInvariant()
    sources = $preflight.source; timeout = 2700; retries = 2; inherited_stages = 0; launches = 1
}

& $python -m tools.doe.document_guided_pilot run --run-dir $run --executable $cli --timeout 2700 --retries 2 *> (Join-Path $verify 'online-run.log')
$code = $LASTEXITCODE
$resultPath = Join-Path $run 'result.json'
$result = if (Test-Path -LiteralPath $resultPath) { Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json } else { $null }
Write-Receipt 'dispatch-terminal.json' @{
    run_directory = $run; at = [DateTime]::UtcNow.ToString('o'); exit_code = $code
    status = $result.status; stage = $result.stage; stages = $result.stages
}
exit $code
