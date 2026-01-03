```toml
# Test Configuration
module = "packet_groper.scanner"
import = ["discover_subnet", "scan_network", "ScanResult", "NetworkError"]
isolation = "per-block"
```

# Network Scanning

Discovers the local network subnet and scans for live hosts.

**Problem:** Users need to quickly identify which hosts are alive on their local
network. This is useful for network troubleshooting, device discovery, and
inventory. The tool should auto-detect the local subnet and, if it's /22 or
smaller (up to 1022 usable hosts), ping all addresses to build a liveness report.

**Error codes:**
- `[no-interface]` — No active network interface found
- `[unsupported-subnet]` — Subnet is larger than /22 (too many hosts to scan safely)
- `[scan-failed]` — Ping sweep encountered a fatal error

---

## Subnet Discovery

The scanner must detect the local network configuration from active interfaces.

### Discovers Local Subnet

```py
subnet = discover_subnet()
subnet.network_address  # expect: contains(".")
```

### Returns Subnet With CIDR Notation

```py
subnet = discover_subnet()
str(subnet)  # expect: contains("/")
```

### Returns Valid Prefix Length

```py
subnet = discover_subnet()
subnet.prefixlen >= 16 and subnet.prefixlen <= 30  # expect: True
```

### Raises Error When No Interface Available

When there's no active network interface (e.g., disconnected laptop), the
scanner should fail clearly rather than hang or return garbage.

```py
discover_subnet(interface=None)  # error: [no-interface]
```

---

## Network Scanning

Scan all usable host addresses in subnets /22 or smaller.

### Scans All Hosts In /24 Subnet

```py
from ipaddress import ip_network
subnet = ip_network("192.168.1.0/24")
result = scan_network(subnet)
len(result.hosts_scanned)  # expect: 254
```

### Scans All Hosts In /23 Subnet

```py
from ipaddress import ip_network
subnet = ip_network("192.168.0.0/23")
result = scan_network(subnet)
len(result.hosts_scanned)  # expect: 510
```

### Scans All Hosts In /22 Subnet

```py
from ipaddress import ip_network
subnet = ip_network("192.168.0.0/22")
result = scan_network(subnet)
len(result.hosts_scanned)  # expect: 1022
```

### Returns ScanResult With Alive Hosts

```py
from ipaddress import ip_network
subnet = ip_network("192.168.1.0/24")
result = scan_network(subnet)
isinstance(result, ScanResult)  # expect: True
```

### ScanResult Contains Host Status

```py
from ipaddress import ip_network
subnet = ip_network("192.168.1.0/24")
result = scan_network(subnet)
hasattr(result, "alive")  # expect: True
hasattr(result, "dead")  # expect: True
```

### Rejects Subnets Larger Than /22

Scanning subnets larger than /22 (more than 1022 hosts) could take too long
or overwhelm the network. We explicitly reject them to keep the tool safe.

```py
from ipaddress import ip_network
large_subnet = ip_network("10.0.0.0/16")
scan_network(large_subnet)  # error: [unsupported-subnet]
```

### Rejects /21 Subnet

```py
from ipaddress import ip_network
subnet = ip_network("10.0.0.0/21")
scan_network(subnet)  # error: [unsupported-subnet]
```

---

## Report Generation

The scan result should provide a clear, usable report.

### Report Lists Alive Hosts

```py
from ipaddress import ip_network
subnet = ip_network("192.168.1.0/24")
result = scan_network(subnet)
report = result.report()
isinstance(report, str)  # expect: True
```

### Report Contains Summary Stats

```py
from ipaddress import ip_network
subnet = ip_network("192.168.1.0/24")
result = scan_network(subnet)
report = result.report()
"alive" in report.lower()  # expect: True
```

---

## CLI Integration

The CLI `scan` subcommand orchestrates discovery and scanning.

### CLI Scan Command Exists

```sh
packet-groper scan --help
# exit: 0
# stdout: contains("subnet")
```

### CLI Scan Runs Discovery

```sh
packet-groper scan
# exit: 0
# stdout: contains("Scanning")
```

### CLI Reports Alive Hosts

```sh
packet-groper scan
# exit: 0
# stdout: contains("alive")
```
