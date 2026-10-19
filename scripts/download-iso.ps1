[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Url,
    [Parameter(Mandatory)][string]$OutFile,
    [int]$Threads = 8,
    [int]$BlockMB = 8
)
$ErrorActionPreference = "Stop"

$dir = Split-Path $OutFile -Parent
$tmpDir = Join-Path $dir ".parts"
New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null

function Get-RemoteSize([string]$u) {
    try {
        $r = [System.Net.HttpWebRequest]::Create($u); $r.Method = "HEAD"; $r.AllowAutoRedirect = $true
        $r.Timeout = 20000
        $s = $r.GetResponse(); $len = [int64]$s.ContentLength; $s.Close(); return $len
    } catch { return [int64]0 }
}

$size = Get-RemoteSize $Url
if ($size -le 0) {
    $r = [System.Net.HttpWebRequest]::Create($Url); $r.AddRange(0, 0); $r.Timeout = 20000
    $s = $r.GetResponse(); $cr = $s.Headers["Content-Range"]; $size = [int64]($cr -split "/")[-1]; $s.Close()
}
Write-Host "Remote size: $size bytes ($([math]::Round($size/1MB,1)) MB)"

$block = [int64]$BlockMB * 1MB
$work = New-Object 'System.Collections.Concurrent.ConcurrentQueue[hashtable]'
$totalBlocks = 0
$idx = 0
for ($off = 0; $off -lt $size; $off += $block) {
    $end = [Math]::Min($off + $block - 1, $size - 1)
    $part = Join-Path $tmpDir ("part-{0:D5}" -f $idx)
    $expected = $end - $off + 1
    if (-not (Test-Path $part) -or (Get-Item $part).Length -ne $expected) {
        $work.Enqueue(@{ s = $off; e = $end; part = $part; exp = $expected })
    }
    $totalBlocks++; $idx++
}
Write-Host "Blocks: $totalBlocks total, $($work.Count) to download"

$worker = {
    param($cq, $u)
    $b = $null
    while ($cq.TryDequeue([ref]$b)) {
        $done = $false
        for ($t = 0; $t -lt 6 -and -not $done; $t++) {
            $fs = $null; $st = $null; $resp = $null
            try {
                $rq = [System.Net.HttpWebRequest]::Create($u); $rq.AddRange($b.s, $b.e)
                $rq.Timeout = 30000; $rq.ReadWriteTimeout = 90000
                $resp = $rq.GetResponse(); $st = $resp.GetResponseStream()
                $fs = [System.IO.File]::Create($b.part)
                $st.CopyTo($fs); $fs.Flush(); $fs.Close(); $st.Close(); $resp.Close()
                if ((Get-Item $b.part).Length -eq $b.exp) { $done = $true }
            } catch {
                if ($fs) { try { $fs.Close() } catch {} }
                if ($st) { try { $st.Close() } catch {} }
                if ($resp) { try { $resp.Close() } catch {} }
                Start-Sleep -Milliseconds 700
            }
        }
    }
}

$pool = [RunspaceFactory]::CreateRunspacePool(1, $Threads)
$pool.Open()
$handles = @()
for ($i = 0; $i -lt $Threads; $i++) {
    $ps = [PowerShell]::Create(); $ps.RunspacePool = $pool
    [void]$ps.AddScript($worker).AddArgument($work).AddArgument($Url)
    $handles += [pscustomobject]@{ ps = $ps; h = $ps.BeginInvoke() }
}

while ($handles.h.IsCompleted -notcontains $true -or $handles.h.IsCompleted -contains $false) {
    Start-Sleep 4
    $doneBytes = [int64]0
    Get-ChildItem $tmpDir -Filter "part-*" -ErrorAction SilentlyContinue | ForEach-Object { $doneBytes += $_.Length }
    $pct = [math]::Round(100 * $doneBytes / $size, 1)
    Write-Host ("Progress: {0}%  ({1}/{2} MB)" -f $pct, [math]::Round($doneBytes/1MB,1), [math]::Round($size/1MB,1))
    if ($handles.h.IsCompleted -notcontains $false) { break }
}
foreach ($x in $handles) { $x.ps.EndInvoke($x.h); $x.ps.Dispose() }
$pool.Close(); $pool.Dispose()

$okBlocks = (Get-ChildItem $tmpDir -Filter "part-*" | Where-Object { $_.Length -gt 0 }).Count
if ($okBlocks -lt $totalBlocks) {
    throw "Only $okBlocks of $totalBlocks blocks downloaded. Re-run script to resume."
}

Write-Host "Merging blocks to $OutFile ..."
if (Test-Path $OutFile) { Remove-Item $OutFile -Force }
$out = [System.IO.File]::Create($OutFile)
for ($i = 0; $i -lt $totalBlocks; $i++) {
    $part = Join-Path $tmpDir ("part-{0:D5}" -f $i)
    $bytes = [System.IO.File]::ReadAllBytes($part)
    $out.Write($bytes, 0, $bytes.Length)
}
$out.Close()
Write-Host "Done. Final size: $((Get-Item $OutFile).Length) bytes"
Remove-Item $tmpDir -Recurse -Force
