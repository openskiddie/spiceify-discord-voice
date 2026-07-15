Write-Host "Starting setup for Discord VC Spicetify..." -ForegroundColor Cyan

# 1. Check and Install Python safely
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found. Installing via Windows Package Manager..." -ForegroundColor Yellow
    winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    Write-Host "Python installed. (Note: You may need to restart your terminal after setup for Python to register)." -ForegroundColor Yellow
} else {
    Write-Host "Python is already installed. Skipping." -ForegroundColor Green
}

# 2. Check and Install Spicetify safely
if (-not (Get-Command "spicetify" -ErrorAction SilentlyContinue)) {
    Write-Host "Spicetify not found. Installing Spicetify..." -ForegroundColor Yellow
    Invoke-WebRequest -UseBasicParsing "https://raw.githubusercontent.com/spicetify/cli/main/install.ps1" | Invoke-Expression
} else {
    Write-Host "Spicetify is already installed. Skipping." -ForegroundColor Green
}

# 3. Install Python Dependencies
if (Test-Path "requirements.txt") {
    Write-Host "Installing Python requirements..." -ForegroundColor Cyan
    # pip automatically skips packages that are already installed, so this is always safe to run
    python -m pip install -r requirements.txt
}

# 4. Install and Apply the Extension
if (Test-Path "discord-vc.js") {
    Write-Host "Copying extension to Spicetify folder..." -ForegroundColor Cyan
    $extensionDir = "$env:APPDATA\spicetify\Extensions"
    
    # Create the folder if it somehow doesn't exist
    if (-not (Test-Path $extensionDir)) { 
        New-Item -ItemType Directory -Force -Path $extensionDir 
    }
    
    Copy-Item -Path "discord-vc.js" -Destination "$extensionDir\discord-vc.js" -Force
    
    Write-Host "Applying Spicetify configuration..." -ForegroundColor Cyan
    spicetify config extensions discord-vc.js
    spicetify apply
} else {
    Write-Host "Error: discord-vc.js not found in the current folder." -ForegroundColor Red
}

Write-Host "Setup complete! You can now run the Python bridge." -ForegroundColor Green
Pause