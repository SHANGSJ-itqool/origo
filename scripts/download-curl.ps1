[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Url,
    [Parameter(Mandatory)][string]$OutFile,
    [int]$Workers = 8,
    [int]$BlockMB = 8
)
$ErrorActionPreference = "Stop"

$dir = Split-Path $OutFile -Parent
$tmpDir = Join-Path $dir ".parts"
$workDir = Join-Path $dir ".work"
New-Item -ItemType Directory -Force -Path $tmpDir, $workDir | Out-Null

# Remote size via a single-byte Range request (works through proxies).
$size = [int64]0
try {
    $r = [System.Net.HttpWebRequest]::Create($Url); $r.Method = "HEAD"; $r.AllowAutoRedirect = $true; $r.Timeout = 20000
    $s = $r.GetResponse(); $size = [int64]$s.ContentLength; $s.Close()
} catch {}
if ($size -le 0) {
    $r = [System.Net.HttpWebRequest]::Create($Url); $r.AddRange(0, 0); $r.Timeout = 20000
    $s = $r.GetResponse(); $cr = $s.Headers["Content-Range"]; $size = [int64]($cr -split "/")[-1]; $s.Close()
}
Write-Host "Remote size: $([math]::Round($size/1MB,1)) MB"

$block = [int64]$BlockMB * 1MB
$totalBlocks = 0
$all = New-Object System.Collections.ArrayList
$idx = 0
for ($off = 0; $off -lt $size; $off += $block) {
    $end = [Math]::Min($off + $block - 1, $size - 1)
    $part = Join-Path $tmpDir ("part-{0:D5}" -f $idx)
    $expected = $end - $off + 1
    [void]$all.Add([pscustomobject]@{ s = $off; e = $end; part = $part; exp = $expected })
    $totalBlocks++; $idx++
}

# Round-robin distribute blocks among worker CSV files.
for ($w = 0; $w -lt $Workers; $w++) {
    $wf = Join-Path $workDir ("worker-{0}.csv" -f $w)
    $set = @()
    for ($i = $w; $i -lt $totalBlocks; $i += $Workers) { $set += $all[$i] }
    $set | Export-Csv $wf -NoTypeInformation
}

# Launch one independent PowerShell process per worker (each uses curl.exe).
$workerScript = Join-Path (Split-Path $MyInvocation.MyCommand.Path) "download-worker.ps1"
$procs = @()
for ($w = 0; $w -lt $Workers; $w++) {
    $wf = Join-Path $workDir ("worker-{0}.csv" -f $w)
    $p = Start-Process powershell -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-File",$workerScript,"-Url",$Url,"-WorkFile",$wf,"-WorkerId",$w `
        -PassThru -WindowStyle Hidden
    $procs += $p
}

while ($procs.HasExited -contains $false) {
    Start-Sleep 5
    $doneBytes = [int64]0
    Get-ChildItem $tmpDir -Filter "part-*" -ErrorAction SilentlyContinue | ForEach-Object { $doneBytes += $_.Length }
    Write-Host ("{0}%  ({1}/{2} MB)" -f [math]::Round(100*$doneBytes/$size,1), [math]::Round($doneBytes/1MB,1), [math]::Round($size/1MB,1))
}
$procs | Wait-Process -Timeout 30 -ErrorAction SilentlyContinue

$ok = (Get-ChildItem $tmpDir -Filter "part-*" | Where-Object { $_.Length -gt 0 }).Count
if ($ok -lt $totalBlocks) { throw "Only $ok of $totalBlocks blocks. Re-run to resume." }

Write-Host "Merging..."
if (Test-Path $OutFile) { Remove-Item $OutFile -Force }
$out = [System.IO.File]::Create($OutFile)
for ($i = 0; $i -lt $totalBlocks; $i++) {
    $bytes = [System.IO.File]::ReadAllBytes((Join-Path $tmpDir ("part-{0:D5}" -f $i)))
    $out.Write($bytes, 0, $bytes.Length)
}
$out.Close()
Write-Host "Done: $((Get-Item $OutFile).Length) bytes"
Remove-Item $tmpDir, $workDir -Recurse -Force -ErrorAction SilentlyContinue
