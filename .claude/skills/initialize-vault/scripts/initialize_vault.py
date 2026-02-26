#!/usr/bin/env python3
"""
Vault Initialization Script

This script initializes a vault structure by:
1. Creating required folders (/Inbox, /Needs_Action, /Done)
2. Verifying required files (Dashboard.md, Company_Handbook.md)
3. Reading Company_Handbook.md to establish Rules of Engagement

Usage:
    python initialize_vault.py [vault_path]

    If vault_path is not provided, uses current working directory.
"""

import sys
import os
from pathlib import Path


def initialize_vault(vault_path=None):
    """
    Initialize vault structure and verify required files.

    Args:
        vault_path: Path to vault directory (defaults to current directory)

    Returns:
        dict with status and handbook_content
    """
    # Use current directory if no path provided
    if vault_path is None:
        vault_path = Path.cwd()
    else:
        vault_path = Path(vault_path).resolve()

    print(f"Initializing vault at: {vault_path}")
    print()

    # Required folders
    required_folders = ["Inbox", "Needs_Action", "Done"]

    # Required files
    required_files = ["Dashboard.md", "Company_Handbook.md"]

    results = {
        "success": True,
        "folders_created": [],
        "folders_existed": [],
        "files_verified": [],
        "files_missing": [],
        "handbook_content": None,
        "errors": []
    }

    # Step 1: Check and create required folders
    print("Step 1: Checking required folders...")
    for folder_name in required_folders:
        folder_path = vault_path / folder_name
        if folder_path.exists():
            print(f"  [OK] {folder_name}/ already exists")
            results["folders_existed"].append(folder_name)
        else:
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"  [CREATED] {folder_name}/")
                results["folders_created"].append(folder_name)
            except Exception as e:
                error_msg = f"Failed to create {folder_name}/: {e}"
                print(f"  [ERROR] {error_msg}")
                results["errors"].append(error_msg)
                results["success"] = False

    print()

    # Step 2: Verify required files
    print("Step 2: Verifying required files...")
    for file_name in required_files:
        file_path = vault_path / file_name
        if file_path.exists() and file_path.is_file():
            print(f"  [OK] {file_name} exists")
            results["files_verified"].append(file_name)
        else:
            print(f"  [MISSING] {file_name} not found")
            results["files_missing"].append(file_name)
            results["success"] = False

    print()

    # Step 3: Read Company_Handbook.md for Rules of Engagement
    print("Step 3: Reading Company_Handbook.md for Rules of Engagement...")
    handbook_path = vault_path / "Company_Handbook.md"

    if handbook_path.exists():
        try:
            with open(handbook_path, 'r', encoding='utf-8') as f:
                handbook_content = f.read()
            results["handbook_content"] = handbook_content
            print(f"  [OK] Successfully read Company_Handbook.md ({len(handbook_content)} characters)")
            print()
            print("=" * 60)
            print("RULES OF ENGAGEMENT (from Company_Handbook.md)")
            print("=" * 60)
            print(handbook_content)
            print("=" * 60)
        except Exception as e:
            error_msg = f"Failed to read Company_Handbook.md: {e}"
            print(f"  [ERROR] {error_msg}")
            results["errors"].append(error_msg)
            results["success"] = False
    else:
        error_msg = "Company_Handbook.md not found - cannot establish Rules of Engagement"
        print(f"  [ERROR] {error_msg}")
        results["errors"].append(error_msg)
        results["success"] = False

    print()

    # Summary
    print("=" * 60)
    print("INITIALIZATION SUMMARY")
    print("=" * 60)

    if results["folders_created"]:
        print(f"Folders created: {', '.join(results['folders_created'])}")

    if results["folders_existed"]:
        print(f"Folders already existed: {', '.join(results['folders_existed'])}")

    if results["files_verified"]:
        print(f"Files verified: {', '.join(results['files_verified'])}")

    if results["files_missing"]:
        print(f"Files MISSING: {', '.join(results['files_missing'])}")

    if results["errors"]:
        print()
        print("ERRORS:")
        for error in results["errors"]:
            print(f"  - {error}")

    print()

    if results["success"]:
        print("[SUCCESS] Vault initialization complete!")
    else:
        print("[FAILED] Vault initialization incomplete - see errors above")

    return results


def main():
    """Main entry point for the script."""
    vault_path = sys.argv[1] if len(sys.argv) > 1 else None

    results = initialize_vault(vault_path)

    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main()
