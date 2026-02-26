#!/usr/bin/env python3
"""
Business Handover Audit Script
Generates comprehensive weekly financial and performance review reports.
"""

import argparse
import json
import yaml
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter


class VaultItem:
    """Represents a single item in the vault"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.folder = os.path.basename(os.path.dirname(filepath))
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
            print(f"Warning: Error parsing {self.filepath}: {e}")

    def get_type(self) -> str:
        return self.metadata.get('type', 'unknown')

    def get_priority(self) -> str:
        return self.metadata.get('priority', 'medium')

    def get_status(self) -> str:
        return self.metadata.get('status', 'unknown')

    def get_amount(self) -> float:
        """Get financial amount"""
        amount_str = self.metadata.get('amount', self.metadata.get('revenue', self.metadata.get('cost', '0')))
        try:
            # Remove currency symbols and commas
            amount_str = re.sub(r'[^\d.-]', '', str(amount_str))
            return float(amount_str) if amount_str else 0.0
        except:
            return 0.0

    def get_date(self, field: str = 'completed_date') -> Optional[datetime]:
        """Get date from metadata"""
        date_str = self.metadata.get(field, self.metadata.get('date', ''))
        if not date_str:
            return None

        try:
            # Try ISO format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                # Try common formats
                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except:
                        continue
            except:
                pass

        return None

    def is_revenue(self) -> bool:
        """Check if item represents revenue"""
        return self.get_type() in ['invoice', 'sale', 'revenue', 'payment_received']

    def is_expense(self) -> bool:
        """Check if item represents expense"""
        return self.get_type() in ['expense', 'bill', 'payment', 'cost']


class BusinessAuditor:
    """Generates business audit reports"""

    def __init__(self, vault_path: str, config: Dict = None):
        self.vault_path = vault_path
        self.config = config or self._default_config()
        self.items = []
        self.metrics = {}

    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'reporting': {
                'period': 'weekly',
                'include_weekends': False
            },
            'metrics': {
                'revenue_target': 500000,
                'expense_budget': 200000,
                'task_completion_target': 0.65,
                'customer_growth_target': 0.05
            },
            'thresholds': {
                'revenue_warning': 0.90,
                'expense_warning': 0.95,
                'task_backlog_warning': 10
            }
        }

    def load_vault_items(self, folders: List[str] = None):
        """Load items from vault folders"""
        if folders is None:
            folders = ['Done', 'Needs_Action', 'Pending_Approval', 'Approved', 'In_Progress']

        for folder in folders:
            folder_path = os.path.join(self.vault_path, folder)
            if not os.path.exists(folder_path):
                continue

            for filename in os.listdir(folder_path):
                if filename.endswith('.md'):
                    filepath = os.path.join(folder_path, filename)
                    self.items.append(VaultItem(filepath))

        print(f"Loaded {len(self.items)} items from vault")

    def filter_by_date_range(self, start_date: datetime, end_date: datetime) -> List[VaultItem]:
        """Filter items by date range"""
        filtered = []
        for item in self.items:
            item_date = item.get_date('completed_date') or item.get_date('date')
            if item_date and start_date <= item_date <= end_date:
                filtered.append(item)
        return filtered

    def calculate_metrics(self, start_date: datetime, end_date: datetime):
        """Calculate all business metrics"""
        # Filter items for this period
        period_items = self.filter_by_date_range(start_date, end_date)

        # Basic counts
        self.metrics['total_items'] = len(self.items)
        self.metrics['period_items'] = len(period_items)

        # Folder counts
        self.metrics['done_count'] = len([i for i in self.items if i.folder == 'Done'])
        self.metrics['needs_action_count'] = len([i for i in self.items if i.folder == 'Needs_Action'])
        self.metrics['pending_approval_count'] = len([i for i in self.items if i.folder == 'Pending_Approval'])
        self.metrics['approved_count'] = len([i for i in self.items if i.folder == 'Approved'])
        self.metrics['in_progress_count'] = len([i for i in self.items if i.folder == 'In_Progress'])

        # Priority breakdown
        priority_counts = Counter(i.get_priority() for i in period_items)
        self.metrics['high_priority'] = priority_counts.get('high', 0)
        self.metrics['medium_priority'] = priority_counts.get('medium', 0)
        self.metrics['low_priority'] = priority_counts.get('low', 0)

        # Financial metrics
        revenue_items = [i for i in period_items if i.is_revenue()]
        expense_items = [i for i in period_items if i.is_expense()]

        self.metrics['revenue'] = sum(i.get_amount() for i in revenue_items)
        self.metrics['expenses'] = sum(i.get_amount() for i in expense_items)
        self.metrics['profit'] = self.metrics['revenue'] - self.metrics['expenses']
        self.metrics['profit_margin'] = (self.metrics['profit'] / self.metrics['revenue'] * 100) if self.metrics['revenue'] > 0 else 0

        # Task completion
        completed_tasks = len([i for i in period_items if i.folder == 'Done'])
        total_tasks = len(period_items)
        self.metrics['completion_rate'] = (completed_tasks / total_tasks) if total_tasks > 0 else 0

        # Type breakdown
        type_counts = Counter(i.get_type() for i in period_items)
        self.metrics['type_breakdown'] = dict(type_counts)

        # Calculate trends (compare with previous period)
        prev_start = start_date - (end_date - start_date)
        prev_end = start_date
        prev_items = self.filter_by_date_range(prev_start, prev_end)

        prev_revenue = sum(i.get_amount() for i in prev_items if i.is_revenue())
        prev_expenses = sum(i.get_amount() for i in prev_items if i.is_expense())

        self.metrics['revenue_change'] = self.metrics['revenue'] - prev_revenue
        self.metrics['revenue_change_pct'] = (self.metrics['revenue_change'] / prev_revenue * 100) if prev_revenue > 0 else 0
        self.metrics['expense_change'] = self.metrics['expenses'] - prev_expenses
        self.metrics['expense_change_pct'] = (self.metrics['expense_change'] / prev_expenses * 100) if prev_expenses > 0 else 0

        # Target comparison
        revenue_target = self.config['metrics']['revenue_target']
        expense_budget = self.config['metrics']['expense_budget']

        self.metrics['revenue_vs_target'] = (self.metrics['revenue'] / revenue_target) if revenue_target > 0 else 0
        self.metrics['expense_vs_budget'] = (self.metrics['expenses'] / expense_budget) if expense_budget > 0 else 0

    def get_status_indicator(self) -> str:
        """Get overall status indicator"""
        revenue_ok = self.metrics['revenue_vs_target'] >= self.config['thresholds']['revenue_warning']
        expense_ok = self.metrics['expense_vs_budget'] <= self.config['thresholds']['expense_warning']
        backlog_ok = self.metrics['needs_action_count'] <= self.config['thresholds']['task_backlog_warning']

        if revenue_ok and expense_ok and backlog_ok:
            return "🟢 Healthy"
        elif not revenue_ok or not expense_ok:
            return "🔴 Needs Attention"
        else:
            return "🟡 Caution"

    def get_completed_items(self, limit: int = 15) -> List[VaultItem]:
        """Get recently completed items"""
        done_items = [i for i in self.items if i.folder == 'Done']
        # Sort by date if available
        done_items.sort(key=lambda x: x.get_date('completed_date') or datetime.min, reverse=True)
        return done_items[:limit]

    def get_pending_items(self) -> Dict[str, List[VaultItem]]:
        """Get pending items by category"""
        return {
            'needs_action': [i for i in self.items if i.folder == 'Needs_Action'],
            'pending_approval': [i for i in self.items if i.folder == 'Pending_Approval'],
            'in_progress': [i for i in self.items if i.folder == 'In_Progress']
        }

    def identify_key_wins(self, limit: int = 5) -> List[str]:
        """Identify key wins from completed items"""
        wins = []
        completed = self.get_completed_items(20)

        # High-value revenue items
        high_revenue = [i for i in completed if i.is_revenue() and i.get_amount() > 10000]
        for item in high_revenue[:2]:
            wins.append(f"Revenue: ${item.get_amount():,.0f} from {item.filename}")

        # High-priority completions
        high_priority = [i for i in completed if i.get_priority() == 'high']
        for item in high_priority[:2]:
            title = item.metadata.get('title', item.filename)
            wins.append(f"Completed high-priority: {title}")

        # Add generic wins if not enough specific ones
        if len(wins) < limit:
            if self.metrics['revenue_change_pct'] > 5:
                wins.append(f"Revenue growth: +{self.metrics['revenue_change_pct']:.1f}%")
            if self.metrics['completion_rate'] > 0.7:
                wins.append(f"High task completion rate: {self.metrics['completion_rate']*100:.0f}%")

        return wins[:limit]

    def identify_concerns(self) -> Dict[str, List[str]]:
        """Identify concerns and risks"""
        concerns = {
            'high': [],
            'medium': [],
            'low': []
        }

        # Revenue concerns
        if self.metrics['revenue_vs_target'] < self.config['thresholds']['revenue_warning']:
            concerns['high'].append(f"Revenue at {self.metrics['revenue_vs_target']*100:.0f}% of target")

        # Expense concerns
        if self.metrics['expense_vs_budget'] > self.config['thresholds']['expense_warning']:
            concerns['high'].append(f"Expenses at {self.metrics['expense_vs_budget']*100:.0f}% of budget")

        # Backlog concerns
        if self.metrics['needs_action_count'] > self.config['thresholds']['task_backlog_warning']:
            concerns['medium'].append(f"{self.metrics['needs_action_count']} items need action")

        # Approval backlog
        if self.metrics['pending_approval_count'] > 5:
            concerns['medium'].append(f"{self.metrics['pending_approval_count']} items pending approval")

        # Completion rate
        if self.metrics['completion_rate'] < self.config['metrics']['task_completion_target']:
            concerns['low'].append(f"Task completion rate below target: {self.metrics['completion_rate']*100:.0f}%")

        return concerns

    def generate_recommendations(self) -> Dict[str, List[str]]:
        """Generate actionable recommendations"""
        recommendations = {
            'immediate': [],
            'short_term': [],
            'strategic': []
        }

        concerns = self.identify_concerns()

        # Immediate actions based on high concerns
        if concerns['high']:
            if any('revenue' in c.lower() for c in concerns['high']):
                recommendations['immediate'].append("Review revenue pipeline and accelerate sales efforts")
            if any('expense' in c.lower() for c in concerns['high']):
                recommendations['immediate'].append("Review and reduce non-essential expenses")

        # Short-term actions
        if self.metrics['needs_action_count'] > 5:
            recommendations['short_term'].append("Clear needs_action backlog - prioritize and delegate")

        if self.metrics['pending_approval_count'] > 3:
            recommendations['short_term'].append("Expedite approval process to unblock team")

        # Strategic recommendations
        if self.metrics['revenue_change_pct'] > 10:
            recommendations['strategic'].append("Maintain momentum - replicate successful strategies")

        if self.metrics['profit_margin'] > 50:
            recommendations['strategic'].append("Strong margins - consider reinvestment in growth")

        return recommendations

    def generate_markdown_report(self, start_date: datetime, end_date: datetime, output_file: str):
        """Generate comprehensive markdown report"""
        self.calculate_metrics(start_date, end_date)

        report = f"""# Weekly Business Audit Report

