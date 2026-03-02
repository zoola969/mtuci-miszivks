from dataclasses import dataclass
from typing import Optional


@dataclass
class SecurityCheckResult:
    internet_connected: Optional[bool] = None
    firewall_installed: Optional[bool] = None
    antivirus_installed: Optional[str] = None
    firewall_operational: Optional[bool] = None
    antivirus_operational: Optional[bool] = None
