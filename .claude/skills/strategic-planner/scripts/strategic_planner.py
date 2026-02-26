#!/usr/bin/env python3
"""
Strategic Planner Script

Creates comprehensive strategic plans for items in /Needs_Action folder,
then moves them to /Pending_Approval for human review.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def parse_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    """
    Parse YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter_dict, body_content)
    """
    frontmatter = {}
    body = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1].strip()
            body = parts[2].strip()

            # Parse YAML-like frontmatter
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

    return frontmatter, body


def update_frontmatter(content: str, updates: Dict[str, str]) -> str:
    """
    Update frontmatter fields in markdown content.

    Args:
        content: Original markdown content
        updates: Dictionary of fields to update

    Returns:
        Updated markdown content
    """
    frontmatter, body = parse_frontmatter(content)
    frontmatter.update(updates)

    # Rebuild frontmatter
    fm_lines = ['---']
    for key, value in frontmatter.items():
        fm_lines.append(f'{key}: {value}')
    fm_lines.append('---')

    return '\n'.join(fm_lines) + '\n\n' + body


def sanitize_filename(text: str) -> str:
    """
    Sanitize text for use in filename.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized filename-safe string
    """
    # Remove or replace invalid filename characters
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    # Trim hyphens from ends
    text = text.strip('-')
    # Limit length
    return text[:50].lower()


def identify_required_tools(frontmatter: Dict[str, str], body: str) -> Dict[str, List[str]]:
    """
    Identify required MCP tools based on item source and content.

    Args:
        frontmatter: Parsed frontmatter dictionary
        body: Item body content

    Returns:
        Dictionary with 'primary' and 'optional' tool lists
    """
    primary_tools = []
    optional_tools = []

    source = frontmatter.get('source', '').lower()
    item_type = frontmatter.get('type', '').lower()

    # Identify tools based on source
    if source == 'gmail' or 'email' in item_type:
        primary_tools.append('Gmail MCP - For sending email responses')

    if source == 'linkedin' or 'linkedin' in item_type:
        primary_tools.append('LinkedIn MCP - For posting content or responding to engagement')

    # Check content for tool hints
    body_lower = body.lower()

    if 'email' in body_lower and 'Gmail MCP' not in str(primary_tools):
        optional_tools.append('Gmail MCP - If email communication is needed')

    if 'linkedin' in body_lower and 'LinkedIn MCP' not in str(primary_tools):
        optional_tools.append('LinkedIn MCP - If LinkedIn engagement is needed')

    if 'document' in body_lower or 'file' in body_lower:
        optional_tools.append('File System Tools - For document creation or management')

    if 'research' in body_lower or 'search' in body_lower:
        optional_tools.append('Web Search Tools - For background research')

    # Default if no tools identified
    if not primary_tools:
        primary_tools.append('To be determined based on approved approach')

    return {
        'primary': primary_tools,
        'optional': optional_tools
    }


def extract_item_title(frontmatter: Dict[str, str], body: str) -> str:
    """
    Extract a meaningful title from the item.

    Args:
        frontmatter: Parsed frontmatter
        body: Item body content

    Returns:
        Item title string
    """
    # Try to get title from subject or first heading
    if 'subject' in frontmatter:
        return frontmatter['subject']

    # Look for first markdown heading
    lines = body.split('\n')
    for line in lines:
        if line.startswith('#'):
            return line.lstrip('#').strip()

    # Fallback to type and source
    item_type = frontmatter.get('type', 'Item')
    source = frontmatter.get('source', '')

    if source:
        return f"{source.title()} {item_type.title()}"

    return item_type.title()


def generate_draft_content(frontmatter: Dict[str, str], body: str) -> str:
    """
    Generate appropriate draft content based on item type.

    Args:
        frontmatter: Parsed frontmatter
        body: Item body content

    Returns:
        Draft content string
    """
    source = frontmatter.get('source', '').lower()
    item_type = frontmatter.get('type', '').lower()

    # Email response draft
    if source == 'gmail' or 'email' in item_type:
        from_name = frontmatter.get('from_name', 'there')
        subject = frontmatter.get('subject', 'Your inquiry')

        draft = f"""**Email Response Draft**

Subject: Re: {subject}

Dear {from_name},

Thank you for reaching out. I appreciate you taking the time to [acknowledge their message/inquiry/request].

[Main response content - address their key points and questions]

[Provide value, information, or next steps]

[Call to action or invitation for further discussion]

Best regards,
[Your Name]

---

