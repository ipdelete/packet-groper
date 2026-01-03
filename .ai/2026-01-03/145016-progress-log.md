# Progress Log

**Date:** 2026-01-03
**Session:** 145016
**Overview:** Created a literate test suite for a network scanning CLI feature using TDD (red phase)

---

## What We Built

### Literate Test Suite for Network Scanner

A markdown-based test specification and custom test runner for a CLI feature that:
1. Discovers the local network subnet
2. Validates it's a /24 network (254 hosts)
3. Performs a ping sweep to identify alive hosts
4. Reports results in human and machine-readable formats

This follows the "literate tests" pattern where markdown files ARE the tests - executable specifications that serve as both documentation and automated validation.

---

## Files Created/Modified

### Created

| File | Description |
|------|-------------|
| `tests/network_scan.md` | Literate test specification with 16 test cases |
| `run_tests.py` | Custom test runner that parses markdown and validates assertions |

### Existing (Not Modified)

| File | Description |
|------|-------------|
| `src/packet_groper/cli.py` | CLI entry point (needs `scan` subcommand) |
| `src/packet_groper/__init__.py` | Package init with version |
| `pyproject.toml` | Project config with `packet-groper` CLI entry |

---

## Key Concepts Explained

### Literate Testing Pattern

```
┌─────────────────────────────────────────────────────────────┐
│  tests/network_scan.md                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ```toml                                               │  │
│  │ module = "packet_groper.scanner"                      │  │
│  │ import = ["discover_subnet", "ping_sweep", ...]       │  │
│  │ ```                                                   │  │
│  │                                                       │  │
│  │ ## Section Header                                     │  │
│  │ Prose explaining the feature...                       │  │
│  │                                                       │  │
│  │ ### Test Name                                         │  │
│  │ ```py                                                 │  │
│  │ result = do_thing()                                   │  │
│  │ result.value  # expect: 42                            │  │
│  │ ```                                                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  run_tests.py                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. Parse TOML frontmatter                             │  │
│  │ 2. Extract code blocks + assertions                   │  │
│  │ 3. Import module under test                           │  │
│  │ 4. Execute code, validate # expect: / # error:        │  │
│  │ 5. Report pass/fail                                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Assertion Syntax

```python
# Value assertion - expression before comment is evaluated
result.value  # expect: 42

# Error assertion - expects exception with .code attribute
do_bad_thing()  # error: [error-code]

# Matchers
pi_value  # expect: approx(3.14, tol=0.01)
output    # expect: contains("substring")
```

### Shell Test Syntax

```sh
packet-groper scan --flag
# exit: 0
# stdout: contains("expected output")
# stderr: contains("[error-code]")
```

### Error Code Pattern

Exceptions must have a `.code` attribute for the runner to match:

```python
class NetworkError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)

raise NetworkError("not-slash-24", "Only /24 networks supported")
```

---

## How to Use

### Run Tests (Red Phase - All Fail)

```bash
uv run python run_tests.py
```

Current output: 0 passed, 16 failed (expected for TDD red phase)

### Test Structure

```
tests/
└── network_scan.md    # Literate test file

run_tests.py           # Custom runner (NOT pytest)
```

---

## Technical Notes

### Test Categories

| Category | Tests | Description |
|----------|-------|-------------|
| Subnet Discovery | 4 | Validate /24 detection, reject other sizes |
| Ping Sweep | 5 | Sweep hosts, collect timing, handle empty |
| CLI Integration | 5 | `packet-groper scan` command behavior |
| ScanResult Object | 2 | Serialization to dict/JSON |

### Expected API (To Be Implemented)

```python
# src/packet_groper/scanner.py

class NetworkError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        ...

def discover_subnet(ip: str, netmask: str) -> SubnetResult:
    """Returns .network (CIDR) and .prefix_length"""
    ...

def ping_sweep(network: str, mock_alive: list[str] = None) -> ScanResult:
    """Returns .alive_hosts, .total_scanned, .to_dict()"""
    ...
```

### CLI Flags Needed

```
packet-groper scan
  --mock-subnet     Override subnet detection (testing)
  --mock-alive      Comma-separated alive hosts (testing)
  --mock-no-interface   Simulate no network interface
```

---

## Next Steps (Not Implemented)

1. **Create `src/packet_groper/scanner.py`** - Implement `discover_subnet()`, `ping_sweep()`, `ScanResult`, `NetworkError`

2. **Add `scan` subcommand to CLI** - Wire up argparse with mock flags

3. **Real network detection** - Use `netifaces` or `psutil` to get actual interface info

4. **Real ping implementation** - Use `subprocess` with `ping` or raw sockets with `icmplib`

5. **Async scanning** - Ping 254 hosts concurrently for speed

6. **Output formats** - Add `--json` flag for machine-readable output

---

## Repository Information

- **Path:** `/Users/ianphil/src/tmp/packet-groper`
- **Branch:** `main`
- **Status:** Untracked files (new project, no commits yet)
