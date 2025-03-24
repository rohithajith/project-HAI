#!/usr/bin/env python
"""
Test runner for the Hotel AI system.

This script runs the tests for the Hotel AI system using pytest.
"""

import os
import sys
import argparse
import subprocess

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run tests for the Hotel AI system")
    parser.add_argument("--module", help="Module to test (e.g., rag, agents)")
    parser.add_argument("--test", help="Specific test file to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    return parser.parse_args()

def run_tests(module=None, test=None, verbose=False, coverage=False):
    """Run the tests."""
    # Determine the command to run
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity flag if requested
    if verbose:
        cmd.append("-v")
    
    # Add coverage flags if requested
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term", "--cov-report=html"])
    
    # Add the module or test to run
    if test:
        cmd.append(test)
    elif module:
        if module == "rag":
            cmd.append("tests/rag/")
        elif module == "agents":
            cmd.append("tests/agents/")
        elif module == "controllers":
            cmd.append("tests/controllers/")
        else:
            print(f"Unknown module: {module}")
            return 1
    else:
        cmd.append("tests/")
    
    # Print the command
    print(f"Running: {' '.join(cmd)}")
    
    # Run the tests
    result = subprocess.run(cmd)
    return result.returncode

def main():
    """Main function."""
    args = parse_args()
    
    # Change to the backend/ai_agents directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run the tests
    return run_tests(
        module=args.module,
        test=args.test,
        verbose=args.verbose,
        coverage=args.coverage
    )

if __name__ == "__main__":
    sys.exit(main())