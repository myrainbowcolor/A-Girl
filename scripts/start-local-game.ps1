param(
    [ValidateSet("1.5b", "7b")]
    [string]$Tier = "7b",
    [switch]$Background
)

& "$PSScriptRoot\start-remote-llm.ps1" -Game -Tier $Tier -Background:$Background
