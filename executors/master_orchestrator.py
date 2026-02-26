#!/usr/bin/env python3
"""
Master Orchestrator
Monitors /Approved folder and executes approved content across all platforms
"""

import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

class ApprovedFileHandler(FileSystemEventHandler):
    """Handles new files in Approved folder"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            self.orchestrator.log(f"New file detected: {Path(event.src_path).name}")
            self.orchestrator.process_file(Path(event.src_path))


class MasterOrchestrator:
    """Master orchestrator for executing approved content"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.approved_dir = self.project_root / "Approved"
        self.done_dir = self.project_root / "Done"
        self.logs_dir = self.project_root / "logs"
        self.screenshots_dir = self.logs_dir / "screenshots"

        # Ensure directories exist
        self.approved_dir.mkdir(exist_ok=True)
        self.done_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.screenshots_dir.mkdir(exist_ok=True)

        # Session directories for persistent browser contexts
        self.session_dirs = {
            'linkedin': self.project_root / '.linkedin_browser_data',
            'facebook': self.project_root / '.facebook_browser_data',
            'instagram': self.project_root / '.instagram_browser_data',
            'twitter': self.project_root / '.x_browser_data',
            'whatsapp': self.project_root / '.whatsapp_browser_data'
        }

        # Execution statistics
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'retried': 0
        }

    def log(self, message: str, level: str = "INFO"):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)

        log_file = self.logs_dir / "orchestrator.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')

    def parse_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """Parse YAML frontmatter from markdown file"""
        if not content.startswith('---'):
            return {}, content

        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content

        frontmatter_text = parts[1].strip()
        body = parts[2].strip()

        # Simple YAML parser
        metadata = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()

        return metadata, body

    def extract_content(self, body: str) -> str:
        """Extract actual content from markdown body"""
        # Look for "## Generated Content" section
        if "## Generated Content" in body:
            parts = body.split("## Generated Content", 1)
            if len(parts) > 1:
                content_section = parts[1]
                # Get content until next ## section
                if "##" in content_section:
                    content = content_section.split("##", 1)[0].strip()
                else:
                    content = content_section.strip()
                return content

        # Fallback: return everything after first heading
        lines = body.split('\n')
        content_lines = []
        skip_next = False

        for line in lines:
            if line.startswith('#'):
                skip_next = True
                continue
            if skip_next and line.strip():
                skip_next = False
            if not skip_next and line.strip():
                content_lines.append(line)

        return '\n'.join(content_lines).strip()

    def execute_with_retry(self, platform: str, metadata: Dict, content: str, max_attempts: int = 3) -> Tuple[bool, str]:
        """Execute with retry logic"""
        from executors.platform_executor import PlatformExecutor

        executor = PlatformExecutor(self.session_dirs, self.screenshots_dir, self.log)

        for attempt in range(1, max_attempts + 1):
            self.log(f"Attempt {attempt}/{max_attempts} for {platform}")

            try:
                success, message = executor.execute(platform, content, metadata)

                if success:
                    self.log(f"[SUCCESS] Execution successful on attempt {attempt}", "SUCCESS")
                    if attempt > 1:
                        self.stats['retried'] += 1
                    return True, message
                else:
                    self.log(f"[ERROR] Execution failed: {message}", "ERROR")

                    if attempt < max_attempts:
                        wait_time = 5 * (2 ** (attempt - 1))  # 5s, 10s, 20s
                        self.log(f"Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)

            except Exception as e:
                self.log(f"[ERROR] Exception during execution: {e}", "ERROR")

                if attempt < max_attempts:
                    wait_time = 5 * (2 ** (attempt - 1))
                    self.log(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)

        return False, f"Failed after {max_attempts} attempts"

    def move_to_done(self, filepath: Path) -> bool:
        """Move file to Done folder"""
        try:
            # Create dated subfolder
            date_folder = self.done_dir / datetime.now().strftime("%Y-%m-%d")
            date_folder.mkdir(exist_ok=True)

            # Move file
            destination = date_folder / filepath.name
            shutil.move(str(filepath), str(destination))

            self.log(f"Moved to Done: {destination.relative_to(self.project_root)}")
            return True

        except Exception as e:
            self.log(f"Error moving file to Done: {e}", "ERROR")
            return False

    def update_dashboard(self):
        """Update Dashboard.md with latest stats"""
        try:
            dashboard_file = self.project_root / "Dashboard.md"

            if not dashboard_file.exists():
                self.log("Dashboard.md not found, skipping update", "WARNING")
                return

            # Read current dashboard
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update execution stats section
            stats_section = f"""
## 🚀 Execution Stats (Last Run)
- **Total Executed**: {self.stats['total']}
- **Successful**: {self.stats['successful']} ({self.stats['successful']/max(self.stats['total'],1)*100:.1f}%)
- **Failed**: {self.stats['failed']}
- **Retried**: {self.stats['retried']}
- **Last Update**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

            # Append or update stats
            if "## 🚀 Execution Stats" in content:
                # Replace existing stats
                parts = content.split("## 🚀 Execution Stats")
                before = parts[0]
                after = parts[1].split("\n\n", 1)
                if len(after) > 1:
                    content = before + stats_section + "\n\n" + after[1]
                else:
                    content = before + stats_section
            else:
                # Append stats
                content += "\n" + stats_section

            # Write updated dashboard
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.log("Dashboard.md updated")

        except Exception as e:
            self.log(f"Error updating dashboard: {e}", "ERROR")

    def process_file(self, filepath: Path) -> bool:
        """Process a single approved file"""
        self.log("="*60)
        self.log(f"Processing: {filepath.name}")
        self.log("="*60)

        self.stats['total'] += 1

        try:
            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse frontmatter
            metadata, body = self.parse_frontmatter(content)

            # Get platform
            platform = metadata.get('platform', metadata.get('source', 'unknown')).lower()
            self.log(f"Platform: {platform}")

            if platform == 'unknown':
                self.log("Unknown platform, skipping", "ERROR")
                self.stats['failed'] += 1
                return False

            # Extract content
            post_content = self.extract_content(body)
            self.log(f"Content length: {len(post_content)} characters")

            # Execute with retry
            success, message = self.execute_with_retry(platform, metadata, post_content)

            if success:
                self.stats['successful'] += 1

                # Move to Done
                self.move_to_done(filepath)

                # Update dashboard
                self.update_dashboard()

                return True
            else:
                self.stats['failed'] += 1
                self.log(f"Execution failed: {message}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Error processing file: {e}", "ERROR")
            self.stats['failed'] += 1
            return False

    def process_all(self) -> Dict:
        """Process all files in Approved folder"""
        self.log("="*60)
        self.log("Master Orchestrator - Processing All Approved Items")
        self.log("="*60)

        # Get all markdown files
        files = list(self.approved_dir.glob("*.md"))

        if not files:
            self.log("No files found in Approved folder")
            return self.stats

        self.log(f"Found {len(files)} files to process")

        for filepath in files:
            self.process_file(filepath)
            time.sleep(2)  # Small delay between files

        # Log summary
        self.log("="*60)
        self.log("Execution Summary")
        self.log("="*60)
        self.log(f"Total: {self.stats['total']}")
        self.log(f"Successful: {self.stats['successful']}")
        self.log(f"Failed: {self.stats['failed']}")
        self.log(f"Retried: {self.stats['retried']}")
        self.log("="*60)

        return self.stats

    def monitor(self):
        """Monitor Approved folder for new files"""
        self.log("="*60)
        self.log("👁️ Master Orchestrator - Monitoring Mode")
        self.log("="*60)
        self.log(f"Watching: {self.approved_dir}")
        self.log("Press Ctrl+C to stop")
        self.log("="*60)

        # Process existing files first
        existing_files = list(self.approved_dir.glob("*.md"))
        if existing_files:
            self.log(f"Processing {len(existing_files)} existing files...")
            for filepath in existing_files:
                self.process_file(filepath)
                time.sleep(2)

        # Start monitoring
        event_handler = ApprovedFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.approved_dir), recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.log("Stopping monitor...")
            observer.stop()

        observer.join()
        self.log("Monitor stopped")


def main():
    """Main entry point"""
    orchestrator = MasterOrchestrator()

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--monitor":
            orchestrator.monitor()
        elif sys.argv[1] == "--file" and len(sys.argv) > 2:
            filepath = Path(sys.argv[2])
            if filepath.exists():
                orchestrator.process_file(filepath)
            else:
                print(f"Error: File not found: {filepath}")
                sys.exit(1)
        elif sys.argv[1] == "--process-all":
            orchestrator.process_all()
        else:
            print("Usage:")
            print("  python master_orchestrator.py --monitor")
            print("  python master_orchestrator.py --process-all")
            print("  python master_orchestrator.py --file <filepath>")
            sys.exit(1)
    else:
        # Default: process all
        orchestrator.process_all()

    # Exit with appropriate code
    if orchestrator.stats['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
