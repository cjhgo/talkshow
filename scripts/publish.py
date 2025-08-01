#!/usr/bin/env python3
"""
Script to build and publish TalkShow package to PyPI.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result


def clean_build():
    """Clean previous build artifacts."""
    print("🧹 Cleaning previous build artifacts...")
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  Removed: {path}")
            elif path.is_file():
                path.unlink()
                print(f"  Removed: {path}")


def build_package():
    """Build the package."""
    print("🔨 Building package...")
    run_command("python -m build")


def check_package():
    """Check the built package."""
    print("✅ Checking package...")
    try:
        run_command("twine check dist/*")
    except:
        print("⚠️  Package check failed, but continuing...")
        return False
    return True


def upload_to_testpypi():
    """Upload to TestPyPI."""
    print("🚀 Uploading to TestPyPI...")
    run_command("twine upload --repository testpypi dist/*")


def upload_to_pypi():
    """Upload to PyPI."""
    print("🚀 Uploading to PyPI...")
    run_command("twine upload dist/*")


def main():
    """Main function."""
    print("📦 TalkShow Package Publisher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("setup.py").exists():
        print("❌ Error: setup.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check for required tools
    try:
        import build
        import twine
    except ImportError:
        print("❌ Error: Required packages not found. Please install:")
        print("  pip install build twine")
        sys.exit(1)
    
    # Clean previous builds
    clean_build()
    
    # Build package
    build_package()
    
    # Check package (optional)
    check_package()
    
    # Ask user what to do
    print("\n" + "=" * 40)
    print("Package built successfully!")
    print("What would you like to do?")
    print("1. Upload to TestPyPI (recommended for testing)")
    print("2. Upload to PyPI (production)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        upload_to_testpypi()
        print("\n✅ Package uploaded to TestPyPI!")
        print("You can test installation with:")
        print("  pip install --index-url https://test.pypi.org/simple/ talkshow")
    elif choice == "2":
        print("\n⚠️  Warning: This will upload to the production PyPI!")
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            upload_to_pypi()
            print("\n✅ Package uploaded to PyPI!")
            print("You can install with:")
            print("  pip install talkshow")
        else:
            print("❌ Upload cancelled.")
    else:
        print("✅ Package built successfully. No upload performed.")
    
    print("\n📦 Build artifacts are in the 'dist' directory.")


if __name__ == "__main__":
    main() 