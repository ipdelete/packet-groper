"""Command-line interface for packet-groper."""

import argparse

from packet_groper import __version__


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

    args = parser.parse_args()

    print("Hello from packet-groper!")


if __name__ == "__main__":
    main()