**Notes:**
- Personalize the greeting and content based on relationship
- Address all points raised in their email
- Maintain professional yet warm tone
- Include clear next steps or call to action
"""
        return draft

    # LinkedIn post draft
    elif source == 'linkedin' and 'comment' in item_type:
        author = frontmatter.get('author', 'the commenter')

        draft = f"""**LinkedIn Comment Response Draft**

Thanks for sharing your thoughts, {author}!

[Acknowledge their comment and add value to the conversation]

[Share additional insights or perspective]

[Ask a question or invite further engagement]

---

**Notes:**
- Keep it conversational and authentic
- Add value to the discussion
- Encourage continued engagement
- Tag the person if appropriate
"""
        return draft

    elif source == 'linkedin' and 'lead' in item_type:
        author = frontmatter.get('author', 'the lead')

        draft = f"""**LinkedIn Lead Engagement Draft**

Hi {author},

[Personalized opening based on their profile/activity]

[Acknowledge the connection or engagement]

[Provide value or insight relevant to their interests]

[Soft call to action - continue conversation, schedule call, share resource]

Looking forward to connecting!

---

**Notes:**
- Research their profile before sending
- Personalize based on their background and interests
- Focus on providing value, not selling
- Keep it brief and professional
"""
        return draft

    # Generic draft
    else:
        draft = f"""**Draft Content**

[Opening - Set context and acknowledge the situation]

[Main Content - Address the core objective]

[Closing - Clear next steps or call to action]

---

**Notes:**
- Customize tone and style for the audience
- Ensure all key points are addressed
- Include specific details and personalization
- Proofread before execution
"""
        return draft


def define_success_criteria(frontmatter: Dict[str, str], body: str) -> Dict[str, List[str]]:
    """
    Define success criteria for the plan.

    Args:
        frontmatter: Parsed frontmatter
        body: Item body content

    Returns:
        Dictionary with 'immediate' and 'long_term' criteria lists
    """
    source = frontmatter.get('source', '').lower()
    item_type = frontmatter.get('type', '').lower()
    priority = frontmatter.get('priority', 'normal').lower()

    immediate = []
    long_term = []

    # Email-specific criteria
    if source == 'gmail' or 'email' in item_type:
        immediate.append('Email sent successfully without errors')
        immediate.append('All points from original email are addressed')
        immediate.append('Professional tone and formatting maintained')

        long_term.append('Recipient responds positively or takes requested action')
        long_term.append('Relationship is maintained or strengthened')

    # LinkedIn-specific criteria
    elif source == 'linkedin':
        if 'comment' in item_type:
            immediate.append('Comment posted successfully')
            immediate.append('Response adds value to the conversation')
            immediate.append('Tone is appropriate and engaging')

            long_term.append('Engagement continues (replies, likes, shares)')
            long_term.append('Professional relationship is strengthened')

        elif 'lead' in item_type:
            immediate.append('Message sent successfully')
            immediate.append('Personalization is evident and relevant')
            immediate.append('Value proposition is clear')

            long_term.append('Lead responds and shows interest')
            long_term.append('Conversation progresses toward opportunity')

    # Generic criteria
    if not immediate:
        immediate.append('Action is completed successfully')
        immediate.append('Quality standards are met')
        immediate.append('Timing is appropriate')

    if not long_term:
        long_term.append('Desired outcome is achieved')
        long_term.append('No negative consequences occur')

    # Add priority-specific criteria
    if priority == 'high':
        immediate.append('Executed within 24 hours of approval')

    return {
        'immediate': immediate,
        'long_term': long_term
    }


def assess_risks(frontmatter: Dict[str, str], body: str) -> List[Dict[str, str]]:
    """
    Assess potential risks and mitigation strategies.

    Args:
        frontmatter: Parsed frontmatter
        body: Item body content

    Returns:
        List of risk dictionaries with 'risk' and 'mitigation' keys
    """
    risks = []
    priority = frontmatter.get('priority', 'normal').lower()
    source = frontmatter.get('source', '').lower()

    # High-priority items have timing risk
    if priority == 'high':
        risks.append({
            'risk': 'Delayed response may reduce effectiveness',
            'mitigation': 'Execute within 24 hours of approval; flag if urgent'
        })

    # Email-specific risks
    if source == 'gmail':
        risks.append({
            'risk': 'Email may be misinterpreted or tone may be unclear',
            'mitigation': 'Review draft carefully; consider having colleague review'
        })

        risks.append({
            'risk': 'Recipient may not respond or may respond negatively',
            'mitigation': 'Set clear expectations; prepare follow-up strategy'
        })

    # LinkedIn-specific risks
    if source == 'linkedin':
        risks.append({
            'risk': 'Public engagement may be visible to wider audience',
            'mitigation': 'Ensure content is professional and brand-appropriate'
        })

        risks.append({
            'risk': 'Response may not generate desired engagement',
            'mitigation': 'Focus on providing value; avoid overly promotional content'
        })

    # Generic risks
    if not risks:
        risks.append({
            'risk': 'Execution may not achieve desired outcome',
            'mitigation': 'Set clear success criteria; monitor results; adjust approach if needed'
        })

    return risks


def generate_plan(item_path: Path, vault_path: Path) -> Optional[str]:
    """
    Generate comprehensive strategic plan for an item.

    Args:
        item_path: Path to item file
        vault_path: Path to vault directory

    Returns:
        Plan content as string, or None if generation fails
    """
    try:
        # Read item
        with open(item_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse frontmatter and body
        frontmatter, body = parse_frontmatter(content)

        # Extract key information
        title = extract_item_title(frontmatter, body)
        priority = frontmatter.get('priority', 'normal')
        source = frontmatter.get('source', 'unknown')
        item_type = frontmatter.get('type', 'unknown')

        # Generate plan components
        tools = identify_required_tools(frontmatter, body)
        draft = generate_draft_content(frontmatter, body)
        success = define_success_criteria(frontmatter, body)
        risks = assess_risks(frontmatter, body)

        # Build plan
        plan = f"""# Strategic Plan: {title}

