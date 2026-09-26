# TERMINAL TYPER: BATTLE PROTOCOL PowerShell Launcher
$Host.UI.RawUI.WindowTitle = "TERMINAL TYPER: BATTLE PROTOCOL"
try {
    $Host.UI.RawUI.WindowSize = New-Object System.Management.Automation.Host.Size(80, 30)
    $Host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(80, 30)
} catch {
    # Ignore if terminal window resizing is restricted
}

python main.py
