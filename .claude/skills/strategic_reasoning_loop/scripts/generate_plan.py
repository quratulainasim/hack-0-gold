#!/usr/bin/env python3
"""
Strategic Reasoning Loop - Plan Generator
Generates Plan.md files with dependency tracking for complex projects.
"""

import argparse
import json
import yaml
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, deque


class Task:
    """Represents a single task in the plan"""

    def __init__(self, task_id: str, name: str, description: str = "",
                 dependencies: List[str] = None, effort: str = "Medium",
                 status: str = "pending", acceptance_criteria: List[str] = None):
        self.id = task_id
        self.name = name
        self.description = description
        self.dependencies = dependencies or []
        self.effort = effort
        self.status = status
        self.acceptance_criteria = acceptance_criteria or []

    def to_dict(self) -> Dict:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'dependencies': self.dependencies,
            'effort': self.effort,
            'status': self.status,
            'acceptance_criteria': self.acceptance_criteria
        }


class DependencyGraph:
    """Manages task dependencies and validation"""

    def __init__(self, tasks: List[Task]):
        self.tasks = {task.id: task for task in tasks}
        self.graph = self._build_graph()

    def _build_graph(self) -> Dict[str, List[str]]:
        """Build adjacency list representation"""
        graph = defaultdict(list)
        for task in self.tasks.values():
            for dep in task.dependencies:
                graph[dep].append(task.id)
        return graph

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate dependencies for errors"""
        errors = []

        # Check for missing dependencies
        for task in self.tasks.values():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    errors.append(f"Task {task.id} depends on non-existent task {dep}")

        # Check for circular dependencies
        circular = self._detect_cycles()
        if circular:
            errors.append(f"Circular dependency detected: {' → '.join(circular)}")

        return len(errors) == 0, errors

    def _detect_cycles(self) -> Optional[List[str]]:
        """Detect circular dependencies using DFS"""
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            if node in self.graph:
                for neighbor in self.graph[node]:
                    if neighbor not in visited:
                        if dfs(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        # Found cycle
                        cycle_start = path.index(neighbor)
                        return path[cycle_start:] + [neighbor]

            path.pop()
            rec_stack.remove(node)
            return False

        for task_id in self.tasks:
            if task_id not in visited:
                result = dfs(task_id)
                if result:
                    return result

        return None

    def get_phases(self) -> List[List[str]]:
        """Calculate execution phases (topological sort levels)"""
        in_degree = {task_id: 0 for task_id in self.tasks}

        # Calculate in-degrees
        for task in self.tasks.values():
            for dep in task.dependencies:
                if dep in in_degree:
                    in_degree[task.id] += 1

        phases = []
        remaining = set(self.tasks.keys())

        while remaining:
            # Find tasks with no dependencies in remaining set
            phase = [task_id for task_id in remaining
                    if all(dep not in remaining for dep in self.tasks[task_id].dependencies)]

            if not phase:
                # Shouldn't happen if validation passed
                break

            phases.append(sorted(phase))
            remaining -= set(phase)

        return phases

    def get_critical_path(self) -> List[str]:
        """Calculate critical path (longest dependency chain)"""
        memo = {}

        def longest_path(task_id: str) -> Tuple[int, List[str]]:
            if task_id in memo:
                return memo[task_id]

            task = self.tasks[task_id]
            if not task.dependencies:
                memo[task_id] = (1, [task_id])
                return memo[task_id]

            max_length = 0
            max_path = []

            for dep in task.dependencies:
                if dep in self.tasks:
                    length, path = longest_path(dep)
                    if length > max_length:
                        max_length = length
                        max_path = path

            result = (max_length + 1, max_path + [task_id])
            memo[task_id] = result
            return result

        # Find longest path among all tasks
        max_length = 0
        critical_path = []

        for task_id in self.tasks:
            length, path = longest_path(task_id)
            if length > max_length:
                max_length = length
                critical_path = path

        return critical_path

    def get_blocked_tasks(self) -> Dict[str, List[str]]:
        """Get tasks that are blocked and their blocking dependencies"""
        blocked = {}

        for task in self.tasks.values():
            if task.status in ['pending', 'blocked']:
                blocking_deps = [dep for dep in task.dependencies
                               if dep in self.tasks and self.tasks[dep].status != 'completed']
                if blocking_deps:
                    blocked[task.id] = blocking_deps

        return blocked

    def to_mermaid(self) -> str:
        """Generate Mermaid diagram syntax"""
        lines = ["graph TD"]

        for task in self.tasks.values():
            # Node definition
            node_label = f"{task.id}[{task.name}]"
            lines.append(f"    {node_label}")

            # Edges
            for dep in task.dependencies:
                if dep in self.tasks:
                    lines.append(f"    {dep} --> {task.id}")

        return "\n".join(lines)


class PlanGenerator:
    """Generates Plan.md files with dependency tracking"""

    def __init__(self):
        self.project_name = ""
        self.objective = ""
        self.owner = ""
        self.success_criteria = []
        self.tasks = []
        self.notes = ""

    def load_from_yaml(self, filepath: str):
        """Load plan from YAML file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        project = data.get('project', {})
        self.project_name = project.get('name', 'Untitled Project')
        self.objective = project.get('objective', '')
        self.owner = project.get('owner', '')

        self.success_criteria = data.get('success_criteria', [])
        self.notes = data.get('notes', '')

        # Parse tasks
        for task_data in data.get('tasks', []):
            task = Task(
                task_id=task_data['id'],
                name=task_data['name'],
                description=task_data.get('description', ''),
                dependencies=task_data.get('dependencies', []),
                effort=task_data.get('effort', 'Medium'),
                status=task_data.get('status', 'pending'),
                acceptance_criteria=task_data.get('acceptance_criteria', [])
            )
            self.tasks.append(task)

    def load_from_markdown(self, filepath: str):
        """Parse existing Plan.md file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract project name
        match = re.search(r'# Project Plan: (.+)', content)
        if match:
            self.project_name = match.group(1).strip()

        # Extract objective
        match = re.search(r'## Objective\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if match:
            self.objective = match.group(1).strip()

        # Extract success criteria
        match = re.search(r'## Success Criteria\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if match:
            criteria_text = match.group(1).strip()
            self.success_criteria = [line.strip('- [ ] ').strip() for line in criteria_text.split('\n') if line.strip()]

        # Extract tasks
        task_pattern = r'### Task \d+: (.+?)\n\*\*ID\*\*: (\w+)\n\*\*Status\*\*: (\w+)\n\*\*Dependencies\*\*: (.+?)\n\*\*Estimated Effort\*\*: (.+?)\n\n(.+?)(?=\n\*\*Acceptance Criteria\*\*:|---|\Z)'
        for match in re.finditer(task_pattern, content, re.DOTALL):
            name, task_id, status, deps_str, effort, description = match.groups()

            # Parse dependencies
            dependencies = []
            if deps_str.strip().lower() != 'none':
                dependencies = [d.strip() for d in deps_str.split(',')]

            task = Task(
                task_id=task_id,
                name=name.strip(),
                description=description.strip(),
                dependencies=dependencies,
                effort=effort.strip(),
                status=status.strip()
            )
            self.tasks.append(task)

    def analyze_brief(self, brief: str) -> List[Task]:
        """Analyze project brief and generate tasks (simplified version)"""
        # This is a simplified implementation
        # In a real system, this would use NLP or LLM to analyze the brief

        tasks = []

        # Extract requirements
        requirements = []
        for line in brief.split('\n'):
            if line.strip().startswith('-') or line.strip().startswith('*'):
                requirements.append(line.strip().lstrip('-*').strip())

        # Generate basic tasks
        task_counter = 1

        # Always start with planning/setup
        tasks.append(Task(
            task_id=f"T{task_counter}",
            name="Project setup and planning",
            description="Initialize project structure, setup development environment, define architecture",
            dependencies=[],
            effort="Medium"
        ))
        task_counter += 1

        # Create tasks from requirements
        for req in requirements[:10]:  # Limit to 10 tasks
            tasks.append(Task(
                task_id=f"T{task_counter}",
                name=req[:50],  # Truncate long names
                description=req,
                dependencies=[f"T{task_counter-1}"] if task_counter > 1 else [],
                effort="Medium"
            ))
            task_counter += 1

        return tasks

    def validate_plan(self) -> Tuple[bool, List[str]]:
        """Validate the plan for errors"""
        graph = DependencyGraph(self.tasks)
        return graph.validate()

    def generate_markdown(self, output_file: str):
        """Generate Plan.md file"""
        graph = DependencyGraph(self.tasks)

        # Validate first
        valid, errors = graph.validate()
        if not valid:
            print("⚠️  Plan has validation errors:")
            for error in errors:
                print(f"  - {error}")
            print("\nGenerating plan anyway...\n")

        content = f"""# Project Plan: {self.project_name}

