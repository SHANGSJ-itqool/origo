[CmdletBinding()]
param(
    [string]$Iso = "H:\origo\dist\origo-v0.1-amd64.iso",
    [string]$VmName = "OrigoTest",
    [string]$VhdPath = "H:\origo\vm\OrigoTest.vhdx",
    [int64]$VhdSize = 40GB
)
$ErrorActionPreference = "Stop"

if (-not (Test-Path $Iso)) { throw "ISO not found: $Iso (download it first)." }

# Use the Hyper-V "Default Switch" (NAT, provides DHCP + internet).
$sw = Get-VMSwitch -Name "Default Switch" -ErrorAction SilentlyContinue
if (-not $sw) { $sw = Get-VMSwitch | Select-Object -First 1 }
if (-not $sw) { throw "No virtual switch found. Open Hyper-V Manager and create one." }

New-Item -ItemType Directory -Force -Path (Split-Path $VhdPath) | Out-Null

# Replace an existing test VM.
if (Get-VM -Name $VmName -ErrorAction SilentlyContinue) {
    Stop-VM -Name $VmName -Force -ErrorAction SilentlyContinue
    Remove-VM -Name $VmName -Force
}
if (Test-Path $VhdPath) { Remove-Item $VhdPath -Force }

$null = New-VHD -Path $VhdPath -SizeBytes $VhdSize -Generation 2
$null = New-VM -Name $VmName -Generation 2 -MemoryStartupBytes 2GB `
    -VHDPath $VhdPath -SwitchName $sw.Name
Set-VM -Name $VmName -ProcessorCount 4 -CheckpointType Disabled
Set-VMMemory -VMName $VmName -DynamicMemoryEnabled $true -MinimumBytes 1GB -StartupBytes 2GB -MaximumBytes 6GB

# Attach the ISO as a DVD drive, boot from it first.
Add-VMDvdDrive -VMName $VmName -Path $Iso
$dvd = Get-VMDvdDrive -VMName $VmName
Set-VMFirmware -VMName $VmName -FirstBootDevice $dvd

# Disable Secure Boot for the test (Debian also supports the Microsoft UEFI CA template).
Set-VMFirmware -VMName $VmName -EnableSecureBoot Off

Write-Host "Starting VM '$VmName' booting $Iso ..."
Start-VM -Name $VmName
Start-Sleep 2
Get-VM -Name $VmName | Format-List Name, State, Uptime
Write-Host "Open 'vmconnect.exe localhost $VmName' (or Hyper-V Manager) for the screen."
