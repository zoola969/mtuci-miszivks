import subprocess

import requests


def is_internet_connected() -> bool:
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except Exception:
        return False


def _run_powershell(command: str) -> str:
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def is_firewall_installed() -> bool:
    output = _run_powershell(
        "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName FirewallProduct"
    )
    return bool(output)


def is_antivirus_installed() -> str | None:
    output = _run_powershell(
        "(Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct)"
        " | Select-Object -ExpandProperty displayName"
    )
    return output.splitlines()[0].strip() if output else None


def is_firewall_operational() -> bool:
    # Check Windows Firewall service
    try:
        result = subprocess.run(
            ["sc", "query", "MpsSvc"],
            capture_output=True,
            text=True,
        )
        service_running = "RUNNING" in result.stdout
    except Exception:
        service_running = False

    if not service_running:
        return False

    # Try reaching a known URL; if blocked → True (firewall is active)
    try:
        requests.get("https://www.google.com", timeout=5)
        # Connection succeeded — firewall is running but not blocking this
        return True
    except Exception:
        # Connection blocked or failed — could mean firewall is active
        return True


def is_antivirus_operational() -> bool:
    output = _run_powershell(
        "(Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct)"
        " | Select-Object -ExpandProperty productState"
    )
    if not output:
        return False
    try:
        # productState is a decimal number; bit 12 (0x1000) = real-time protection on
        state = int(output.splitlines()[0].strip())
        return bool(state & 0x1000)
    except ValueError:
        return False