**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: In Progress
**Owner**: {self.owner or 'Not specified'}

## Objective

{self.objective}

## Success Criteria

"""

        for criterion in self.success_criteria:
            content += f"- [ ] {criterion}\n"

        content += "\n## Tasks\n\n"

        # Add tasks
        for i, task in enumerate(self.tasks, 1):
            deps_str = ', '.join(task.dependencies) if task.dependencies else 'None'

            content += f"""### Task {i}: {task.name}
**ID**: {task.id}
**Status**: {task.status}
**Dependencies**: {deps_str}
**Estimated Effort**: {task.effort}

{task.description}

"""

            if task.acceptance_criteria:
                content += "**Acceptance Criteria**:\n"
                for criterion in task.acceptance_criteria:
                    content += f"- [ ] {criterion}\n"
                content += "\n"

            content += "---\n\n"

        # Add dependency graph
        content += "## Dependency Graph\n\n```\n"

        phases = graph.get_phases()
        for i, phase in enumerate(phases, 1):
            if i < len(phases):
                content += f"{', '.join(phase)} → "
            else:
                content += ', '.join(phase)
        content += "\n```\n\n"

        # Add timeline
        content += "## Timeline\n\n"
        for i, phase in enumerate(phases, 1):
            content += f"**Phase {i}**: {', '.join(phase)}"
            if len(phase) > 1:
                content += " (can run in parallel)"
            content += "\n"

        # Add critical path
        critical_path = graph.get_critical_path()
        if critical_path:
            content += f"\n**Critical Path**: {' → '.join(critical_path)}\n"

        # Add notes
        if self.notes:
            content += f"\n## Notes\n\n{self.notes}\n"

        # Write file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✓ Plan generated: {output_file}")

        # Show summary
        print(f"\nSummary:")
        print(f"  Total tasks: {len(self.tasks)}")
        print(f"  Phases: {len(phases)}")
        print(f"  Critical path length: {len(critical_path)}")

    def export_json(self, output_file: str):
        """Export plan to JSON"""
        data = {
            'project': {
                'name': self.project_name,
                'objective': self.objective,
                'owner': self.owner,
                'created': datetime.now().isoformat()
            },
            'success_criteria': self.success_criteria,
            'tasks': [task.to_dict() for task in self.tasks],
            'notes': self.notes
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"✓ JSON exported: {output_file}")

    def update_task_status(self, task_id: str, status: str):
        """Update task status"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = status
                print(f"✓ Updated {task_id} status to: {status}")
                return

        print(f"✗ Task {task_id} not found")


