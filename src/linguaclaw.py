from __future__ import annotations

import argparse

__version__ = "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="linguaclaw",
        description="A Claude-Code-style agent harness implemented mostly in natural language.",
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
    print("LinguaClaw public runtime scaffold. The thin appserver runtime and harness modules will be released incrementally.")


if __name__ == "__main__":
    main()
