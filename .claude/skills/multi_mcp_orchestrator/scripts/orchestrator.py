#!/usr/bin/env python3
"""
Multi-MCP Orchestrator
Orchestrates complex workflows across multiple MCP servers.
"""

import argparse
import json
import yaml
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict
import copy


class WorkflowStep:
    """Represents a single step in a workflow"""

    def __init__(self, step_id: str, config: Dict):
        self.id = step_id
        self.name = config.get('name', step_id)
        self.mcp_server = config.get('mcp_server', 'default')
        self.action = config.get('action')
        self.params = config.get('params', {})
        self.depends_on = config.get('depends_on', [])
        self.condition = config.get('condition')
        self.on_error = config.get('on_error', 'fail')  # retry, continue, fail, rollback
        self.retry_count = config.get('retry_count', 0)
        self.retry_delay = config.get('retry_delay', 1)
        self.optional = config.get('optional', False)
        self.timeout = config.get('timeout', 300)
        self.rollback = config.get('rollback')
        self.for_each = config.get('for_each')

        self.status = 'pending'  # pending, running, success, failed, skipped
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None
        self.attempts = 0

    def to_dict(self) -> Dict:
        """Convert step to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'result': self.result,
            'error': str(self.error) if self.error else None,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'attempts': self.attempts
        }


class WorkflowOrchestrator:
    """Orchestrates workflow execution"""

    def __init__(self, workflow_config: Dict, dry_run: bool = False):
        self.config = workflow_config
        self.dry_run = dry_run
        self.name = workflow_config.get('name', 'Unnamed Workflow')
        self.description = workflow_config.get('description', '')
        self.variables = workflow_config.get('variables', {})
        self.steps = self._parse_steps(workflow_config.get('steps', []))
        self.execution_log = []
        self.workflow_id = f"wf_{int(time.time())}"
        self.started_at = None
        self.completed_at = None

    def _parse_steps(self, steps_config: List[Dict]) -> Dict[str, WorkflowStep]:
        """Parse step configurations"""
        steps = {}
        for step_config in steps_config:
            step_id = step_config['id']
            steps[step_id] = WorkflowStep(step_id, step_config)
        return steps

    def _substitute_variables(self, text: str, context: Dict) -> str:
        """Substitute variables in text using {{variable}} syntax"""
        if not isinstance(text, str):
            return text

        # Replace {{variable}} patterns
        pattern = r'\{\{([^}]+)\}\}'

        def replace_var(match):
            var_path = match.group(1).strip()

            # Handle filters (e.g., {{name | slugify}})
            if '|' in var_path:
                var_path, filter_name = var_path.split('|', 1)
                var_path = var_path.strip()
                filter_name = filter_name.strip()

                value = self._get_nested_value(context, var_path)
                return self._apply_filter(value, filter_name)

            return str(self._get_nested_value(context, var_path))

        return re.sub(pattern, replace_var, text)

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, '')
            else:
                return ''

        return value

    def _apply_filter(self, value: Any, filter_name: str) -> str:
        """Apply filter to value"""
        if filter_name == 'slugify':
            return re.sub(r'[^a-z0-9]+', '-', str(value).lower()).strip('-')
        elif filter_name == 'upper':
            return str(value).upper()
        elif filter_name == 'lower':
            return str(value).lower()
        elif filter_name == 'title':
            return str(value).title()
        else:
            return str(value)

    def _substitute_params(self, params: Dict, context: Dict) -> Dict:
        """Recursively substitute variables in parameters"""
        if isinstance(params, dict):
            return {k: self._substitute_params(v, context) for k, v in params.items()}
        elif isinstance(params, list):
            return [self._substitute_params(item, context) for item in params]
        elif isinstance(params, str):
            return self._substitute_variables(params, context)
        else:
            return params

    def _evaluate_condition(self, condition: str, context: Dict) -> bool:
        """Evaluate condition expression"""
        if not condition:
            return True

        # Substitute variables
        condition = self._substitute_variables(condition, context)

        # Simple evaluation (in production, use safer evaluation)
        try:
            # Basic comparison operators
            if '==' in condition:
                left, right = condition.split('==')
                return left.strip().strip("'\"") == right.strip().strip("'\"")
            elif '!=' in condition:
                left, right = condition.split('!=')
                return left.strip().strip("'\"") != right.strip().strip("'\"")
            elif '>' in condition:
                left, right = condition.split('>')
                return float(left.strip()) > float(right.strip())
            elif '<' in condition:
                left, right = condition.split('<')
                return float(left.strip()) < float(right.strip())
            else:
                # Treat as boolean
                return condition.lower() in ['true', '1', 'yes']
        except:
            return False

    def _get_execution_order(self) -> List[List[str]]:
        """Calculate execution order respecting dependencies (topological sort)"""
        # Build dependency graph
        in_degree = {step_id: 0 for step_id in self.steps}
        graph = defaultdict(list)

        for step_id, step in self.steps.items():
            for dep in step.depends_on:
                if dep in self.steps:
                    graph[dep].append(step_id)
                    in_degree[step_id] += 1

        # Topological sort by levels (for parallel execution)
        levels = []
        remaining = set(self.steps.keys())

        while remaining:
            # Find steps with no dependencies in remaining set
            level = [step_id for step_id in remaining
                    if all(dep not in remaining for dep in self.steps[step_id].depends_on)]

            if not level:
                # Circular dependency detected
                raise ValueError(f"Circular dependency detected in workflow")

            levels.append(level)
            remaining -= set(level)

        return levels

    def _execute_step(self, step: WorkflowStep, context: Dict) -> bool:
        """Execute a single step"""
        step.status = 'running'
        step.started_at = datetime.now().isoformat()
        step.attempts += 1

        print(f"  ⏳ Executing: {step.name} (ID: {step.id})")

        # Check condition
        if step.condition and not self._evaluate_condition(step.condition, context):
            step.status = 'skipped'
            step.completed_at = datetime.now().isoformat()
            print(f"  ⏭️  Skipped: {step.name} (condition not met)")
            return True

        # Substitute parameters
        params = self._substitute_params(step.params, context)

        if self.dry_run:
            print(f"  [DRY RUN] Would execute: {step.action}")
            print(f"  [DRY RUN] MCP Server: {step.mcp_server}")
            print(f"  [DRY RUN] Params: {json.dumps(params, indent=2)}")
            step.status = 'success'
            step.result = {'dry_run': True}
            step.completed_at = datetime.now().isoformat()
            return True

        try:
            # Simulate MCP call (in production, use actual MCP client)
            result = self._call_mcp_server(step.mcp_server, step.action, params)

            step.status = 'success'
            step.result = result
            step.completed_at = datetime.now().isoformat()

            duration = (datetime.fromisoformat(step.completed_at) -
                       datetime.fromisoformat(step.started_at)).total_seconds()

            print(f"  ✓ Completed: {step.name} ({duration:.1f}s)")
            return True

        except Exception as e:
            step.error = str(e)
            print(f"  ✗ Failed: {step.name} - {e}")

            # Handle error based on strategy
            if step.on_error == 'retry' and step.attempts < step.retry_count:
                print(f"  🔄 Retrying in {step.retry_delay}s... (attempt {step.attempts + 1}/{step.retry_count})")
                time.sleep(step.retry_delay)
                return self._execute_step(step, context)

            elif step.on_error == 'continue' or step.optional:
                print(f"  ⚠️  Continuing despite error (optional step)")
                step.status = 'failed'
                step.completed_at = datetime.now().isoformat()
                return True

            else:
                step.status = 'failed'
                step.completed_at = datetime.now().isoformat()
                return False

    def _call_mcp_server(self, server: str, action: str, params: Dict) -> Dict:
        """Call MCP server (simulated - replace with actual MCP client)"""
        # This is a simulation. In production, use actual MCP client
        print(f"    → MCP Call: {server}.{action}")

        # Simulate different actions
        if action == 'send_email':
            return {'message_id': f"msg_{int(time.time())}", 'status': 'sent'}
        elif action == 'create_channel':
            return {'channel_id': f"ch_{int(time.time())}", 'name': params.get('name')}
        elif action == 'send_message':
            return {'message_id': f"msg_{int(time.time())}", 'timestamp': datetime.now().isoformat()}
        elif action == 'create_post':
            return {'post_id': f"post_{int(time.time())}", 'url': 'https://linkedin.com/post/123'}
        else:
            return {'success': True}

    def execute(self) -> Dict:
        """Execute the workflow"""
        print(f"\n{'='*70}")
        print(f"Executing Workflow: {self.name}")
        if self.description:
            print(f"Description: {self.description}")
        if self.dry_run:
            print("Mode: DRY RUN (no actual changes will be made)")
        print(f"{'='*70}\n")

        self.started_at = datetime.now().isoformat()

        # Build execution context
        context = {
            'variables': self.variables,
            'steps': {},
            'workflow': {
                'id': self.workflow_id,
                'name': self.name
            }
        }

        try:
            # Get execution order
            execution_levels = self._get_execution_order()

            total_steps = len(self.steps)
            completed_steps = 0

            # Execute steps level by level
            for level_num, level in enumerate(execution_levels, 1):
                print(f"\n--- Phase {level_num}/{len(execution_levels)} ---")

                if len(level) > 1:
                    print(f"Executing {len(level)} steps in parallel:")

                # Execute all steps in this level
                for step_id in level:
                    step = self.steps[step_id]

                    success = self._execute_step(step, context)

                    # Update context with step result
                    context['steps'][step_id] = {
                        'result': step.result,
                        'status': step.status
                    }

                    if step.status in ['success', 'skipped']:
                        completed_steps += 1

                    # Log step execution
                    self.execution_log.append(step.to_dict())

                    if not success and not step.optional:
                        raise Exception(f"Step {step_id} failed: {step.error}")

            self.completed_at = datetime.now().isoformat()

            # Summary
            print(f"\n{'='*70}")
            print(f"✓ Workflow Completed Successfully")
            print(f"{'='*70}")

            duration = (datetime.fromisoformat(self.completed_at) -
                       datetime.fromisoformat(self.started_at)).total_seconds()

            print(f"\nSummary:")
            print(f"  Total steps: {total_steps}")
            print(f"  Completed: {completed_steps}")
            print(f"  Duration: {duration:.1f}s")

            return {
                'workflow_id': self.workflow_id,
                'name': self.name,
                'status': 'completed',
                'started_at': self.started_at,
                'completed_at': self.completed_at,
                'duration_seconds': duration,
                'steps_executed': total_steps,
                'steps_completed': completed_steps,
                'execution_log': self.execution_log
            }

        except Exception as e:
            self.completed_at = datetime.now().isoformat()

            print(f"\n{'='*70}")
            print(f"✗ Workflow Failed: {e}")
            print(f"{'='*70}")

            return {
                'workflow_id': self.workflow_id,
                'name': self.name,
                'status': 'failed',
                'error': str(e),
                'started_at': self.started_at,
                'completed_at': self.completed_at,
                'execution_log': self.execution_log
            }

    def save_checkpoint(self, filepath: str):
        """Save workflow state to checkpoint file"""
        checkpoint = {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'started_at': self.started_at,
            'variables': self.variables,
            'steps': {step_id: step.to_dict() for step_id, step in self.steps.items()},
            'execution_log': self.execution_log
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2)

        print(f"Checkpoint saved: {filepath}")


def load_workflow(filepath: str) -> Dict:
    """Load workflow from YAML or JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        if filepath.endswith('.yaml') or filepath.endswith('.yml'):
            return yaml.safe_load(f)
        else:
            return json.load(f)


def main():
    parser = argparse.ArgumentParser(description='Multi-MCP Workflow Orchestrator')
    parser.add_argument('--workflow', '-w', help='Workflow file (YAML or JSON)')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Dry run mode')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--checkpoint', '-c', help='Save checkpoint to file')
    parser.add_argument('--resume', '-r', help='Resume from checkpoint')
    parser.add_argument('--output', '-o', help='Output results to file')

    args = parser.parse_args()

    if args.interactive:
        print("Interactive workflow builder not yet implemented")
        return

    if not args.workflow:
        parser.print_help()
        return

    # Load workflow
    workflow_config = load_workflow(args.workflow)

    # Create orchestrator
    orchestrator = WorkflowOrchestrator(workflow_config, dry_run=args.dry_run)

    # Execute workflow
    result = orchestrator.execute()

    # Save checkpoint if requested
    if args.checkpoint:
        orchestrator.save_checkpoint(args.checkpoint)

    # Save output if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to: {args.output}")


if __name__ == '__main__':
    main()
