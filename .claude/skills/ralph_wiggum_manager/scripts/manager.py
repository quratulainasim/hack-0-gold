#!/usr/bin/env python3
"""
Ralph Wiggum Manager - Autonomous Loop Orchestrator

Manages the complete workflow from Inbox to Done, coordinating all skills
in a continuous loop. Named after Ralph Wiggum for its simple, reliable,
continuous operation - "I'm helping!"
"""

import argparse
import json
import logging
import os
import sys
import time
import yaml
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field


class WorkflowState(Enum):
    """Workflow state machine states"""
    IDLE = "idle"
    TRIAGING = "triaging"
    PLANNING = "planning"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    AUDITING = "auditing"
    ERROR = "error"


class SkillStatus(Enum):
    """Skill execution status"""
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass
class SkillConfig:
    """Configuration for a skill"""
    name: str
    enabled: bool = True
    trigger: str = ""
    timeout: int = 300
    max_retries: int = 3
    retry_delay: int = 60


@dataclass
class WorkflowMetrics:
    """Workflow execution metrics"""
    cycles_completed: int = 0
    items_processed: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_cycle_time: float = 0.0
    error_count: int = 0
    last_cycle_time: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)


@dataclass
class FolderStatus:
    """Status of a vault folder"""
    name: str
    path: Path
    item_count: int = 0
    last_updated: Optional[datetime] = None


