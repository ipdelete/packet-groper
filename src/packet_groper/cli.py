"""Command-line interface for packet-groper."""

import argparse
import sys

from packet_groper import __version__
from packet_groper.scanner import discover_subnet, scan_network, NetworkError


def cmd_scan(args: argparse.Namespace) -> int:
    """Execute the scan subcommand."""
    print("Scanning local network...")

    try:
        # Discover local subnet
        subnet = discover_subnet()
        print(f"Discovered subnet: {subnet}")

        if subnet.prefixlen < 22:
            print(f"Warning: Subnet /{subnet.prefixlen} is larger than /22, skipping scan")
            return 1

        # Scan the network
        num_hosts = subnet.num_addresses - 2
        print(f"Scanning {num_hosts} hosts...")
        result = scan_network(subnet)

        # Print report
        print()
        print(result.report())
        print()
        print(f"Found {len(result.alive)} alive hosts")
        return 0

    except NetworkError as e:
        print(f"Error [{e.code}]: {e}", file=sys.stderr)
        return 1


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="packet-groper",
        description="Packet Groper CLI tool",
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    # scan subcommand
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan local network subnet for alive hosts",
    )
    scan_parser.add_argument(
        "--subnet",
        help="Subnet to scan (default: auto-discover)",
        default=None,
    )

    args = parser.parse_args()

    if args.command == "scan":
        sys.exit(cmd_scan(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
