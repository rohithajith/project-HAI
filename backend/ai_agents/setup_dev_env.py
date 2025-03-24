#!/usr/bin/env python
"""
Setup script for the Hotel AI development environment.

This script installs all the required dependencies for the Hotel AI system,
including the RAG module, agents, and tests.
"""

import os
import sys
import subprocess
import argparse

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Setup the Hotel AI development environment")
    parser.add_argument("--venv", action="store_true", help="Create a virtual environment")
    parser.add_argument("--venv-path", default="venv", help="Path to the virtual environment")
    parser.add_argument("--upgrade", action="store_true", help="Upgrade existing packages")
    return parser.parse_args()

def create_venv(venv_path):
    """Create a virtual environment."""
    print(f"Creating virtual environment at {venv_path}...")
    subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
    
    # Determine the pip path
    if os.name == "nt":  # Windows
        pip_path = os.path.join(venv_path, "Scripts", "pip")
    else:  # Unix/Linux/Mac
        pip_path = os.path.join(venv_path, "bin", "pip")
    
    # Upgrade pip
    print("Upgrading pip...")
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
    
    return pip_path

def install_dependencies(pip_path, upgrade=False):
    """Install the required dependencies."""
    # Install the package in development mode
    print("Installing the package in development mode...")
    cmd = [pip_path, "install", "-e", "."]
    if upgrade:
        cmd.append("--upgrade")
    subprocess.run(cmd, check=True)
    
    # Install test dependencies
    print("Installing test dependencies...")
    cmd = [pip_path, "install", "-e", ".[dev]"]
    if upgrade:
        cmd.append("--upgrade")
    subprocess.run(cmd, check=True)
    
    # Install RAG module dependencies
    print("Installing RAG module dependencies...")
    cmd = [pip_path, "install", "-r", "rag/requirements.txt"]
    if upgrade:
        cmd.append("--upgrade")
    subprocess.run(cmd, check=True)

def main():
    """Main function."""
    args = parse_args()
    
    # Change to the backend/ai_agents directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Create a virtual environment if requested
    if args.venv:
        pip_path = create_venv(args.venv_path)
    else:
        # Use the current Python interpreter's pip
        pip_path = "pip"
    
    # Install dependencies
    install_dependencies(pip_path, args.upgrade)
    
    print("\nSetup complete! You can now run the tests with:")
    if args.venv:
        if os.name == "nt":  # Windows
            print(f"{args.venv_path}\\Scripts\\python run_tests.py")
        else:  # Unix/Linux/Mac
            print(f"{args.venv_path}/bin/python run_tests.py")
    else:
        print("python run_tests.py")

if __name__ == "__main__":
    main()