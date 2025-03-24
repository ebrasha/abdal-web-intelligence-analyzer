#!/bin/bash

# -------------------------------------------------------------------
# Programmer       : Ebrahim Shafiei (EbraSha)
# Email            : Prof.Shafiei@Gmail.com
# -------------------------------------------------------------------

set -e

# Print Banner
clear
echo "=============================================================="
echo "               Google Chrome Manager Script                   "
echo "--------------------------------------------------------------"
echo "  Author   : Ebrahim Shafiei (EbraSha)                        "
echo "  Email    : Prof.Shafiei@Gmail.com                           "
echo "  Purpose  : Install / Uninstall / Check Google Chrome        "
echo "             on Debian and RHEL based Linux distributions     "
echo "=============================================================="
echo ""

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "[-] Cannot detect distribution. /etc/os-release not found."
    exit 1
fi

# -------------------------------
# INSTALL FUNCTION
# -------------------------------
install_chrome_debian() {
    echo "[✓] Debian-based system detected: $DISTRO"
    sudo apt update -y
    sudo apt install wget gnupg2 -y
    wget -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo dpkg -i google-chrome.deb || true
    sudo apt --fix-broken install -y
    sudo dpkg -i google-chrome.deb
    echo "[✓] Google Chrome Installed:"
    google-chrome --version
}

install_chrome_rhel() {
    echo "[✓] RHEL-based system detected: $DISTRO"
    sudo dnf install -y wget || sudo yum install -y wget
    wget -O google-chrome.rpm https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
    sudo dnf localinstall -y google-chrome.rpm || sudo yum localinstall -y google-chrome.rpm
    echo "[✓] Google Chrome Installed:"
    google-chrome --version
}

# -------------------------------
# UNINSTALL FUNCTION
# -------------------------------
uninstall_chrome_debian() {
    echo "[+] Removing Google Chrome..."
    sudo apt remove --purge -y google-chrome-stable
    sudo apt autoremove -y
    echo "[✓] Google Chrome removed."
}

uninstall_chrome_rhel() {
    echo "[+] Removing Google Chrome..."
    sudo dnf remove -y google-chrome-stable || sudo yum remove -y google-chrome-stable
    echo "[✓] Google Chrome removed."
}

# -------------------------------
# CHECK FUNCTION
# -------------------------------
check_chrome() {
    echo "[+] Checking Google Chrome installation..."
    if command -v google-chrome >/dev/null 2>&1; then
        echo "[✓] Google Chrome is installed:"
        google-chrome --version
    else
        echo "[✗] Google Chrome is NOT installed."
    fi
}

# -------------------------------
# MAIN CONTROL
# -------------------------------
case "$1" in
    --install)
        if command -v google-chrome >/dev/null 2>&1; then
            echo "[✓] Google Chrome is already installed."
            google-chrome --version
            exit 0
        fi
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
        ;;
    --uninstall)
        case "$DISTRO" in
            ubuntu|debian|kali|linuxmint)
                uninstall_chrome_debian
                ;;
            centos|rhel|fedora|almalinux|rocky)
                uninstall_chrome_rhel
                ;;
            *)
                echo "[-] Unsupported distribution: $DISTRO"
                exit 1
                ;;
        esac
        ;;
    --check)
        check_chrome
        ;;
    *)
        echo "Usage:"
        echo "  $0 --install     Install Google Chrome"
        echo "  $0 --uninstall   Uninstall Google Chrome"
        echo "  $0 --check       Check if Chrome is installed"
        exit 1
        ;;
esac
