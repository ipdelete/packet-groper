# packet-groper

A CLI tool that discovers your local network subnet and pings all hosts to report which are alive.

## Installation

```bash
uv sync
```

## Usage

```bash
# Scan local network (auto-discovers subnet)
uv run packet-groper scan

# Show help
uv run packet-groper --help
uv run packet-groper scan --help
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
  192.168.68.127

Found 15 alive hosts
```

## Features

- Auto-detects local network subnet
- Supports /22, /23, /24 and smaller subnets (up to 1022 hosts)
- Concurrent ping sweep with 100 workers
- Clean report of alive/dead hosts

## Testing

Uses literate tests (markdown-based executable specifications):

```bash
uv run python tests/run_tests.py
```

## License

MIT
