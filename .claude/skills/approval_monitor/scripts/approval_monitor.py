#!/usr/bin/env python3
"""
Approval Monitor - HITL Gatekeeper
Monitors and manages items in /Pending_Approval folder for human review.
"""

import argparse
import json
import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ApprovalItem:
    """Represents an item awaiting approval"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.metadata = {}
        self.content = ""
        self._parse_file()

    def _parse_file(self):
        """Parse markdown file with frontmatter"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.startswith('---'):
                self.content = content
                return

            parts = content.split('---', 2)
            if len(parts) < 3:
                self.content = content
                return

            frontmatter = parts[1].strip()
            self.content = parts[2].strip()

            # Parse YAML-like frontmatter
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    self.metadata[key.strip()] = value.strip().strip('"\'')

        except Exception as e:
            print(f"Error parsing {self.filepath}: {e}")

    def get_title(self) -> str:
        """Get item title"""
        return self.metadata.get('title', self.filename)

    def get_type(self) -> str:
        """Get item type"""
        return self.metadata.get('type', 'unknown')

    def get_priority(self) -> str:
        """Get priority level"""
        return self.metadata.get('priority', 'medium')

    def get_status(self) -> str:
        """Get approval status"""
        return self.metadata.get('approval_status', 'pending')

    def get_cost(self) -> str:
        """Get estimated cost"""
        return self.metadata.get('estimated_cost', 'N/A')

    def get_submitted_date(self) -> str:
        """Get submission date"""
        return self.metadata.get('submitted_date', 'Unknown')

    def get_submitted_by(self) -> str:
        """Get submitter"""
        return self.metadata.get('submitted_by', 'Unknown')

    def get_summary(self, max_length: int = 100) -> str:
        """Get content summary"""
        # Extract first paragraph or objective
        lines = self.content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                return line[:max_length] + ('...' if len(line) > max_length else '')
        return "No summary available"

    def update_metadata(self, updates: Dict):
        """Update item metadata"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.startswith('---'):
                # Add frontmatter
                frontmatter = "---\n"
                for key, value in updates.items():
                    frontmatter += f"{key}: {value}\n"
                frontmatter += "---\n\n"
                content = frontmatter + content
            else:
                # Update existing frontmatter
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter_lines = parts[1].strip().split('\n')

                    # Update or add fields
                    updated_lines = []
                    updated_keys = set()

                    for line in frontmatter_lines:
                        if ':' in line:
                            key = line.split(':', 1)[0].strip()
                            if key in updates:
                                updated_lines.append(f"{key}: {updates[key]}")
                                updated_keys.add(key)
                            else:
                                updated_lines.append(line)
                        else:
                            updated_lines.append(line)

                    # Add new fields
                    for key, value in updates.items():
                        if key not in updated_keys:
                            updated_lines.append(f"{key}: {value}")

                    parts[1] = '\n' + '\n'.join(updated_lines) + '\n'
                    content = '---'.join(parts)

            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            # Reload metadata
            self._parse_file()

        except Exception as e:
            print(f"Error updating metadata: {e}")


class ApprovalMonitor:
    """Monitors and manages approval workflow"""

    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.pending_dir = os.path.join(vault_path, 'Pending_Approval')
        self.approved_dir = os.path.join(vault_path, 'Approved')
        self.rejected_dir = os.path.join(vault_path, 'Rejected')
        self.audit_log = os.path.join(vault_path, 'approval_audit.log')

        # Ensure directories exist
        for directory in [self.pending_dir, self.approved_dir, self.rejected_dir]:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def get_pending_items(self) -> List[ApprovalItem]:
        """Get all pending approval items"""
        items = []

        if not os.path.exists(self.pending_dir):
            return items

        for filename in os.listdir(self.pending_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.pending_dir, filename)
                items.append(ApprovalItem(filepath))

        return items

    def display_summary(self, items: List[ApprovalItem]):
        """Display summary of pending items"""
        print("\n" + "═" * 70)
        print(f"{'PENDING APPROVALS':^70}")
        print(f"{'(' + str(len(items)) + ')':^70}")
        print("═" * 70 + "\n")

        if not items:
            print("No items pending approval.\n")
            return

        for i, item in enumerate(items, 1):
            priority_icon = "🔴" if item.get_priority() == "high" else "🟡" if item.get_priority() == "medium" else "🟢"

            print(f"[{i}] {item.filename} - {item.get_title()}")
            print(f"    {priority_icon} Type: {item.get_type()} | Priority: {item.get_priority()} | Cost: ${item.get_cost()}")
            print(f"    Submitted: {item.get_submitted_date()} by {item.get_submitted_by()}")
            print(f"    Summary: {item.get_summary()}")
            print()

        print("═" * 70)
        print("Commands: [v]iew details | [a]pprove | [r]eject | [q]uit")
        print("═" * 70 + "\n")

    def display_details(self, item: ApprovalItem):
        """Display detailed view of an item"""
        print("\n" + "═" * 70)
        print(f"{'APPROVAL ITEM DETAILS':^70}")
        print("═" * 70 + "\n")

        print(f"File: {item.filename}")
        print(f"Title: {item.get_title()}")
        print(f"Type: {item.get_type()}")
        print(f"Priority: {item.get_priority()}")
        print(f"Status: {item.get_status()}")
        print()
        print(f"Submitted: {item.get_submitted_date()}")
        print(f"Submitted by: {item.get_submitted_by()}")
        print()

        if item.get_cost() != 'N/A':
            print(f"Estimated Cost: ${item.get_cost()}")

        if 'estimated_time' in item.metadata:
            print(f"Estimated Time: {item.metadata['estimated_time']}")

        print()
        print("Content Preview:")
        print("-" * 70)

        # Show first 500 characters of content
        preview = item.content[:500]
        if len(item.content) > 500:
            preview += "\n\n[... content truncated ...]"
        print(preview)

        print("-" * 70)
        print(f"\n[Full content available in: {item.filepath}]")

        print("\n" + "═" * 70)
        print("Actions: [a]pprove | [r]eject | [c]hanges | [b]ack")
        print("═" * 70 + "\n")

    def approve_item(self, item: ApprovalItem, approver: str = "CEO", notes: str = ""):
        """Approve an item and move to Approved folder"""
        try:
            # Update metadata
            updates = {
                'approval_status': 'approved',
                'approved_by': approver,
                'approved_date': datetime.now().isoformat(),
                'approval_notes': notes or 'Approved'
            }
            item.update_metadata(updates)

            # Move to Approved folder
            dest_path = os.path.join(self.approved_dir, item.filename)
            shutil.move(item.filepath, dest_path)

            # Log action
            self._log_action('approved', item.filename, approver, notes)

            print(f"✓ {item.filename} approved and moved to /Approved")
            return True

        except Exception as e:
            print(f"✗ Error approving item: {e}")
            return False

    def reject_item(self, item: ApprovalItem, approver: str = "CEO", reason: str = ""):
        """Reject an item and move to Rejected folder"""
        try:
            # Update metadata
            updates = {
                'approval_status': 'rejected',
                'rejected_by': approver,
                'rejected_date': datetime.now().isoformat(),
                'rejection_reason': reason or 'Rejected'
            }
            item.update_metadata(updates)

            # Move to Rejected folder
            dest_path = os.path.join(self.rejected_dir, item.filename)
            shutil.move(item.filepath, dest_path)

            # Log action
            self._log_action('rejected', item.filename, approver, reason)

            print(f"✓ {item.filename} rejected and moved to /Rejected")
            return True

        except Exception as e:
            print(f"✗ Error rejecting item: {e}")
            return False

    def request_changes(self, item: ApprovalItem, feedback: str):
        """Request changes to an item"""
        try:
            # Update metadata
            updates = {
                'approval_status': 'changes_requested',
                'changes_requested_date': datetime.now().isoformat(),
                'feedback': feedback
            }
            item.update_metadata(updates)

            # Log action
            self._log_action('changes_requested', item.filename, 'CEO', feedback)

            print(f"✓ Changes requested for {item.filename}")
            return True

        except Exception as e:
            print(f"✗ Error requesting changes: {e}")
            return False

    def _log_action(self, action: str, item: str, actor: str, notes: str):
        """Log approval action to audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'item': item,
            'actor': actor,
            'notes': notes
        }

        try:
            with open(self.audit_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Warning: Could not write to audit log: {e}")

    def generate_dashboard(self, output_file: str = None):
        """Generate approval dashboard"""
        if output_file is None:
            output_file = os.path.join(self.vault_path, 'Approval_Dashboard.md')

        pending_items = self.get_pending_items()

        # Count by priority
        high_priority = [i for i in pending_items if i.get_priority() == 'high']
        medium_priority = [i for i in pending_items if i.get_priority() == 'medium']
        low_priority = [i for i in pending_items if i.get_priority() == 'low']

        # Check for old items
        old_items = []
        for item in pending_items:
            try:
                submitted = datetime.fromisoformat(item.get_submitted_date().replace('Z', '+00:00'))
                if datetime.now() - submitted > timedelta(hours=24):
                    old_items.append(item)
            except:
                pass

        dashboard = f"""# Approval Dashboard

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Pending**: {len(pending_items)} items
- **High Priority**: {len(high_priority)} items
- **Medium Priority**: {len(medium_priority)} items
- **Low Priority**: {len(low_priority)} items

## Pending Items ({len(pending_items)})

"""

        if high_priority:
            dashboard += f"### High Priority ({len(high_priority)})\n\n"
            for item in high_priority:
                cost = f"${item.get_cost()}" if item.get_cost() != 'N/A' else 'N/A'
                time = item.metadata.get('estimated_time', 'N/A')
                dashboard += f"- **{item.get_title()}** ({cost}, {time})\n"
                dashboard += f"  - File: {item.filename}\n"
                dashboard += f"  - Type: {item.get_type()}\n"
                dashboard += f"  - Submitted: {item.get_submitted_date()}\n\n"

        if medium_priority:
            dashboard += f"### Medium Priority ({len(medium_priority)})\n\n"
            for item in medium_priority:
                cost = f"${item.get_cost()}" if item.get_cost() != 'N/A' else 'N/A'
                dashboard += f"- **{item.get_title()}** ({cost})\n"

        if low_priority:
            dashboard += f"### Low Priority ({len(low_priority)})\n\n"
            for item in low_priority:
                dashboard += f"- {item.get_title()}\n"

        # Warnings
        if high_priority or old_items:
            dashboard += "\n## Action Required\n\n"
            if high_priority:
                dashboard += f"⚠️ {len(high_priority)} high-priority items need review\n"
            if old_items:
                dashboard += f"⚠️ {len(old_items)} items pending for >24 hours\n"

        # Write dashboard
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(dashboard)

        print(f"✓ Dashboard generated: {output_file}")

    def interactive_mode(self):
        """Run interactive approval interface"""
        print("\n🔍 Approval Monitor - Interactive Mode\n")

        while True:
            items = self.get_pending_items()
            self.display_summary(items)

            if not items:
                break

            choice = input("Enter command: ").strip().lower()

            if choice == 'q':
                break
            elif choice == 'v':
                try:
                    num = int(input("Enter item number: "))
                    if 1 <= num <= len(items):
                        self.display_details(items[num - 1])

                        action = input("Action: ").strip().lower()
                        if action == 'a':
                            notes = input("Approval notes (optional): ").strip()
                            self.approve_item(items[num - 1], notes=notes)
                        elif action == 'r':
                            reason = input("Rejection reason: ").strip()
                            self.reject_item(items[num - 1], reason=reason)
                        elif action == 'c':
                            feedback = input("Feedback for changes: ").strip()
                            self.request_changes(items[num - 1], feedback)
                except ValueError:
                    print("Invalid number")
            elif choice == 'a':
                try:
                    num = int(input("Enter item number to approve: "))
                    if 1 <= num <= len(items):
                        notes = input("Approval notes (optional): ").strip()
                        self.approve_item(items[num - 1], notes=notes)
                except ValueError:
                    print("Invalid number")
            elif choice == 'r':
                try:
                    num = int(input("Enter item number to reject: "))
                    if 1 <= num <= len(items):
                        reason = input("Rejection reason: ").strip()
                        self.reject_item(items[num - 1], reason=reason)
                except ValueError:
                    print("Invalid number")


def main():
    parser = argparse.ArgumentParser(description='Monitor and manage approval workflow')
    parser.add_argument('--vault-path', '-v', required=True, help='Path to vault')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--approve', help='Approve specific item')
    parser.add_argument('--reject', help='Reject specific item')
    parser.add_argument('--note', help='Approval note')
    parser.add_argument('--reason', help='Rejection reason')
    parser.add_argument('--request-changes', help='Request changes for item')
    parser.add_argument('--feedback', help='Feedback for changes')
    parser.add_argument('--generate-dashboard', action='store_true', help='Generate dashboard')
    parser.add_argument('--filter', help='Filter items (e.g., priority=high)')
    parser.add_argument('--sort', help='Sort by field (date, cost, priority)')

    args = parser.parse_args()

    monitor = ApprovalMonitor(args.vault_path)

    # Interactive mode
    if args.interactive:
        monitor.interactive_mode()
        return

    # Generate dashboard
    if args.generate_dashboard:
        monitor.generate_dashboard()
        return

    # Approve item
    if args.approve:
        items = monitor.get_pending_items()
        item = next((i for i in items if i.filename == args.approve), None)
        if item:
            monitor.approve_item(item, notes=args.note or "")
        else:
            print(f"Item not found: {args.approve}")
        return

    # Reject item
    if args.reject:
        items = monitor.get_pending_items()
        item = next((i for i in items if i.filename == args.reject), None)
        if item:
            monitor.reject_item(item, reason=args.reason or "")
        else:
            print(f"Item not found: {args.reject}")
        return

    # Request changes
    if args.request_changes:
        items = monitor.get_pending_items()
        item = next((i for i in items if i.filename == args.request_changes), None)
        if item:
            monitor.request_changes(item, args.feedback or "")
        else:
            print(f"Item not found: {args.request_changes}")
        return

    # Default: show summary
    items = monitor.get_pending_items()

    # Apply filters
    if args.filter:
        key, value = args.filter.split('=')
        if key == 'priority':
            items = [i for i in items if i.get_priority() == value]
        elif key == 'type':
            items = [i for i in items if i.get_type() == value]

    # Apply sorting
    if args.sort:
        if args.sort == 'date':
            items.sort(key=lambda x: x.get_submitted_date())
        elif args.sort == 'cost':
            items.sort(key=lambda x: x.get_cost(), reverse=True)
        elif args.sort == 'priority':
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            items.sort(key=lambda x: priority_order.get(x.get_priority(), 3))

    monitor.display_summary(items)


if __name__ == '__main__':
    main()
