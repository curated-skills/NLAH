from __future__ import annotations

import argparse

from nlah import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nlah",
        description="Natural-Language Agent Harnesses public runtime scaffold.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main() -> None:
    parser = build_parser()
    parser.parse_args()
    print("NLAH public runtime scaffold. Runtime modules and harness components will be released incrementally.")


if __name__ == "__main__":
    main()