**Week of**: {start_date.strftime('%B %d')}-{end_date.strftime('%d, %Y')}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Reporting Period**: {(end_date - start_date).days} days

---

## Executive Summary

**Overall Status**: {self.get_status_indicator()}

"""

        # Key highlights
        wins = self.identify_key_wins(3)
        concerns = self.identify_concerns()

        if wins:
            report += "**Key Highlights**:\n"
            for win in wins:
                report += f"- ✅ {win}\n"

        if concerns['high']:
            report += "\n**Critical Concerns**:\n"
            for concern in concerns['high']:
                report += f"- ⚠️ {concern}\n"

        report += f"""

---

## Financial Performance

### Revenue
- **This Week**: ${self.metrics['revenue']:,.0f}
- **Change**: {'+' if self.metrics['revenue_change'] >= 0 else ''}{self.metrics['revenue_change_pct']:,.1f}%
- **vs Target**: {self.metrics['revenue_vs_target']*100:.1f}%

### Expenses
- **This Week**: ${self.metrics['expenses']:,.0f}
- **Change**: {'+' if self.metrics['expense_change'] >= 0 else ''}{self.metrics['expense_change_pct']:,.1f}%
- **vs Budget**: {self.metrics['expense_vs_budget']*100:.1f}%

### Profit
- **This Week**: ${self.metrics['profit']:,.0f}
- **Margin**: {self.metrics['profit_margin']:.1f}%

