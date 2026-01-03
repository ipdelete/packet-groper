"""Network scanning functionality for packet-groper."""

import subprocess
import socket
import struct
import fcntl
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from ipaddress import IPv4Network, IPv4Address
from typing import List, Optional


class NetworkError(Exception):
    """Exception for network-related errors."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


@dataclass
class ScanResult:
    """Results from a network scan."""

    subnet: IPv4Network
    hosts_scanned: List[IPv4Address] = field(default_factory=list)
    alive: List[IPv4Address] = field(default_factory=list)
    dead: List[IPv4Address] = field(default_factory=list)

    def report(self) -> str:
        """Generate a human-readable report of scan results."""
        lines = [
            f"Scan Results for {self.subnet}",
            f"{'=' * 40}",
            f"Hosts scanned: {len(self.hosts_scanned)}",
            f"Alive: {len(self.alive)}",
            f"Dead: {len(self.dead)}",
            "",
            "Alive hosts:",
        ]
        for host in sorted(self.alive):
            lines.append(f"  {host}")
        return "\n".join(lines)


def get_interfaces() -> List[str]:
    """Get list of active network interfaces."""
    interfaces = []
    try:
        with open("/proc/net/route") as f:
            for line in f.readlines()[1:]:
                parts = line.strip().split()
                if parts[1] != "00000000":  # Skip default route
                    continue
                interfaces.append(parts[0])
    except FileNotFoundError:
        # macOS fallback - use socket to find default interface
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            # Get the interface name (we'll use the IP instead on macOS)
            interfaces.append("default")
            s.close()
        except Exception:
            pass
    return interfaces


def _get_local_ip() -> Optional[str]:
    """Get the local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def _get_netmask() -> Optional[str]:
    """Get the netmask for the default interface."""
    try:
        # Try using ifconfig on macOS
        result = subprocess.run(
            ["ifconfig"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        local_ip = _get_local_ip()
        if not local_ip:
            return None

        lines = result.stdout.split("\n")
        for i, line in enumerate(lines):
            if local_ip in line:
                # Look for netmask in same or nearby lines
                for j in range(max(0, i - 2), min(len(lines), i + 3)):
                    if "netmask" in lines[j]:
                        parts = lines[j].split()
                        for k, part in enumerate(parts):
                            if part == "netmask" and k + 1 < len(parts):
                                mask = parts[k + 1]
                                # Convert hex netmask to dotted decimal if needed
                                if mask.startswith("0x"):
                                    mask_int = int(mask, 16)
                                    return socket.inet_ntoa(struct.pack(">I", mask_int))
                                return mask
        # Default to /24 if we can't determine
        return "255.255.255.0"
    except Exception:
        return "255.255.255.0"


def discover_subnet(interface: Optional[str] = "auto") -> IPv4Network:
    """Discover the local network subnet.

    Args:
        interface: Network interface to use, or "auto" for auto-detection.
                  Pass None to simulate no interface available.

    Returns:
        IPv4Network representing the local subnet.

    Raises:
        NetworkError: If no interface is available or subnet cannot be determined.
    """
    if interface is None:
        raise NetworkError("no-interface", "No active network interface found")

    interfaces = get_interfaces()
    if not interfaces:
        raise NetworkError("no-interface", "No active network interface found")

    local_ip = _get_local_ip()
    if not local_ip:
        raise NetworkError("no-interface", "Could not determine local IP address")

    netmask = _get_netmask()
    if not netmask:
        raise NetworkError("no-interface", "Could not determine network mask")

    # Calculate network address
    network = IPv4Network(f"{local_ip}/{netmask}", strict=False)
    return network


def _ping_host(ip: IPv4Address, timeout: float = 0.5) -> bool:
    """Ping a single host to check if it's alive.

    Args:
        ip: IP address to ping.
        timeout: Timeout in seconds.

    Returns:
        True if host responds, False otherwise.
    """
    try:
        # Use system ping command with short timeout
        # macOS uses -W in ms, Linux uses -W in seconds
        import platform
        if platform.system() == "Darwin":
            timeout_arg = str(int(timeout * 1000))  # macOS: milliseconds
        else:
            timeout_arg = str(int(timeout))  # Linux: seconds

        result = subprocess.run(
            ["ping", "-c", "1", "-W", timeout_arg, str(ip)],
            capture_output=True,
            timeout=timeout + 0.5,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def scan_network(
    subnet: IPv4Network,
    timeout: float = 0.5,
    max_workers: int = 100,
) -> ScanResult:
    """Scan all hosts in a subnet to find alive hosts.

    Args:
        subnet: The subnet to scan (must be /22 or smaller).
        timeout: Ping timeout per host in seconds.
        max_workers: Maximum concurrent ping threads.

    Returns:
        ScanResult containing alive and dead hosts.

    Raises:
        NetworkError: If subnet is larger than /22.
    """
    if subnet.prefixlen < 22:
        raise NetworkError(
            "unsupported-subnet",
            f"Only /22 or smaller subnets are supported, got /{subnet.prefixlen}",
        )

    result = ScanResult(subnet=subnet)
    hosts = list(subnet.hosts())  # Excludes network and broadcast addresses
    result.hosts_scanned = hosts

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(_ping_host, ip, timeout): ip for ip in hosts}

        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                if future.result():
                    result.alive.append(ip)
                else:
                    result.dead.append(ip)
            except Exception:
                result.dead.append(ip)

    return result
