# Install Python
# Check if chocolatey is installed
try {
    choco -v > $null
}
catch {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
}

$package = "%packagename%"
choco install $package -y

$is_installed = choco list -lo $package
if ($is_installed) {
    Write-Host "Package $package installed successfully" -ForegroundColor Green
}
else {
    Write-Host "Package $package installation failed" -ForegroundColor Red
}