---

## Operational Metrics

### Task Completion
- **Completed**: {self.metrics['done_count']} tasks
- **In Progress**: {self.metrics['in_progress_count']} tasks
- **Pending**: {self.metrics['needs_action_count']} tasks
- **Completion Rate**: {self.metrics['completion_rate']*100:.0f}%

### Priority Breakdown
- **High Priority**: {self.metrics['high_priority']} items
- **Medium Priority**: {self.metrics['medium_priority']} items
- **Low Priority**: {self.metrics['low_priority']} items

---

## Completed Work ({self.metrics['done_count']} items)

"""

        # List completed items by priority
        completed = self.get_completed_items(15)
        high_pri = [i for i in completed if i.get_priority() == 'high']
        med_pri = [i for i in completed if i.get_priority() == 'medium']
        low_pri = [i for i in completed if i.get_priority() == 'low']

        if high_pri:
            report += f"### High Priority ({len(high_pri)})\n"
            for i, item in enumerate(high_pri[:5], 1):
                title = item.metadata.get('title', item.filename)
                report += f"{i}. ✅ **{title}**\n"
            report += "\n"

        if med_pri:
            report += f"### Medium Priority ({len(med_pri)})\n"
            for i, item in enumerate(med_pri[:7], 1):
                title = item.metadata.get('title', item.filename)
                report += f"{i}. ✅ {title}\n"
            report += "\n"

        if low_pri:
            report += f"### Low Priority ({len(low_pri)})\n"
            for i, item in enumerate(low_pri[:3], 1):
                title = item.metadata.get('title', item.filename)
                report += f"{i}. ✅ {title}\n"
            report += "\n"

        # Pending items
        pending = self.get_pending_items()

        report += f"""---

