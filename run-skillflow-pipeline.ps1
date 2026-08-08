param(
  [Parameter(Mandatory = $true)]
  [int]$K,

  [string]$Config,
  [string]$Root,
  [ValidateSet("download", "download-group", "fcg", "doe", "all")]
  [string]$Phase,
  [switch]$SemanticLlm,
  [switch]$WithSimilarity,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$nodeScript = Join-Path $scriptDir "scripts\skillflow-pipeline.js"

$argsList = @($nodeScript, "--k", $K)

if ($Config) {
  $argsList += @("--config", $Config)
}
if ($Root) {
  $argsList += @("--root", $Root)
}
if ($Phase) {
  $argsList += @("--phase", $Phase)
}
if ($SemanticLlm) {
  $argsList += "--semantic-llm"
}
if ($WithSimilarity) {
  $argsList += "--with-similarity"
}
if ($DryRun) {
  $argsList += "--dry-run"
}

Push-Location $scriptDir
try {
  & node @argsList
  exit $LASTEXITCODE
} finally {
  Pop-Location
}
