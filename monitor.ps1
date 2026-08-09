# Project NETRA - continuous serial monitor for the Glyph C6.
#
# Use this instead of the Arduino IDE Serial Monitor. The IDE toggles DTR/RTS
# when it opens the port, and on the ESP32-C6 those lines are strapped to EN
# and BOOT, so it reboots the chip into serial download mode - you get
# "ESP-ROM:esp32c6-20220919" and nothing else. This script sets both lines
# once before opening and never touches them again, so the sketch keeps running.
#
#   powershell -ExecutionPolicy Bypass -File monitor.ps1
#
# Ctrl+C to stop.

param(
    [string]$Port = 'COM6',
    [int]$Baud = 115200,
    [switch]$Csv,          # write rows to netra-log.csv as well
    [switch]$Quiet         # suppress the per-row echo, just show the counter
)

$sp = New-Object System.IO.Ports.SerialPort $Port, $Baud, 'None', 8, 'One'
$sp.ReadTimeout = 500
$sp.DtrEnable   = $true
$sp.RtsEnable   = $true
$sp.NewLine     = "`n"

try {
    $sp.Open()
} catch {
    Write-Host "Could not open $Port : $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Something else owns the port - close the Arduino Serial Monitor." -ForegroundColor Yellow
    exit 1
}

$logPath = Join-Path $PSScriptRoot 'netra-log.csv'
if ($Csv) {
    Set-Content -Path $logPath -Value 'host_ms,distance_cm,echo_us,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,temp_c,status' -Encoding utf8
    Write-Host "logging to $logPath" -ForegroundColor Cyan
}

Write-Host "Connected to $Port. Ctrl+C to stop." -ForegroundColor Green

$sb    = New-Object System.Text.StringBuilder
$t0    = Get-Date
$rows  = 0
$errs  = 0

try {
    while ($true) {
        try {
            $chunk = $sp.ReadExisting()
            if ($chunk) {
                [void]$sb.Append($chunk)
                $parts = $sb.ToString() -split "`n"
                for ($i = 0; $i -lt $parts.Count - 1; $i++) {
                    $line = $parts[$i].TrimEnd("`r")
                    if ($line -eq '') { continue }

                    $isRow = $line -match '^(-?[0-9]+\.[0-9]+|nan),'
                    if ($isRow) {
                        $rows++
                        if ($line -match 'RANGE_TIMEOUT|IMU_ERROR') { $errs++ }
                        if ($Csv) {
                            $ms = [int]((Get-Date) - $t0).TotalMilliseconds
                            Add-Content -Path $logPath -Value "$ms,$line" -Encoding utf8
                        }
                        if (-not $Quiet) {
                            $color = if ($line -match 'RANGE_TIMEOUT|IMU_ERROR') { 'Yellow' } else { 'Gray' }
                            Write-Host $line -ForegroundColor $color
                        }
                        if ($Quiet -and ($rows % 10 -eq 0)) {
                            $el = ((Get-Date) - $t0).TotalSeconds
                            Write-Host ("`r{0} rows  {1:N2}/s  {2} flagged" -f $rows, ($rows / $el), $errs) -NoNewline
                        }
                    } else {
                        # Banner, I2C scan, ROM messages.
                        $color = if ($line -match 'ESP-ROM') { 'Red' } else { 'Cyan' }
                        Write-Host $line -ForegroundColor $color
                        if ($line -match 'ESP-ROM') {
                            Write-Host "  ^ board is in download mode, not running the sketch." -ForegroundColor Red
                            Write-Host "    tap EN, or run the esptool hard-reset command." -ForegroundColor Red
                        }
                    }
                }
                [void]$sb.Clear()
                [void]$sb.Append($parts[$parts.Count - 1])
            }
        } catch [TimeoutException] { }
        Start-Sleep -Milliseconds 30
    }
} finally {
    $el = ((Get-Date) - $t0).TotalSeconds
    if ($el -gt 0) {
        Write-Host ""
        Write-Host ("stopped: {0} rows in {1:N1} s = {2:N2} rows/s, {3} flagged" -f $rows, $el, ($rows / $el), $errs) -ForegroundColor Green
    }
    $sp.Close()
    $sp.Dispose()
}
