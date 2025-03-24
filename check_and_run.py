# -------------------------------------------------------------------
# Programmer       : Ebrahim Shafiei (EbraSha)
# Email            : Prof.Shafiei@Gmail.com
# -------------------------------------------------------------------

import subprocess
import sys
import os

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError  # For Python <3.8 with backport

# Path to flag file indicating base tools have already been ensured
FLAG_FILE = ".base_tools_installed.flag"


# Step 1: Ensure pip and setuptools are installed and upgraded (only once)
def ensure_base_tools():
    if os.path.exists(FLAG_FILE):
        # print("[*] Base tools already ensured, skipping...")
        return
    try:
        print("[+] Ensuring pip and setuptools are installed and up-to-date...")
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools"])
        # Create a flag file to remember the setup was done
        with open(FLAG_FILE, "w") as f:
            f.write("base tools installed")
        print("[+] pip and setuptools setup completed.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error while upgrading pip/setuptools: {e}")
        sys.exit(1)


# Step 2: Define required packages and versions
required_packages = {
    "beautifulsoup4": "4.13.3",
    "undetected-chromedriver": "3.5.5",
    "httpx": "0.28.1",
    "colorama": "0.4.6"
}


# Step 3: Check if correct version of package is installed
def is_correct_version_installed(pkg_name, required_version):
    try:
        installed_version = version(pkg_name)
        return installed_version == required_version
    except PackageNotFoundError:
        return False


# Step 4: Install specific package version
def install_package(pkg_name, ver):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", f"{pkg_name}=={ver}"])
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to install {pkg_name}=={ver}: {e}")
        sys.exit(1)


# Execute all steps
if __name__ == "__main__":
    ensure_base_tools()

    for pkg, ver in required_packages.items():
        if not is_correct_version_installed(pkg, ver):
            print(f"[+] Installing or upgrading: {pkg}=={ver}")
            install_package(pkg, ver)

    # Step 5: Run the main script
    subprocess.call([sys.executable, "abdal-web-intelligence-analyzer.py"])
