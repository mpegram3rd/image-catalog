#!/usr/bin/env python3
"""Test runner script for image-catalog backend.

This script provides a convenient way to run different types of tests
with various options.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> int:
    """Run a command and return the exit code."""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=Path(__file__).parent)

    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
    else:
        print(f"❌ {description} - FAILED")

    return result.returncode


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for image-catalog backend")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--html-cov", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--markers", help="Run tests with specific markers")

    args = parser.parse_args()

    # Base command
    base_cmd = ["uv", "run", "pytest"]

    # Add verbosity
    if args.verbose:
        base_cmd.append("-v")

    # Determine test selection
    test_paths = []
    if args.unit:
        test_paths.append("tests/unit")
    elif args.integration:
        test_paths.append("tests/integration")
    else:
        test_paths.append("tests")

    # Add markers
    if args.markers:
        base_cmd.extend(["-m", args.markers])

    if args.fast:
        base_cmd.extend(["-m", "not slow"])

    # Coverage options
    if args.coverage or args.html_cov:
        base_cmd.extend(["--cov=.", "--cov-config=.coveragerc"])

        if args.html_cov:
            base_cmd.append("--cov-report=html")
            base_cmd.append("--cov-report=term")
        else:
            base_cmd.append("--cov-report=term-missing")

    # Add test paths
    base_cmd.extend(test_paths)

    # Run tests
    exit_code = run_command(base_cmd, "Running tests")

    # Additional commands based on options
    if args.html_cov and exit_code == 0:
        print(f"\n📊 Coverage report generated: file://{Path.cwd()}/htmlcov/index.html")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())