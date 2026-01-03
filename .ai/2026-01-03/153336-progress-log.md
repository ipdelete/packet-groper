# Progress Log

**Date:** 2026-01-03
**Session:** 153336
**Overview:** Built a network scanning CLI tool using TDD with literate tests. The tool discovers the local subnet and pings all hosts to report which are alive. Supports /22 and smaller subnets (up to 1022 hosts).

---

## What We Built

### 1. Network Scanner Module
Core scanning functionality with subnet discovery and concurrent ping sweep.

- **Subnet Discovery** (`scanner.py:116-146`): Auto-detects local network using socket connections and ifconfig parsing
- **Ping Sweep** (`scanner.py:180-220`): Concurrent host scanning with ThreadPoolExecutor (100 workers)
- **ScanResult** (`scanner.py:21-43`): Dataclass holding scan results with report generation

### 2. CLI Scan Command
Added `scan` subcommand to the existing CLI.

- **cmd_scan** (`cli.py:10-37`): Orchestrates discovery, scanning, and reporting
- **Subparser** (`cli.py:51-62`): Adds `packet-groper scan` with `--subnet` option

### 3. Literate Test Suite
Markdown-based executable tests following TDD red/green cycle.

- **16 tests** covering: subnet discovery, network scanning, report generation, CLI integration
- **Custom runner** that parses markdown and executes code blocks with assertions

---

## Files Created/Modified

### Created
| File | Description |
|------|-------------|
| `src/packet_groper/scanner.py` | Network scanning module (220 lines) |
| `tests/network_scan.md` | Literate test specification (183 lines) |
| `tests/run_tests.py` | Test runner for markdown tests |

### Modified
| File | Changes |
|------|---------|
| `src/packet_groper/cli.py` | Added `scan` subcommand, imports, cmd_scan function |

### Existing (unchanged)
| File | Purpose |
|------|---------|
| `src/packet_groper/__init__.py` | Package init with version |
| `src/packet_groper/__main__.py` | Entry point for `python -m` |

---

## Key Concepts Explained

### Literate Testing Pattern
Tests are written as markdown files with embedded code blocks. The prose explains *why*, code blocks are the actual tests:

```markdown
### Rejects Subnets Larger Than /22

Scanning subnets larger than /22 (more than 1022 hosts) could take too long.

\`\`\`py
scan_network(ip_network("10.0.0.0/16"))  # error: [unsupported-subnet]
\`\`\`
```

Assertions use comment syntax:
- `# expect: <value>` - Assert equality
- `# error: [code]` - Assert exception with `.code` attribute
- `# exit: N` - Assert CLI exit code
- `# stdout: contains("text")` - Assert output contains string

### Concurrent Ping Architecture

```
┌─────────────────────────────────────────────────────┐
│                  scan_network()                      │
├─────────────────────────────────────────────────────┤
│  subnet.hosts() → [192.168.1.1, ..., 192.168.1.254] │
│                         │                            │
│           ┌─────────────┼─────────────┐              │
│           ▼             ▼             ▼              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ ThreadPool   │ │ ThreadPool   │ │ ThreadPool   │  │
│  │ Worker 1     │ │ Worker 2     │ │ Worker N     │  │
│  │ _ping_host() │ │ _ping_host() │ │ _ping_host() │  │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘  │
│         │                │                │          │
│         └────────────────┼────────────────┘          │
│                          ▼                           │
│                   ScanResult                         │
│                   - alive: [...]                     │
│                   - dead: [...]                      │
└─────────────────────────────────────────────────────┘
```

### Error Code Pattern
Exceptions have a `.code` attribute for test matching:

```python
class NetworkError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code  # e.g., "no-interface", "unsupported-subnet"
        super().__init__(message)
```

---

## How to Use

### Run the Scanner
```bash
# Scan local network (auto-discovers subnet)
uv run packet-groper scan

# Show help
uv run packet-groper scan --help
```

### Run Tests
```bash
uv run python tests/run_tests.py
```

### Example Output
```
Scanning local network...
Discovered subnet: 192.168.68.0/22
Scanning 1022 hosts...

Scan Results for 192.168.68.0/22
========================================
Hosts scanned: 1022
Alive: 15
Dead: 1007

Alive hosts:
  192.168.68.1
  192.168.68.45
  ...

Found 15 alive hosts
```

---

## Technical Notes

### Performance Tuning
- **Ping timeout:** 0.5s (was 1.0s) - faster failure detection
- **Workers:** 100 concurrent (was 50) - better parallelization
- **Result:** /22 scan completes in ~15 seconds

### Platform Compatibility
- macOS: Uses `-W` flag with milliseconds
- Linux: Uses `-W` flag with seconds
- Detection via `platform.system()` at `scanner.py:163-166`

### Subnet Size Limits
| Prefix | Hosts | Supported |
|--------|-------|-----------|
| /24 | 254 | Yes |
| /23 | 510 | Yes |
| /22 | 1022 | Yes |
| /21 | 2046 | No (too large) |

---

## Next Steps (Not Implemented)

1. **Output formats** - Add `--format json|csv|table` for scripting
2. **Custom subnet** - Use `--subnet 10.0.0.0/24` to override auto-discovery
3. **Port scanning** - Add `--ports 22,80,443` to check specific ports
4. **Hostname resolution** - Reverse DNS lookup for alive hosts
5. **Progress bar** - Show scan progress for large subnets
6. **ARP scanning** - Faster alternative to ICMP ping (requires root)

---

## Repository Information

- **URL:** https://github.com/ipdelete/packet-groper
- **Branch:** main
- **Commit:** `f5b4aea` - Add network scanning feature with TDD literate tests

```
f5b4aea Add network scanning feature with TDD literate tests
a678c9d Initial project setup with Python CLI and TDD test suite for network scanning
```
