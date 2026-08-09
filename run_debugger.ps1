param(
    [string]$Port = 'COM6',
    [int]$Baud = 115200
)

python "$PSScriptRoot\netra_3d_gui.py" --port $Port --baud $Baud
