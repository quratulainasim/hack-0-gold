---
name: initialize-vault
description: Initialize and verify vault structure with required folders (Inbox, Needs_Action, Done) and files (Dashboard.md, Company_Handbook.md). Use this skill when the user asks to initialize a vault, set up vault structure, verify vault integrity, or mentions working with a vault system. The skill reads Company_Handbook.md to establish Rules of Engagement that govern all subsequent file operations.
---

# Initialize Vault

This skill initializes and verifies a vault structure, ensuring required folders and files exist, and establishes operational guidelines from the Company Handbook.

## Workflow

When this skill is invoked, follow these steps:

### 1. Run the Initialization Script

Execute the vault initialization script:

```bash
python scripts/initialize_vault.py [vault_path]
```

- If `vault_path` is provided, initialize vault at that location
- If omitted, initialize vault in current working directory

The script will:
- Create missing folders: `/Inbox`, `/Needs_Action`, `/Done`
- Verify required files exist: `Dashboard.md`, `Company_Handbook.md`
- Read and display `Company_Handbook.md` content

### 2. Review the Rules of Engagement

The script outputs the complete content of `Company_Handbook.md`. This document contains the Rules of Engagement that must govern all subsequent file operations in the vault.

**Critical**: After initialization, all file operations (creating, editing, moving, organizing files) must follow the guidelines specified in the Company Handbook. These rules may include:
- File naming conventions
- Folder organization standards
- Workflow processes
- Content formatting requirements
- Any company-specific policies

### 3. Handle Missing Files

If `Dashboard.md` or `Company_Handbook.md` are missing:

**Ask the user** whether to:
- Create template files
- Provide the files themselves
- Specify a different vault location

Do not proceed with vault operations until these required files exist.

### 4. Confirm Initialization

After successful initialization, inform the user:
- Which folders were created vs. already existed
- That required files have been verified
- That Rules of Engagement have been loaded from Company_Handbook.md
- That the vault is ready for use

## Script Details

The `scripts/initialize_vault.py` script provides:

- **Folder creation**: Creates `/Inbox`, `/Needs_Action`, `/Done` if missing
- **File verification**: Checks for `Dashboard.md` and `Company_Handbook.md`
- **Handbook reading**: Loads and displays Company Handbook content
- **Status reporting**: Detailed output of what was created, verified, or missing
- **Exit codes**: Returns 0 on success, 1 on failure

## Important Notes

- The vault path can be absolute or relative
- All folder paths use forward slashes (e.g., `/Inbox` not `\Inbox`)
- Company_Handbook.md must be UTF-8 encoded
- Rules of Engagement from the handbook apply to ALL subsequent vault operations
- If initialization fails, do not proceed with vault operations until issues are resolved
