param([Parameter(Mandatory=$true)][ValidateSet('/root')][string]$Owner)
$ErrorActionPreference = 'Stop'
$verifyPath = $PSScriptRoot
$projectPath = [IO.Path]::GetFullPath((Join-Path $verifyPath '../../..'))
function Get-Pin([string]$Path) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
$preparedPath = Join-Path $verifyPath 'prepared-run.json'
$preparedRun = Get-Content -LiteralPath $preparedPath -Raw | ConvertFrom-Json
$runPath = [IO.Path]::GetFullPath($preparedRun.run_directory)
$expectedRoot = [IO.Path]::GetFullPath((Join-Path $projectPath 'experiments/doe/runs'))
if ((Split-Path -Parent $runPath) -ne $expectedRoot -or (Split-Path -Leaf $runPath) -notmatch '^document-guided-ga4-runtime-locality-high-[0-9]{8}-[0-9]{6}$') { throw 'Prepared run is outside the exact fresh authorized namespace' }
if ($preparedRun.sole_owner -ne $Owner) { throw 'Only the explicit root owner may dispatch' }
$protocolPath = Join-Path $runPath 'run-protocol.json'
if ((Get-Pin $protocolPath) -ne $preparedRun.run_protocol_sha256) { throw 'Prepared protocol binding changed' }
$protocol = Get-Content -LiteralPath $protocolPath -Raw | ConvertFrom-Json
$acceptancePath = Join-Path $verifyPath '../runtime-locality-20261117/offline-acceptance.json'
if ((Get-Pin $acceptancePath) -ne $preparedRun.offline_acceptance_sha256 -or (Get-Pin $acceptancePath) -ne $protocol.offline_acceptance_sha256) { throw 'Offline acceptance binding changed' }
$acceptance = Get-Content -LiteralPath $acceptancePath -Raw | ConvertFrom-Json
$guardPath = Join-Path $verifyPath 'lifecycle_guard.py'
$guardKey = 'output/verification/online-ga4-runtime-locality-20261117/lifecycle_guard.py'
if ((Get-Pin $guardPath) -ne $acceptance.lifecycle_file_sha256.$guardKey) { throw 'Accepted read-only preflight guard changed' }
$pythonPath = $protocol.python_executable
if ((Get-Pin $pythonPath) -ne $protocol.python_executable_sha256) { throw 'Pinned Python executable changed' }
# This preflight reads only pinned local files. It cannot launch a model or replay.
& $pythonPath -B $guardPath --owner $Owner --verify $verifyPath
if ($LASTEXITCODE -ne 0) { throw 'Read-only lifecycle preflight rejected dispatch' }
$intentPath = Join-Path $verifyPath 'dispatch-intent.json'
$intentStream = [IO.File]::Open($intentPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
$intentWriter = [IO.StreamWriter]::new($intentStream, [Text.UTF8Encoding]::new($false))
try {
    $intentWriter.WriteLine((@{ status = 'dispatch_claimed'; run_directory = $runPath; claimed_at = [DateTime]::UtcNow.ToString('o'); maximum_launches = 1; owner = $Owner; prepared_run_sha256 = (Get-Pin $preparedPath); run_protocol_sha256 = (Get-Pin $protocolPath); offline_acceptance_sha256 = (Get-Pin $acceptancePath) } | ConvertTo-Json))
} finally { $intentWriter.Dispose() }
$controllerPath = Join-Path $runPath 'controller.py'
$controllerProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-B', ('"' + $controllerPath + '"'), '--owner', $Owner) -WorkingDirectory $projectPath -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runPath 'controller.stdout.log') -RedirectStandardError (Join-Path $runPath 'controller.stderr.log') -PassThru
$dispatchReceipt = @{ status = 'dispatched_once'; wrapper_pid = $controllerProcess.Id; started_at = [DateTime]::UtcNow.ToString('o'); run_directory = $runPath; maximum_launches = 1; owner = $Owner; prepared_run_sha256 = (Get-Pin $preparedPath) }
$receiptStream = [IO.File]::Open((Join-Path $verifyPath 'dispatch-started.json'), [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
$receiptWriter = [IO.StreamWriter]::new($receiptStream, [Text.UTF8Encoding]::new($false))
try { $receiptWriter.WriteLine(($dispatchReceipt | ConvertTo-Json)) } finally { $receiptWriter.Dispose() }
$dispatchReceipt | ConvertTo-Json
