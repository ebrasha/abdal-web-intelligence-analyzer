#!/bin/bash

# -------------------------------------------------------------------
# Programmer       : Ebrahim Shafiei (EbraSha)
# Email            : Prof.Shafiei@Gmail.com
# -------------------------------------------------------------------

set -e

# Print Banner
clear
echo "=============================================================="
echo "               Google Chrome Auto Installer Script            "
echo "--------------------------------------------------------------"
echo "  Author   : Ebrahim Shafiei (EbraSha)                        "
echo "  Email    : Prof.Shafiei@Gmail.com                           "
echo "  Purpose  : Automatically installs Google Chrome             "
echo "             on Debian/Ubuntu/Kali and RHEL/CentOS/Fedora     "
echo "             with smart dependency fix and version check.     "
echo "=============================================================="
echo ""

# Check if Chrome is already installed
echo "[+] Checking if Google Chrome is already installed..."

if command -v google-chrome >/dev/null 2>&1; then
    echo "[✓] Google Chrome is already installed."
    google-chrome --version
    exit 0
fi

echo "[!] Google Chrome not found. Proceeding with installation..."

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "[-] Cannot detect distribution. /etc/os-release not found."
    exit 1
fi

# Function for Debian-based systems
install_chrome_debian() {
    echo "[✓] Debian-based system detected: $DISTRO"
    sudo apt update -y
    sudo apt install wget gnupg2 -y

    echo "[+] Downloading Chrome package..."
    wget -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

    echo "[+] Installing Chrome..."
    sudo dpkg -i google-chrome.deb || true

    echo "[+] Fixing broken dependencies if needed..."
    sudo apt --fix-broken install -y
    sudo dpkg -i google-chrome.deb

    echo "[+] Installation complete:"
    google-chrome --version
}

# Function for RHEL-based systems
install_chrome_rhel() {
    echo "[✓] RHEL-based system detected: $DISTRO"
    sudo dnf install -y wget || sudo yum install -y wget

    echo "[+] Downloading Chrome package..."
    wget -O google-chrome.rpm https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm

    echo "[+] Installing Chrome..."
    sudo dnf localinstall -y google-chrome.rpm || sudo yum localinstall -y google-chrome.rpm

    echo "[+] Installation complete:"
    google-chrome --version
}

# Dispatch based on distro
case "$DISTRO" in
    ubuntu|debian|kali|linuxmint)
        install_chrome_debian
        ;;
    centos|rhel|fedora|almalinux|rocky)
        install_chrome_rhel
        ;;
    *)
        echo "[-] Unsupported distribution: $DISTRO"
        exit 1
        ;;
esac