## Pending Items

### Needs Action ({len(pending['needs_action'])} items)
"""
        for item in pending['needs_action'][:5]:
            priority_icon = "🔴" if item.get_priority() == "high" else "🟡" if item.get_priority() == "medium" else "🟢"
            title = item.metadata.get('title', item.filename)
            report += f"{priority_icon} **{item.get_priority().title()}**: {title}\n"

        report += f"""

### Pending Approval ({len(pending['pending_approval'])} items)
"""
        for item in pending['pending_approval'][:5]:
            priority_icon = "🔴" if item.get_priority() == "high" else "🟡" if item.get_priority() == "medium" else "🟢"
            title = item.metadata.get('title', item.filename)
            report += f"{priority_icon} **{item.get_priority().title()}**: {title}\n"

        report += f"""

### In Progress ({len(pending['in_progress'])} items)
"""
        for item in pending['in_progress'][:8]:
            title = item.metadata.get('title', item.filename)
            progress = item.metadata.get('progress', 'N/A')
            report += f"- {title} ({progress})\n"

        # Key wins
        report += "\n---\n\n## Key Wins 🎉\n\n"
        for i, win in enumerate(self.identify_key_wins(5), 1):
            report += f"{i}. {win}\n"

        # Concerns
        report += "\n---\n\n## Concerns & Risks ⚠️\n\n"
        concerns = self.identify_concerns()

        if concerns['high']:
            report += "### High Priority\n"
            for concern in concerns['high']:
                report += f"- {concern}\n"
            report += "\n"

        if concerns['medium']:
            report += "### Medium Priority\n"
            for concern in concerns['medium']:
                report += f"- {concern}\n"
            report += "\n"

        if concerns['low']:
            report += "### Low Priority\n"
            for concern in concerns['low']:
                report += f"- {concern}\n"
            report += "\n"

        # Recommendations
        report += "---\n\n## Recommendations\n\n"
        recommendations = self.generate_recommendations()

        if recommendations['immediate']:
            report += "### Immediate Actions (This Week)\n"
            for i, rec in enumerate(recommendations['immediate'], 1):
                report += f"{i}. {rec}\n"
            report += "\n"

        if recommendations['short_term']:
            report += "### Short-term Actions (Next 2 Weeks)\n"
            for i, rec in enumerate(recommendations['short_term'], 1):
                report += f"{i}. {rec}\n"
            report += "\n"

        if recommendations['strategic']:
            report += "### Strategic Recommendations\n"
            for i, rec in enumerate(recommendations['strategic'], 1):
                report += f"{i}. {rec}\n"
            report += "\n"

        # Appendix
        report += f"""---

