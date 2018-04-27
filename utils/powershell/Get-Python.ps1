# Install Python
# Check if chocolatey is installed
try {
    choco -v > $null
}
catch {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
}

$pyver = "%pythonversion%"
choco install $pyver -y