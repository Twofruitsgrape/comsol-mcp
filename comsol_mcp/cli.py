"""Command-line entry point for the COMSOL MCP server.

Usage:
    comsol-mcp                 # run the MCP server over stdio (for MCP clients)
    comsol-mcp web             # run the lightweight status dashboard
    comsol-mcp compile-bridge  # compile the Java GUI bridge with comsolcompile
"""

import argparse
import sys


def _run_server() -> None:
    from comsol_mcp.tools import mcp

    mcp.run()


def _run_web() -> None:
    from comsol_mcp.web.server import run

    run()


def _compile_bridge() -> None:
    from comsol_mcp.backends.session import compile_bridge

    try:
        out = compile_bridge()
        print(f"Bridge compiled successfully -> {out}")
    except Exception as e:  # noqa: BLE001
        print(f"Bridge compilation failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(prog="comsol-mcp", description="COMSOL MCP server")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("web", help="run the status dashboard")
    sub.add_parser("compile-bridge", help="compile the Java GUI bridge")
    args = parser.parse_args()

    if args.cmd == "web":
        _run_web()
    elif args.cmd == "compile-bridge":
        _compile_bridge()
    else:
        _run_server()


if __name__ == "__main__":
    main()