class RalphWiggumManager:
    """
    Autonomous loop orchestrator that manages the complete workflow.

    Coordinates skills from Inbox through Done in a continuous loop.
    """

    def __init__(self, vault_path: str, config_path: Optional[str] = None):
        """
        Initialize the manager.

        Args:
            vault_path: Path to the vault directory
            config_path: Optional path to configuration file
        """
        self.vault_path = Path(vault_path)
        self.config = self._load_config(config_path)
        self.state = WorkflowState.IDLE
        self.metrics = WorkflowMetrics()
        self.skills: Dict[str, SkillConfig] = {}
        self.skill_status: Dict[str, SkillStatus] = {}
        self.folders: Dict[str, FolderStatus] = {}
        self.running = False
        self.paused = False

        # Setup logging
        self._setup_logging()

        # Initialize components
        self._initialize_skills()
        self._initialize_folders()

        self.logger.info("Ralph Wiggum Manager initialized")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)

        # Default configuration
        return {
            'loop': {
                'enabled': True,
                'interval': 60,
                'max_cycles': 0,
                'max_duration': 0
            },
            'vault': {
                'folders': ['Inbox', 'Needs_Action', 'Pending_Approval', 'Approved', 'Rejected', 'Done']
            },
            'skills': {
                'triage_inbox': {
                    'enabled': True,
                    'trigger': 'inbox_not_empty',
                    'timeout': 300
                },
                'strategic_planner': {
                    'enabled': True,
                    'trigger': 'needs_action_not_empty',
                    'timeout': 600
                },
                'approval_monitor': {
                    'enabled': True,
                    'trigger': 'pending_approval_not_empty',
                    'mode': 'notify'
                },
                'executor': {
                    'enabled': True,
                    'trigger': 'approved_not_empty',
                    'timeout': 900
                },
                'metric_auditor': {
                    'enabled': True,
                    'trigger': 'done_updated',
                    'schedule': 'daily'
                }
            },
            'monitoring': {
                'enabled': True,
                'health_check_interval': 300,
                'metrics_interval': 60
            },
            'error_handling': {
                'retry_enabled': True,
                'max_retries': 3,
                'retry_delay': 60,
                'backoff_multiplier': 2
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/manager.log'
            }
        }

    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'logs/manager.log')

        # Create logs directory
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger('ralph_wiggum_manager')

    def _initialize_skills(self):
        """Initialize skill configurations"""
        skills_config = self.config.get('skills', {})

        for skill_name, skill_config in skills_config.items():
            self.skills[skill_name] = SkillConfig(
                name=skill_name,
                enabled=skill_config.get('enabled', True),
                trigger=skill_config.get('trigger', ''),
                timeout=skill_config.get('timeout', 300),
                max_retries=skill_config.get('max_retries', 3),
                retry_delay=skill_config.get('retry_delay', 60)
            )
            self.skill_status[skill_name] = SkillStatus.READY if skill_config.get('enabled', True) else SkillStatus.DISABLED

        self.logger.info(f"Initialized {len(self.skills)} skills")

    def _initialize_folders(self):
        """Initialize vault folder tracking"""
        folder_names = self.config.get('vault', {}).get('folders', [])

        for folder_name in folder_names:
            folder_path = self.vault_path / folder_name
            folder_path.mkdir(parents=True, exist_ok=True)

            self.folders[folder_name] = FolderStatus(
                name=folder_name,
                path=folder_path
            )

        self._update_folder_status()
        self.logger.info(f"Initialized {len(self.folders)} vault folders")

    def _update_folder_status(self):
        """Update status of all vault folders"""
        for folder_name, folder_status in self.folders.items():
            if folder_status.path.exists():
                # Count markdown files
                items = list(folder_status.path.glob('*.md'))
                folder_status.item_count = len(items)

                # Get last modified time
                if items:
                    latest = max(items, key=lambda p: p.stat().st_mtime)
                    folder_status.last_updated = datetime.fromtimestamp(latest.stat().st_mtime)

    def _check_trigger(self, trigger: str) -> bool:
        """
        Check if a trigger condition is met.

        Args:
            trigger: Trigger condition to check

        Returns:
            True if trigger condition is met
        """
        if trigger == 'inbox_not_empty':
            return self.folders.get('Inbox', FolderStatus('Inbox', Path())).item_count > 0

        elif trigger == 'needs_action_not_empty':
            return self.folders.get('Needs_Action', FolderStatus('Needs_Action', Path())).item_count > 0

        elif trigger == 'pending_approval_not_empty':
            return self.folders.get('Pending_Approval', FolderStatus('Pending_Approval', Path())).item_count > 0

        elif trigger == 'approved_not_empty':
            return self.folders.get('Approved', FolderStatus('Approved', Path())).item_count > 0

        elif trigger == 'done_updated':
            done_folder = self.folders.get('Done')
            if done_folder and done_folder.last_updated:
                # Check if updated in last hour
                return datetime.now() - done_folder.last_updated < timedelta(hours=1)
            return False

        return False

    def _execute_skill(self, skill_name: str) -> bool:
        """
        Execute a skill.

        Args:
            skill_name: Name of the skill to execute

        Returns:
            True if skill executed successfully
        """
        skill = self.skills.get(skill_name)
        if not skill or not skill.enabled:
            self.logger.warning(f"Skill {skill_name} not available or disabled")
            return False

        self.logger.info(f"Executing skill: {skill_name}")
        self.skill_status[skill_name] = SkillStatus.RUNNING

        try:
            # In a real implementation, this would invoke the actual skill
            # For now, we simulate skill execution
            self.logger.info(f"Skill {skill_name} would be executed here")

            # Simulate processing time
            time.sleep(1)

            self.skill_status[skill_name] = SkillStatus.READY
            self.metrics.successful_operations += 1
            return True

        except Exception as e:
            self.logger.error(f"Skill {skill_name} failed: {e}")
            self.skill_status[skill_name] = SkillStatus.FAILED
            self.metrics.failed_operations += 1
            self.metrics.error_count += 1
            return False

    def _process_inbox(self) -> bool:
        """Process items in Inbox folder"""
        self.state = WorkflowState.TRIAGING
        self.logger.info("Processing Inbox")

        if self._check_trigger('inbox_not_empty'):
            return self._execute_skill('triage_inbox')

        return True

    def _process_needs_action(self) -> bool:
        """Process items in Needs_Action folder"""
        self.state = WorkflowState.PLANNING
        self.logger.info("Processing Needs_Action")

        if self._check_trigger('needs_action_not_empty'):
            return self._execute_skill('strategic_planner')

        return True

    def _process_pending_approval(self) -> bool:
        """Process items in Pending_Approval folder"""
        self.state = WorkflowState.AWAITING_APPROVAL
        self.logger.info("Processing Pending_Approval")

        if self._check_trigger('pending_approval_not_empty'):
            return self._execute_skill('approval_monitor')

        return True

    def _process_approved(self) -> bool:
        """Process items in Approved folder"""
        self.state = WorkflowState.EXECUTING
        self.logger.info("Processing Approved")

        if self._check_trigger('approved_not_empty'):
            return self._execute_skill('executor')

        return True

    def _process_done(self) -> bool:
        """Process items in Done folder"""
        self.state = WorkflowState.AUDITING
        self.logger.info("Processing Done")

        if self._check_trigger('done_updated'):
            return self._execute_skill('metric_auditor')

        return True

    def _run_cycle(self) -> bool:
        """
        Run one complete workflow cycle.

        Returns:
            True if cycle completed successfully
        """
        cycle_start = time.time()
        self.logger.info(f"Starting cycle {self.metrics.cycles_completed + 1}")

        try:
            # Update folder status
            self._update_folder_status()

            # Process each stage
            stages = [
                self._process_inbox,
                self._process_needs_action,
                self._process_pending_approval,
                self._process_approved,
                self._process_done
            ]

            for stage in stages:
                if not self.running or self.paused:
                    return False

                if not stage():
                    self.logger.warning(f"Stage {stage.__name__} failed")
                    # Continue to next stage even if one fails

            # Update metrics
            cycle_time = time.time() - cycle_start
            self.metrics.cycles_completed += 1
            self.metrics.last_cycle_time = cycle_time
            self.metrics.total_cycle_time += cycle_time

            self.state = WorkflowState.IDLE
            self.logger.info(f"Cycle {self.metrics.cycles_completed} completed in {cycle_time:.2f}s")

            return True

        except Exception as e:
            self.logger.error(f"Cycle failed: {e}")
            self.state = WorkflowState.ERROR
            self.metrics.error_count += 1
            return False

    def _display_dashboard(self):
        """Display real-time status dashboard"""
        uptime = datetime.now() - self.metrics.start_time
        avg_cycle_time = self.metrics.total_cycle_time / max(self.metrics.cycles_completed, 1)
        success_rate = (self.metrics.successful_operations /
                       max(self.metrics.successful_operations + self.metrics.failed_operations, 1) * 100)

        print("\n" + "="*60)
        print("           RALPH WIGGUM MANAGER - STATUS")
        print("="*60)
        print(f"\nStatus: {'🟢 RUNNING' if self.running else '🔴 STOPPED'}")
        print(f"State: {self.state.value.upper()}")
        print(f"Uptime: {uptime}")
        print(f"Cycles: {self.metrics.cycles_completed}")
        print(f"Last Cycle: {self.metrics.last_cycle_time:.2f}s ago")

        print("\n" + "-"*60)
        print("WORKFLOW STAGES")
        print("-"*60)
        for folder_name, folder_status in self.folders.items():
            status_icon = "→" if folder_status.item_count > 0 else "✓"
            print(f"{folder_name:20} {folder_status.item_count:3} items  {status_icon}")

        print("\n" + "-"*60)
        print("SKILL STATUS")
        print("-"*60)
        for skill_name, status in self.skill_status.items():
            status_icon = {
                SkillStatus.READY: "✓",
                SkillStatus.RUNNING: "⏳",
                SkillStatus.WAITING: "⏸",
                SkillStatus.FAILED: "✗",
                SkillStatus.DISABLED: "○"
            }.get(status, "?")
            print(f"{skill_name:25} {status_icon} {status.value}")

        print("\n" + "-"*60)
        print("METRICS")
        print("-"*60)
        print(f"Items Processed:   {self.metrics.items_processed}")
        print(f"Success Rate:      {success_rate:.1f}%")
        print(f"Avg Cycle Time:    {avg_cycle_time:.2f}s")
        print(f"Error Count:       {self.metrics.error_count}")

        print("\n" + "="*60)

    def run_continuous(self, interval: int = 60):
        """
        Run in continuous mode.

        Args:
            interval: Seconds between cycles
        """
        self.running = True
        self.logger.info("Starting continuous mode")

        try:
            while self.running:
                if not self.paused:
                    self._run_cycle()

                    # Display dashboard if monitoring enabled
                    if self.config.get('monitoring', {}).get('enabled', True):
                        self._display_dashboard()

                # Wait for next cycle
                time.sleep(interval)

        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
            self.running = False

        self.logger.info("Continuous mode stopped")

    def run_single_cycle(self):
        """Run a single workflow cycle"""
        self.logger.info("Running single cycle")
        self.running = True
        success = self._run_cycle()
        self.running = False

        self._display_dashboard()

        return success

    def validate_vault(self) -> bool:
        """
        Validate vault structure.

        Returns:
            True if vault is valid
        """
        self.logger.info("Validating vault structure")

        if not self.vault_path.exists():
            self.logger.error(f"Vault path does not exist: {self.vault_path}")
            return False

        required_folders = self.config.get('vault', {}).get('folders', [])

        for folder_name in required_folders:
            folder_path = self.vault_path / folder_name
            if not folder_path.exists():
                self.logger.warning(f"Creating missing folder: {folder_name}")
                folder_path.mkdir(parents=True, exist_ok=True)

        self.logger.info("Vault structure validated")
        return True

    def get_status(self) -> Dict:
        """
        Get current status.

        Returns:
            Status dictionary
        """
        return {
            'state': self.state.value,
            'running': self.running,
            'paused': self.paused,
            'metrics': {
                'cycles_completed': self.metrics.cycles_completed,
                'items_processed': self.metrics.items_processed,
                'successful_operations': self.metrics.successful_operations,
                'failed_operations': self.metrics.failed_operations,
                'error_count': self.metrics.error_count,
                'uptime': str(datetime.now() - self.metrics.start_time)
            },
            'folders': {
                name: {
                    'item_count': status.item_count,
                    'last_updated': status.last_updated.isoformat() if status.last_updated else None
                }
                for name, status in self.folders.items()
            },
            'skills': {
                name: status.value
                for name, status in self.skill_status.items()
            }
        }

    def pause(self):
        """Pause the workflow"""
        self.paused = True
        self.logger.info("Workflow paused")

    def resume(self):
        """Resume the workflow"""
        self.paused = False
        self.logger.info("Workflow resumed")

    def stop(self):
        """Stop the workflow"""
        self.running = False
        self.logger.info("Workflow stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Ralph Wiggum Manager - Autonomous Loop Orchestrator'
    )

    parser.add_argument(
        '--vault-path',
        required=True,
        help='Path to vault directory'
    )

    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )

    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run in continuous mode'
    )

    parser.add_argument(
        '--single-cycle',
        action='store_true',
        help='Run a single cycle'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Seconds between cycles (default: 60)'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate vault structure'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current status'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    try:
        # Create manager
        manager = RalphWiggumManager(
            vault_path=args.vault_path,
            config_path=args.config
        )

        if args.verbose:
            manager.logger.setLevel(logging.DEBUG)

        # Execute requested operation
        if args.validate:
            success = manager.validate_vault()
            sys.exit(0 if success else 1)

        elif args.status:
            status = manager.get_status()
            print(json.dumps(status, indent=2))
            sys.exit(0)

        elif args.single_cycle:
            success = manager.run_single_cycle()
            sys.exit(0 if success else 1)

        elif args.continuous:
            manager.run_continuous(interval=args.interval)
            sys.exit(0)

        else:
            # Default to single cycle
            success = manager.run_single_cycle()
            sys.exit(0 if success else 1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
