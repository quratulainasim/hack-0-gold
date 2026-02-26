#!/usr/bin/env python3
"""
Strategic Planner Script
Creates comprehensive strategic plans for items in Needs_Action.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

def parse_frontmatter(content: str) -> tuple[Dict[str, str], str]:
    """Parse frontmatter from markdown content."""
    frontmatter = {}
    body = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()

            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

    return frontmatter, body

def update_frontmatter(content: str, updates: Dict[str, str]) -> str:
    """Update frontmatter in markdown content."""
    if not content.startswith('---'):
        fm_lines = ['---']
        for key, value in updates.items():
            fm_lines.append(f'{key}: {value}')
        fm_lines.append('---')
        return '\n'.join(fm_lines) + '\n\n' + content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return content

    fm_text = parts[1].strip()
    body = parts[2]

    fm_dict = {}
    for line in fm_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            fm_dict[key.strip()] = value.strip()

    fm_dict.update(updates)

    fm_lines = ['---']
    for key, value in fm_dict.items():
        fm_lines.append(f'{key}: {value}')
    fm_lines.append('---')

    return '\n'.join(fm_lines) + body

def identify_required_tools(frontmatter: Dict[str, str], body: str) -> list[str]:
    """Identify required MCP tools based on item content."""
    tools = []

    source = frontmatter.get('source', '').lower()
    item_type = frontmatter.get('type', '').lower()

    if 'gmail' in source or 'email' in item_type:
        tools.append('Gmail MCP')

    if 'linkedin' in source or 'linkedin' in item_type:
        tools.append('LinkedIn MCP')

    if 'whatsapp' in source or 'whatsapp' in item_type:
        tools.append('WhatsApp Response (Manual)')

    if 'facebook' in source or 'facebook' in item_type:
        tools.append('Facebook MCP')

    if 'x' in source or 'twitter' in source:
        tools.append('X (Twitter) MCP')

    if not tools:
        tools.append('Manual Response')

    return tools

def generate_plan(filepath: Path, vault_path: Path) -> Optional[Path]:
    """Generate strategic plan for an item."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, body = parse_frontmatter(content)

        # Extract metadata
        item_type = frontmatter.get('type', 'unknown')
        priority = frontmatter.get('priority', 'medium')
        source = frontmatter.get('source', 'unknown')
        sender = frontmatter.get('sender', 'Unknown')
        keywords = frontmatter.get('keywords', '')

        # Identify required tools
        tools = identify_required_tools(frontmatter, body)

        # Extract title from body
        title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
        title = title_match.group(1) if title_match else filepath.stem

        # Create folder name
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        folder_name = f"{timestamp}_{filepath.stem}"
        folder_path = vault_path / 'Pending_Approval' / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        # Generate Plan.md
        plan_content = f"""---
status: pending_approval
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
priority: {priority}
original_file: {filepath.name}
---

# Strategic Plan: {title}

**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: Pending Approval
**Priority**: {priority.upper()}
**Source**: {source}

---

## 1. Objective

### Context
This is a {priority} priority {item_type} from {source}.

**From**: {sender}
**Keywords**: {keywords}

### Expected Outcome
Provide appropriate response to address the urgent request.

---

## 2. Required MCP Tools

### Primary Tools
{chr(10).join(f'- **{tool}**: Required for execution' for tool in tools)}

### Tool Configuration
Ensure MCP tools are properly configured and authenticated.

---

## 3. Proposed Draft

### Approach
Respond promptly to the urgent request with appropriate action.

### Response Strategy

**Immediate Actions:**
1. Acknowledge receipt of the message
2. Assess urgency and priority
3. Determine appropriate response channel
4. Craft professional response

### Tone & Style
- **Tone**: Professional and responsive
- **Style**: Clear and direct
- **Key Messages**: Acknowledgment, understanding, next steps

---

## 4. Success Criteria

### Immediate Success
- [ ] Response sent within appropriate timeframe
- [ ] Sender acknowledges receipt
- [ ] Urgent matter is addressed

### Long-term Success
- [ ] Relationship maintained or strengthened
- [ ] Issue fully resolved
- [ ] Follow-up completed if needed

### Metrics to Track
- Response time: Target < 2 hours for urgent items
- Resolution time: Target < 24 hours
- Sender satisfaction: Positive acknowledgment

---

## Risk Assessment

### Potential Risks
- **Delayed Response**: Set up alerts and monitoring
- **Miscommunication**: Clarify requirements before responding
- **Tool Failure**: Have backup communication channels ready

### Contingency Plans
If primary tool fails, use alternative communication method.

---

## Execution Notes

### Timing
Execute immediately upon approval for high-priority items.

### Dependencies
- MCP tool availability
- Authentication credentials
- Network connectivity

### Follow-up Actions
- Monitor for response
- Track resolution status
- Update dashboard metrics

---

## Approval Checklist

Before approving, verify:
- [ ] Objective is clear and achievable
- [ ] Required tools are available
- [ ] Response strategy is appropriate
- [ ] Success criteria are measurable
- [ ] Risks have been considered
- [ ] Timing is appropriate

---

*Plan generated by strategic-planner skill on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        plan_path = folder_path / 'Plan.md'
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)

        # Move original file to folder
        new_filepath = folder_path / filepath.name

        # Update original file status
        updates = {
            'status': 'pending_approval',
            'planned_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'plan_file': 'Plan.md',
            'moved_to': f'/Pending_Approval/{folder_name}'
        }

        updated_content = update_frontmatter(content, updates)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        # Move file
        filepath.rename(new_filepath)

        print(f"  [OK] Created plan for: {filepath.name}")
        print(f"       Folder: {folder_name}")
        print(f"       Tools: {', '.join(tools)}")
        print(f"       Priority: {priority}")

        return folder_path

    except Exception as e:
        print(f"  [ERROR] Failed to create plan for {filepath.name}: {e}")
        return None

def main():
    """Main entry point."""
    vault_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    print("="*60)
    print("Strategic Planner")
    print("="*60)
    print(f"Vault: {vault_path.absolute()}")
    print()

    needs_action_path = vault_path / 'Needs_Action'

    if not needs_action_path.exists():
        print("[ERROR] Needs_Action folder not found")
        return 1

    files = list(needs_action_path.glob('*.md'))

    if not files:
        print("[INFO] No items in Needs_Action")
        return 0

    print(f"Processing {len(files)} item(s)...")
    print()

    created_plans = []
    for filepath in files:
        plan_path = generate_plan(filepath, vault_path)
        if plan_path:
            created_plans.append(plan_path)

    print()
    print("="*60)
    print(f"Planning Complete - {len(created_plans)} plan(s) created")
    print("="*60)
    print()
    print("Plans moved to /Pending_Approval for review")

    return 0

if __name__ == '__main__':
    sys.exit(main())
