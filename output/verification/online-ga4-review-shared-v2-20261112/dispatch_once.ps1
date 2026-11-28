$ErrorActionPreference = 'Stop'
$verifyPath = $PSScriptRoot
$preparedRun = Get-Content -LiteralPath (Join-Path $verifyPath 'prepared-run.json') -Raw | ConvertFrom-Json
$runPath = [IO.Path]::GetFullPath($preparedRun.run_directory)
$expectedRoot = [IO.Path]::GetFullPath('D:/Projects/SkillFlow/experiments/doe/runs') + [IO.Path]::DirectorySeparatorChar
if (-not $runPath.StartsWith($expectedRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Prepared run is outside the authorized workspace run directory' }
if ((Split-Path -Leaf $runPath) -ne 'document-guided-ga4-review-shared-v2-high-20261112-221242') { throw 'This dispatch belongs to the sole prepared fresh run' }
foreach ($markerName in @('controller-started.json', 'replay-started.json', 'controller-finished.json')) {
    if (Test-Path -LiteralPath (Join-Path $runPath $markerName)) { throw "Run already has $markerName" }
}
$savedResult = Get-Content -LiteralPath (Join-Path $runPath 'result.json') -Raw | ConvertFrom-Json
if ($savedResult.status -ne 'prepared') { throw 'Only a fresh prepared run can be dispatched' }
$intentPath = Join-Path $verifyPath 'dispatch-intent.json'
$intentStream = [IO.File]::Open($intentPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
$intentWriter = [IO.StreamWriter]::new($intentStream, [Text.UTF8Encoding]::new($false))
try {
    $intentWriter.WriteLine((@{ status = 'dispatch_claimed'; run_directory = $runPath; claimed_at = [DateTime]::UtcNow.ToString('o'); maximum_launches = 1; owner = '/root' } | ConvertTo-Json))
} finally { $intentWriter.Dispose() }
$pythonPath = 'C:/Users/admin/AppData/Local/Temp/skillflow-input-contracts-20261111-venv/Scripts/python.exe'
$controllerPath = Join-Path $runPath 'controller.py'
$controllerProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-B', ('"' + $controllerPath + '"')) -WorkingDirectory 'D:/Projects/SkillFlow' -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runPath 'controller.stdout.log') -RedirectStandardError (Join-Path $runPath 'controller.stderr.log') -PassThru
$dispatchReceipt = @{ status = 'dispatched_once'; wrapper_pid = $controllerProcess.Id; started_at = [DateTime]::UtcNow.ToString('o'); run_directory = $runPath; maximum_launches = 1; owner = '/root' }
[IO.File]::WriteAllText((Join-Path $verifyPath 'dispatch-started.json'), ($dispatchReceipt | ConvertTo-Json) + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
$dispatchReceipt | ConvertTo-Json
