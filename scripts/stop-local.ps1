# Stop local A-Girl + llama-cpp services (by port)
$ErrorActionPreference = "SilentlyContinue"
foreach ($port in @(8011, 11435)) {
    $lines = netstat -ano | Select-String (":$port\s")
    foreach ($line in $lines) {
        if ($line -match "\sLISTENING\s+(\d+)\s*$") {
            $procId = [int]$Matches[1]
            Write-Host ("Stopping PID " + $procId + " on port " + $port)
            Stop-Process -Id $procId -Force
        }
    }
}
Write-Host "Done." -ForegroundColor Green