## Appendix

### Detailed Metrics
- Total vault items: {self.metrics['total_items']}
- Items in Done: {self.metrics['done_count']}
- Items in Needs_Action: {self.metrics['needs_action_count']}
- Items in Pending_Approval: {self.metrics['pending_approval_count']}
- Items in Approved: {self.metrics['approved_count']}
- Items in Progress: {self.metrics['in_progress_count']}

---

**Report prepared by**: Business Audit System
**Next review**: {(end_date + timedelta(days=7)).strftime('%B %d, %Y')}
"""

        # Write report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✓ Report generated: {output_file}")
        print(f"\nSummary:")
        print(f"  Revenue: ${self.metrics['revenue']:,.0f} ({self.metrics['revenue_change_pct']:+.1f}%)")
        print(f"  Expenses: ${self.metrics['expenses']:,.0f}")
        print(f"  Profit: ${self.metrics['profit']:,.0f} ({self.metrics['profit_margin']:.1f}% margin)")
        print(f"  Completed: {self.metrics['done_count']} tasks")
        print(f"  Status: {self.get_status_indicator()}")

    def generate_json_report(self, output_file: str):
        """Generate JSON format report"""
        report_data = {
            'generated': datetime.now().isoformat(),
            'metrics': self.metrics,
            'status': self.get_status_indicator(),
            'wins': self.identify_key_wins(5),
            'concerns': self.identify_concerns(),
            'recommendations': self.generate_recommendations()
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        print(f"✓ JSON report generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Generate business audit reports')
    parser.add_argument('--vault-path', '-v', required=True, help='Path to vault')
    parser.add_argument('--output', '-o', default='Weekly_Audit.md', help='Output file')
    parser.add_argument('--format', '-f', choices=['markdown', 'json'], default='markdown',
                       help='Output format')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    parser.add_argument('--config', '-c', help='Configuration file (YAML)')

    args = parser.parse_args()

    # Load configuration
    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

    # Create auditor
    auditor = BusinessAuditor(args.vault_path, config)

    # Load vault items
    auditor.load_vault_items()

    # Determine date range
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    else:
        end_date = datetime.now()

    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    else:
        start_date = end_date - timedelta(days=7)

    # Generate report
    if args.format == 'markdown':
        auditor.generate_markdown_report(start_date, end_date, args.output)
    elif args.format == 'json':
        auditor.calculate_metrics(start_date, end_date)
        auditor.generate_json_report(args.output)


if __name__ == '__main__':
    main()