**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: Pending Approval
**Priority**: {priority.title()}
**Source**: {source.title()}
**Type**: {item_type.title()}

---

## 1. Objective

### Primary Goal
{title}

### Context
This item originated from {source.title()} and requires strategic planning to ensure an effective response. The priority level is {priority}, indicating {'immediate attention is required' if priority == 'high' else 'standard processing timeline'}.

### Expected Outcome
Successfully address the request/opportunity while maintaining professional standards and achieving the desired business outcome.

---

## 2. Required MCP Tools

### Primary Tools
"""

        for tool in tools['primary']:
            plan += f"- **{tool}**\n"

        if tools['optional']:
            plan += "\n### Optional Tools\n"
            for tool in tools['optional']:
                plan += f"- **{tool}**\n"

        plan += """
### Tool Configuration
Ensure all required MCP tools are properly configured and accessible before execution. Verify authentication and permissions are current.

---

## 3. Proposed Draft

### Approach
The recommended approach is to respond professionally and promptly, addressing all key points while maintaining appropriate tone and style for the platform and audience.

### Content/Response

"""
        plan += draft

        plan += """

### Tone & Style
- **Tone**: Professional yet personable
- **Style**: Clear, concise, and action-oriented
- **Key Messages**: Address core needs, provide value, maintain relationship

---

## 4. Success Criteria

### Immediate Success
"""

        for criterion in success['immediate']:
            plan += f"- [ ] {criterion}\n"

        plan += "\n### Long-term Success\n"
        for criterion in success['long_term']:
            plan += f"- [ ] {criterion}\n"

        plan += """
### Metrics to Track
- Response time from approval to execution
- Recipient engagement or response
- Quality of outcome vs. expectations

---

## Risk Assessment

### Potential Risks
"""

        for risk in risks:
            plan += f"- **{risk['risk']}**: {risk['mitigation']}\n"

        plan += """
### Contingency Plans
If the initial approach doesn't achieve desired results:
1. Review feedback and adjust strategy
2. Consider alternative communication channels
3. Escalate to human decision-maker if needed
4. Document lessons learned for future improvements

---

## Execution Notes

### Timing
"""
        if priority == 'high':
            plan += "Execute within 24 hours of approval (high priority)\n"
        else:
            plan += "Execute within 48-72 hours of approval (standard timeline)\n"

        plan += """
### Dependencies
- Human approval of this plan
- MCP tools must be configured and accessible
- Any referenced attachments or resources must be available

### Follow-up Actions
- Monitor for response or engagement
- Track success metrics
- Update Dashboard with execution results
- Move completed item to /Done folder

---

## Approval Checklist

Before approving, verify:
- [ ] Objective is clear and achievable
- [ ] Required MCP tools are available and configured
- [ ] Draft content is appropriate, accurate, and professional
- [ ] Success criteria are measurable and realistic
- [ ] Risks have been identified and mitigation strategies are sound
- [ ] Timing is appropriate for the situation
- [ ] All information from original item has been considered