def main():
    parser = argparse.ArgumentParser(description='Generate strategic plans with dependency tracking')
    parser.add_argument('--input', '-i', help='Input file (YAML or Markdown)')
    parser.add_argument('--output', '-o', default='Plan.md', help='Output file')
    parser.add_argument('--format', '-f', choices=['markdown', 'json', 'yaml'], default='markdown',
                       help='Output format')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--update', help='Update existing plan')
    parser.add_argument('--task', help='Task ID to update')
    parser.add_argument('--status', help='New status for task')
    parser.add_argument('--check-blockers', action='store_true', help='Check for blocked tasks')
    parser.add_argument('--critical-path', action='store_true', help='Show critical path')
    parser.add_argument('--visualize', action='store_true', help='Generate Mermaid diagram')

    args = parser.parse_args()

    generator = PlanGenerator()

    # Update mode
    if args.update:
        generator.load_from_markdown(args.update)

        if args.task and args.status:
            generator.update_task_status(args.task, args.status)
            generator.generate_markdown(args.update)
            return

        if args.check_blockers:
            graph = DependencyGraph(generator.tasks)
            blocked = graph.get_blocked_tasks()
            if blocked:
                print("Blocked tasks:")
                for task_id, blocking_deps in blocked.items():
                    print(f"  {task_id}: waiting on {', '.join(blocking_deps)}")
            else:
                print("No blocked tasks")
            return

        if args.critical_path:
            graph = DependencyGraph(generator.tasks)
            path = graph.get_critical_path()
            print(f"Critical path: {' → '.join(path)}")
            return

        if args.visualize:
            graph = DependencyGraph(generator.tasks)
            mermaid = graph.to_mermaid()
            print(mermaid)
            return

    # Load input
    elif args.input:
        if args.input.endswith('.yaml') or args.input.endswith('.yml'):
            generator.load_from_yaml(args.input)
        elif args.input.endswith('.md'):
            # Treat as brief
            with open(args.input, 'r', encoding='utf-8') as f:
                brief = f.read()
            generator.project_name = "Generated Project"
            generator.objective = "Extracted from brief"
            generator.tasks = generator.analyze_brief(brief)
        else:
            print("Unsupported input format")
            return

    # Interactive mode
    elif args.interactive:
        print("Interactive Plan Generator")
        print("-" * 40)
        generator.project_name = input("Project name: ")
        generator.objective = input("Objective: ")
        generator.owner = input("Owner: ")

        print("\nEnter success criteria (empty line to finish):")
        while True:
            criterion = input("  - ")
            if not criterion:
                break
            generator.success_criteria.append(criterion)

        print("\nEnter tasks (empty name to finish):")
        task_counter = 1
        while True:
            print(f"\nTask {task_counter}:")
            name = input("  Name: ")
            if not name:
                break

            description = input("  Description: ")
            deps = input("  Dependencies (comma-separated IDs, or empty): ")
            effort = input("  Effort (Low/Medium/High) [Medium]: ") or "Medium"

            dependencies = [d.strip() for d in deps.split(',')] if deps else []

            task = Task(
                task_id=f"T{task_counter}",
                name=name,
                description=description,
                dependencies=dependencies,
                effort=effort
            )
            generator.tasks.append(task)
            task_counter += 1

    else:
        parser.print_help()
        return

    # Validate
    valid, errors = generator.validate_plan()
    if not valid:
        print("\n⚠️  Validation errors:")
        for error in errors:
            print(f"  - {error}")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    # Generate output
    if args.format == 'markdown':
        generator.generate_markdown(args.output)
    elif args.format == 'json':
        generator.export_json(args.output)


if __name__ == '__main__':
    main()
