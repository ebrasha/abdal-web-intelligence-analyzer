# -------------------------------------------------------------------
# Programmer       : Ebrahim Shafiei (EbraSha)
# Email            : Prof.Shafiei@Gmail.com
# -------------------------------------------------------------------

import subprocess
import sys

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError  # For Python <3.8 with backport

# Define required packages and versions
required_packages = {
    "beautifulsoup4": "4.13.3",
    "undetected-chromedriver": "3.5.5",
    "httpx": "0.28.1",
    "colorama": "0.4.6"
}

def is_correct_version_installed(pkg_name, required_version):
    try:
        installed_version = version(pkg_name)
        return installed_version == required_version
    except PackageNotFoundError:
        return False

def install_package(pkg_name, ver):
    subprocess.check_call([sys.executable, "-m", "pip", "install", f"{pkg_name}=={ver}"])

# Check and install missing or incorrect versions
for pkg, ver in required_packages.items():
    if not is_correct_version_installed(pkg, ver):
        print(f"[+] Installing or upgrading: {pkg}=={ver}")
        install_package(pkg, ver)


# Run main script
subprocess.call([sys.executable, "abdal-web-intelligence-analyzer.py"])