---

## Original Item Reference

**File**: {item_path.name}
**Location**: /Needs_Action/{item_path.name}

See the original item file in this folder for complete context and details.

---

*Plan generated by strategic-planner skill on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return plan

    except Exception as e:
        print(f"  [ERROR] Error generating plan for {item_path.name}: {e}")
        return None


def process_item(item_path: Path, vault_path: Path) -> bool:
    """
    Process a single item from Needs_Action.

    Args:
        item_path: Path to item file
        vault_path: Path to vault directory

    Returns:
        True if processed successfully, False otherwise
    """
    try:
        # Read item
        with open(item_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse frontmatter
        frontmatter, body = parse_frontmatter(content)

        # Check if already processed
        status = frontmatter.get('status', 'pending')
        if status == 'pending_approval':
            print(f"  [SKIP]  Skipping (already pending approval): {item_path.name}")
            return False

        # Generate plan
        print(f"  [PLAN] Planning: {item_path.name}")
        plan_content = generate_plan(item_path, vault_path)

        if not plan_content:
            print(f"  [ERROR] Failed to generate plan for {item_path.name}")
            return False

        # Create folder in Pending_Approval
        date_str = datetime.now().strftime('%Y-%m-%d')
        item_title = extract_item_title(frontmatter, body)
        folder_name = f"{date_str}_{sanitize_filename(item_title)}"

        pending_folder = vault_path / 'Pending_Approval' / folder_name
        pending_folder.mkdir(parents=True, exist_ok=True)

        # Save Plan.md
        plan_path = pending_folder / 'Plan.md'
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)

        # Move original item to pending folder
        new_item_path = pending_folder / item_path.name

        # Update item status
        updated_content = update_frontmatter(content, {
            'status': 'pending_approval',
            'planned_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'plan_file': 'Plan.md',
            'moved_to': f'/Pending_Approval/{folder_name}'
        })

        # Write updated item to new location
        with open(new_item_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        # Remove from Needs_Action
        item_path.unlink()

        # Report success
        print(f"  [OK] Plan created: {folder_name}/Plan.md")
        print(f"     Moved to: /Pending_Approval/{folder_name}")

        return True

    except Exception as e:
        print(f"  [ERROR] Error processing {item_path.name}: {e}")
        return False


def plan_needs_action_items(vault_path: Path) -> Dict[str, int]:
    """
    Process all items in Needs_Action folder.

    Args:
        vault_path: Path to vault directory

    Returns:
        Dictionary with processing statistics
    """
    needs_action_path = vault_path / 'Needs_Action'

    if not needs_action_path.exists():
        print(f"[ERROR] Needs_Action folder not found: {needs_action_path}")
        return {'processed': 0, 'skipped': 0, 'errors': 0}

    # Ensure Pending_Approval folder exists
    pending_approval_path = vault_path / 'Pending_Approval'
    pending_approval_path.mkdir(exist_ok=True)

    # Find all markdown files
    md_files = list(needs_action_path.glob('*.md'))

    if not md_files:
        print(f"[EMPTY] No items found in Needs_Action")
        return {'processed': 0, 'skipped': 0, 'errors': 0}

    print(f"\n[PLAN] Strategic Planner - Processing {len(md_files)} items from Needs_Action\n")

    stats = {'processed': 0, 'skipped': 0, 'errors': 0}

    for item_path in md_files:
        result = process_item(item_path, vault_path)
        if result:
            stats['processed'] += 1
        else:
            stats['skipped'] += 1

    # Print summary
    print(f"\n{'='*60}")
    print(f"Strategic Planning Summary")
    print(f"{'='*60}")
    print(f"[OK] Plans Created: {stats['processed']}")
    print(f"[SKIP]  Skipped: {stats['skipped']}")
    print(f"[ERROR] Errors: {stats['errors']}")
    print(f"{'='*60}\n")

    if stats['processed'] > 0:
        print(f"[PLAN] {stats['processed']} items moved to /Pending_Approval for human review\n")

    return stats


def main():
    """Main entry point for strategic planner script."""
    # Get vault path from command line or use current directory
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        vault_path = Path.cwd()

    # Validate vault path
    if not vault_path.exists():
        print(f"[ERROR] Error: Vault path does not exist: {vault_path}")
        sys.exit(1)

    print(f"[INFO] Strategic Planner - Vault: {vault_path.absolute()}")

    # Process items
    stats = plan_needs_action_items(vault_path)

    # Exit with appropriate code
    if stats['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
