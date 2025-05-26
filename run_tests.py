#!/usr/bin/env python3
"""
Test runner script for the local RAG system.
Provides different test execution modes for development and CI.
"""
import sys
import subprocess
import argparse
import os


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ FAILED: {description}")
        return False
    else:
        print(f"✅ PASSED: {description}")
        return True


def install_dependencies():
    """Install test dependencies."""
    commands = [
        ("pip install -r requirements.txt", "Installing main dependencies"),
        ("pip install -r test_requirements.txt", "Installing test dependencies")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True


def run_unit_tests():
    """Run unit tests."""
    commands = [
        ("pytest tests/test_file_finder.py -v", "FileSystemRAG unit tests"),
        ("pytest tests/test_app.py -v", "Flask app unit tests")
    ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
    
    return success


def run_integration_tests():
    """Run integration tests."""
    return run_command("pytest tests/test_integration.py -v", "Integration tests")


def run_all_tests():
    """Run all tests with coverage."""
    return run_command(
        "pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html",
        "All tests with coverage"
    )


def run_quick_tests():
    """Run quick tests (unit tests only)."""
    return run_command(
        "pytest tests/test_file_finder.py tests/test_app.py -v --tb=short",
        "Quick unit tests"
    )


def run_lint():
    """Run code linting."""
    commands = [
        ("flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Critical lint errors"),
        ("flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics", "All lint warnings")
    ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
    
    return success


def run_security_scan():
    """Run security scans."""
    commands = [
        ("pip install safety bandit", "Installing security tools"),
        ("safety check", "Dependency vulnerability scan"),
        ("bandit -r . -f json -o bandit-report.json", "Security code scan")
    ]
    
    success = True
    for command, description in commands:
        # Don't fail on bandit warnings
        if "bandit" in command:
            run_command(command, description)
        else:
            if not run_command(command, description):
                success = False
    
    return success


def main():
    parser = argparse.ArgumentParser(description="Test runner for local RAG system")
    parser.add_argument(
        "mode",
        choices=["install", "unit", "integration", "all", "quick", "lint", "security", "ci"],
        help="Test mode to run"
    )
    parser.add_argument(
        "--no-install",
        action="store_true",
        help="Skip dependency installation"
    )
    
    args = parser.parse_args()
    
    print("🧪 Local RAG System Test Runner")
    print(f"Mode: {args.mode}")
    
    # Install dependencies unless skipped
    if not args.no_install and args.mode != "install":
        print("\n📦 Installing dependencies...")
        if not install_dependencies():
            print("❌ Failed to install dependencies")
            sys.exit(1)
    
    success = True
    
    if args.mode == "install":
        success = install_dependencies()
    
    elif args.mode == "unit":
        success = run_unit_tests()
    
    elif args.mode == "integration":
        success = run_integration_tests()
    
    elif args.mode == "all":
        success = run_all_tests()
    
    elif args.mode == "quick":
        success = run_quick_tests()
    
    elif args.mode == "lint":
        success = run_lint()
    
    elif args.mode == "security":
        success = run_security_scan()
    
    elif args.mode == "ci":
        # Full CI pipeline
        steps = [
            ("Linting", run_lint),
            ("Unit tests", run_unit_tests),
            ("Integration tests", run_integration_tests),
            ("Security scan", run_security_scan)
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔄 Running {step_name}...")
            if not step_func():
                print(f"❌ {step_name} failed")
                success = False
            else:
                print(f"✅ {step_name} passed")
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 