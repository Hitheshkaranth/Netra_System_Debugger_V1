$ErrorActionPreference = 'Stop'

python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name Netra_System_Debugger_V1 `
    --add-data "netra_scene.qml;." `
    --add-data "assets;assets" `
    netra_3d_gui.py

Write-Host "Build complete: $PSScriptRoot\dist\Netra_System_Debugger_V1\Netra_System_Debugger_V1.exe"
