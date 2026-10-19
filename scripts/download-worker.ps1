param(
    [Parameter(Mandatory)][string]$Url,
    [Parameter(Mandatory)][string]$WorkFile,
    [Parameter(Mandatory)][string]$WorkerId
)
$ErrorActionPreference = "Continue"
$blocks = Import-Csv $WorkFile
foreach ($b in $blocks) {
    $exp = [int64]$b.exp
    if ((Test-Path $b.part) -and (Get-Item $b.part).Length -eq $exp) { continue }
    for ($t = 0; $t -lt 6; $t++) {
        if (Test-Path $b.part) { Remove-Item $b.part -Force -ErrorAction SilentlyContinue }
        & curl.exe -s -L --fail --connect-timeout 20 --max-time 180 `
            -r "$($b.s)-$($b.e)" -o $b.part $Url
        if ($LASTEXITCODE -eq 0 -and (Test-Path $b.part) -and (Get-Item $b.part).Length -eq $exp) { break }
        Start-Sleep -Milliseconds 800
    }
}
