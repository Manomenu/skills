#!/usr/bin/env python3
"""Validate files against an EditorConfig using ec-windows-amd64.exe."""

import argparse
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EC_EXE = os.path.join(SCRIPT_DIR, "internal", "ec-windows-amd64.exe")


def main():
    parser = argparse.ArgumentParser(
        description="Validate files against an EditorConfig."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="File paths relative to cwd to validate",
    )
    parser.add_argument(
        "--editorconfig",
        "-c",
        required=True,
        help="Directory containing .editorconfig, relative to cwd",
    )
    args = parser.parse_args()

    cwd = os.getcwd()
    editorconfig_dir = os.path.join(cwd, args.editorconfig)
    file_paths = [os.path.join(cwd, f) for f in args.files]

    cmd = [EC_EXE] + file_paths
    result = subprocess.run(cmd, capture_output=False, cwd=editorconfig_dir)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
