# Progress Log: packet-groper

**Date:** 2026-01-03
**Session:** 143846
**Overview:** Initialized a Python CLI project using `uv` and wrote TDD-style literate tests for a network subnet discovery and ping scan feature.

---

## What We Built

### 1. Python CLI Project Structure
Set up a modern Python CLI project using Astral's `uv` package manager with:
- src-layout package structure
- Hatchling build backend
- Console script entry point
- pytest for testing

### 2. TDD Test Suite for Network Scanner
Created a comprehensive test suite (12 tests) defining the API for a network scanning feature before implementation. Tests cover:
- **Subnet discovery** - Auto-detect local /24 network
- **Host pinging** - ICMP ping with timeout handling
- **Subnet scanning** - Scan all 254 hosts in /24
- **CLI integration** - User-facing command interface

---

## Files Created/Modified

### Created

| File | Description |
|------|-------------|
| `pyproject.toml` | Project manifest with CLI entry point and dev dependencies |
| `src/packet_groper/__init__.py` | Package init with version |
| `src/packet_groper/__main__.py` | Module runner (`python -m packet_groper`) |
| `src/packet_groper/cli.py` | CLI entry point with argparse skeleton |
| `tests/test_network_scan.py` | Literate test suite (12 tests) |
| `.python-version` | Python 3.12 pinned |
| `.gitignore` | Standard Python ignores |
| `uv.lock` | Dependency lockfile |
| `README.md` | Empty placeholder |

### Project Structure

```
packet-groper/
├── .git/
├── .gitignore
├── .python-version          # Python 3.12
├── .venv/                   # Virtual environment
├── README.md
├── pyproject.toml           # Project config + CLI entry point
├── uv.lock                  # Locked dependencies
├── src/
│   └── packet_groper/
│       ├── __init__.py      # __version__ = "0.1.0"
│       ├── __main__.py      # python -m support
│       └── cli.py           # argparse CLI (skeleton)
└── tests/
    └── test_network_scan.py # TDD tests (all failing)
```

---

## Key Concepts Explained

### TDD Red/Green/Refactor Cycle

```
┌─────────────────────────────────────────────────────┐
│  RED: Write failing tests first                     │
│       ↓                                             │
│  GREEN: Write minimal code to pass tests            │  ← We are here
│       ↓                                             │
│  REFACTOR: Clean up while keeping tests green       │
└─────────────────────────────────────────────────────┘
```

We completed the **RED** phase - all 12 tests fail with `ModuleNotFoundError` because `scanner.py` doesn't exist yet.

### Literate Testing Pattern

Tests are written as documentation-first, with docstrings explaining:
- **What** the test verifies
- **Why** the behavior matters
- **How** it fits into the user's workflow

Example from `tests/test_network_scan.py:54-77`:
```python
class TestSubnetDiscovery:
    """
    ## Subnet Discovery

    The tool must automatically detect the local network interface and its
    subnet. This is foundational - without knowing the subnet, we can't
    determine what hosts to scan.
    """
```

### API Design (Defined by Tests)

```
┌──────────────────┐     ┌─────────────┐     ┌─────────────┐
│ discover_subnet()│────▶│ SubnetInfo  │────▶│scan_subnet()│
└──────────────────┘     │ .network    │     └──────┬──────┘
                         │ .interface  │            │
                         │ .local_ip   │            ▼
                         └─────────────┘     ┌─────────────┐
                                             │ ScanReport  │
┌──────────────────┐                         │ .alive_hosts│
│   ping_host(ip)  │◀────────────────────────│ .alive_count│
│   returns bool   │   (called 254 times)    │ .duration   │
└──────────────────┘                         └─────────────┘
```

### Error Codes

| Code | When Raised |
|------|-------------|
| `no-interface` | No default network interface found |
| `not-slash-24` | Subnet mask isn't /24 (e.g., /16 or /8) |
| `scan-failed` | Ping scan couldn't complete |
| `permission-denied` | Can't send ICMP (needs sudo on some systems) |

---

## How to Use

### Run the CLI (current skeleton)
```bash
uv run packet-groper           # Prints "Hello from packet-groper!"
uv run packet-groper --version # Shows version 0.1.0
```

### Run the Tests
```bash
uv run pytest                     # Run all tests
uv run pytest -v                  # Verbose output
uv run pytest tests/test_network_scan.py::TestSubnetDiscovery  # Single class
```

### Add Dependencies
```bash
uv add netifaces    # Will be needed for subnet discovery
uv add --dev ruff   # Optional: linting
```

---

## Technical Notes

### Current Test Status
All 12 tests fail with `ModuleNotFoundError: No module named 'packet_groper.scanner'`

This is expected - TDD red phase complete.

### Dependencies Required for Implementation
```toml
# Will need to add:
dependencies = [
    "netifaces",  # Cross-platform network interface detection
]
```

### Platform Considerations
- `ping` command syntax differs between macOS (`-t` timeout) and Linux (`-W` timeout)
- Tests mock `subprocess.run` to avoid platform-specific behavior
- ICMP ping may require root/sudo on some systems

### Security Considerations
- Network scanning should only be performed on networks you own/administer
- The tool is limited to /24 to prevent accidental large-scale scans
- No raw sockets used - relies on system `ping` command

---

## Next Steps (Not Implemented)

### To Go Green
1. Create `src/packet_groper/scanner.py` with:
   - `SubnetInfo` dataclass
   - `ScanReport` dataclass
   - `NetworkError` exception with `.code` property
   - `discover_subnet()` function using netifaces
   - `ping_host(ip)` function using subprocess
   - `scan_subnet(info)` function

2. Update `src/packet_groper/cli.py`:
   - Add `--scan` flag to argparse
   - Import and call scanner functions
   - Format and print `ScanReport`

3. Add `netifaces` dependency:
   ```bash
   uv add netifaces
   ```

### Future Enhancements
- Parallel ping for faster scanning (threading/asyncio)
- JSON output format (`--json` flag)
- Custom subnet specification (`--subnet 192.168.1.0/24`)
- Support for /25, /26 smaller subnets
- MAC address resolution via ARP
- Hostname resolution via reverse DNS
- Progress bar during scan

---

## Repository Information

- **Location:** `/Users/ianphil/src/tmp/packet-groper`
- **Git:** Initialized by `uv init`
- **Branch:** `main` (default)
- **No commits yet** - initial files are staged

To create initial commit:
```bash
git add -A
git commit -m "Initial project setup with TDD test suite for network scanner"
```
