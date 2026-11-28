param([Parameter(Mandatory=$true)][ValidateSet('/root')][string]$Owner)
$ErrorActionPreference = 'Stop'
$verify = $PSScriptRoot
$root = [IO.Path]::GetFullPath((Join-Path $verify '../../..'))
$preparedPath = Join-Path $verify 'prepared-run.json'
function Get-Pin([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Write-Once([string]$Path, $Record) {
    $file = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    $writer = [IO.StreamWriter]::new($file, [Text.UTF8Encoding]::new($false))
    try { $writer.WriteLine(($Record | ConvertTo-Json)) } finally { $writer.Dispose() }
}
$prepared = Get-Content -LiteralPath $preparedPath -Raw | ConvertFrom-Json
$run = [IO.Path]::GetFullPath($prepared.run_directory)
if ((Split-Path -Parent $run) -ne (Join-Path $root 'experiments/doe/runs') -or
    (Split-Path -Leaf $run) -notmatch '^document-guided-ga4-program-owned-cfg-high-[0-9]{8}-[0-9]{6}$' -or
    $prepared.sole_owner -ne $Owner) { throw 'Unauthorized run directory or owner' }
$protocolPath = Join-Path $run 'run-protocol.json'
$guard = Join-Path $verify 'lifecycle_guard.py'
if ((Get-Pin $protocolPath) -ne $prepared.run_protocol_sha256 -or
    (Get-Pin $guard) -ne $prepared.verification_pins.'lifecycle_guard.py') { throw 'Dispatch preflight pin changed' }
$protocol = Get-Content -LiteralPath $protocolPath -Raw | ConvertFrom-Json
$python = $protocol.python_executable
if ((Get-Pin $python) -ne $protocol.python_executable_sha256) { throw 'Python executable changed' }
if ((Test-Path (Join-Path $verify 'dispatch-intent.json')) -or (Test-Path (Join-Path $verify 'dispatch-started.json'))) {
    throw 'The one-time dispatch is already claimed'
}
& $python -B $guard --owner $Owner
if ($LASTEXITCODE -ne 0) { throw 'Read-only preflight rejected dispatch' }
Write-Once (Join-Path $verify 'dispatch-intent.json') @{
    status = 'dispatch_claimed'; run_directory = $run; owner = $Owner; maximum_launches = 1
    claimed_at = [DateTime]::UtcNow.ToString('o'); prepared_run_sha256 = (Get-Pin $preparedPath)
    run_protocol_sha256 = (Get-Pin $protocolPath); offline_acceptance_sha256 = $protocol.offline_acceptance_sha256
}
$controller = Join-Path $run 'controller.py'
$process = Start-Process -FilePath $python -ArgumentList @('-B', ('"' + $controller + '"'), '--owner', $Owner) -WorkingDirectory $root -WindowStyle Hidden -RedirectStandardOutput (Join-Path $run 'controller.stdout.log') -RedirectStandardError (Join-Path $run 'controller.stderr.log') -PassThru
$receipt = @{
    status = 'dispatched_once'; wrapper_pid = $process.Id; started_at = [DateTime]::UtcNow.ToString('o')
    run_directory = $run; owner = $Owner; maximum_launches = 1; prepared_run_sha256 = (Get-Pin $preparedPath)
}
Write-Once (Join-Path $verify 'dispatch-started.json') $receipt
$receipt | ConvertTo-Json
