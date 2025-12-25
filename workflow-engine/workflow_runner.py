"""
YAML Workflow Engine for Browser Automation
Executes browser automation workflows defined in YAML files
"""

import yaml
import sys
import csv
import os
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from actions.navigation import NavigateAction, WaitAction
from actions.interaction import ClickAction, FillAction
from actions.extraction import ExtractAction, ExtractTableAction, TemplateExtractAction
from actions.human import WaitForHumanAction
from actions.utility import ScreenshotAction, SaveCSVAction, SaveJSONAction, RateLimitAction, ConditionalAction
from actions.download import DownloadAction, DownloadLinkAction, DownloadMediaAction


class WorkflowRunner:
    """Main workflow execution engine"""

    # Map action names to action classes
    ACTION_MAP = {
        'navigate': NavigateAction,
        'click': ClickAction,
        'fill': FillAction,
        'wait': WaitAction,
        'wait_for_human': WaitForHumanAction,
        'extract': ExtractAction,
        'extract_table': ExtractTableAction,
        'template_extract': TemplateExtractAction,
        'screenshot': ScreenshotAction,
        'save_csv': SaveCSVAction,
        'save_json': SaveJSONAction,
        'rate_limit': RateLimitAction,
        'conditional': ConditionalAction,
        'download': DownloadAction,
        'download_link': DownloadLinkAction,
        'download_media': DownloadMediaAction,
    }

    def __init__(self, workflow_file, headless=False, browser_type='chromium'):
        """
        Initialize workflow runner

        Args:
            workflow_file: Path to YAML workflow file
            headless: Run browser in headless mode
            browser_type: Browser to use (chromium, firefox, webkit)
        """
        self.workflow_file = Path(workflow_file)
        self.headless = headless
        self.browser_type_name = browser_type
        self.workflow = None
        self.browser = None
        self.context = None
        self.page = None
        self.data_store = {}  # Store extracted data

    def load_workflow(self):
        """Load and validate YAML workflow file"""
        if not self.workflow_file.exists():
            raise FileNotFoundError(f"Workflow file not found: {self.workflow_file}")

        with open(self.workflow_file, 'r') as f:
            self.workflow = yaml.safe_load(f)

        # Validate required fields
        if 'name' not in self.workflow:
            raise ValueError("Workflow must have a 'name' field")
        if 'steps' not in self.workflow:
            raise ValueError("Workflow must have a 'steps' field")

        print(f"✅ Loaded workflow: {self.workflow['name']}")
        print(f"   Steps: {len(self.workflow['steps'])}")

    def setup_browser(self):
        """Initialize Playwright browser"""
        self.playwright = sync_playwright().start()

        # Get browser type
        browser_types = {
            'chromium': self.playwright.chromium,
            'chrome': self.playwright.chromium,
            'firefox': self.playwright.firefox,
            'webkit': self.playwright.webkit,
        }

        browser_launcher = browser_types.get(
            self.workflow.get('browser', self.browser_type_name).lower(),
            self.playwright.chromium
        )

        # Launch browser
        self.browser = browser_launcher.launch(
            headless=self.headless,
            channel='chrome' if self.workflow.get('browser', '').lower() in ['chrome', 'brave'] else None
        )

        # Create context
        timeout = self.workflow.get('timeout', 30) * 1000  # Convert to ms
        self.context = self.browser.new_context()
        self.context.set_default_timeout(timeout)

        # Create page
        self.page = self.context.new_page()

        print(f"✅ Browser launched: {self.workflow.get('browser', 'chromium')}")

    def execute_step(self, step_num, step):
        """Execute a single workflow step"""
        action_name = step.get('action')

        if not action_name:
            raise ValueError(f"Step {step_num}: Missing 'action' field")

        if action_name not in self.ACTION_MAP:
            raise ValueError(f"Step {step_num}: Unknown action '{action_name}'")

        # Get action class and instantiate
        action_class = self.ACTION_MAP[action_name]
        action = action_class(step, self.page, self.data_store)

        # Execute action
        print(f"\n[{step_num}/{len(self.workflow['steps'])}] {action_name.upper()}: {action.description()}")

        try:
            result = action.execute()

            if result:
                print(f"    ✅ {result}")

            return True

        except PlaywrightTimeout as e:
            print(f"    ❌ Timeout: {e}")
            if step.get('continue_on_error', False):
                print(f"    ⚠️  Continuing despite error (continue_on_error=true)")
                return True
            raise

        except Exception as e:
            print(f"    ❌ Error: {e}")
            if step.get('continue_on_error', False):
                print(f"    ⚠️  Continuing despite error (continue_on_error=true)")
                return True
            raise

    def run(self):
        """Execute the complete workflow"""
        start_time = datetime.now()

        try:
            # Load workflow
            self.load_workflow()

            # Setup browser
            self.setup_browser()

            print(f"\n{'='*60}")
            print(f"EXECUTING: {self.workflow['name']}")
            print(f"{'='*60}")

            # Execute each step
            for idx, step in enumerate(self.workflow['steps'], 1):
                self.execute_step(idx, step)

            # Success
            duration = (datetime.now() - start_time).total_seconds()
            print(f"\n{'='*60}")
            print(f"✅ WORKFLOW COMPLETED SUCCESSFULLY")
            print(f"   Duration: {duration:.2f}s")
            print(f"{'='*60}\n")

        except KeyboardInterrupt:
            print("\n\n⚠️  Workflow interrupted by user")

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            print(f"\n{'='*60}")
            print(f"❌ WORKFLOW FAILED")
            print(f"   Error: {e}")
            print(f"   Duration: {duration:.2f}s")
            print(f"{'='*60}\n")
            raise

        finally:
            # Cleanup
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if hasattr(self, 'playwright'):
                self.playwright.stop()


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='YAML Workflow Engine for Browser Automation')
    parser.add_argument('workflow', help='Path to YAML workflow file')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--browser', default='chromium',
                       choices=['chromium', 'chrome', 'firefox', 'webkit'],
                       help='Browser to use (default: chromium)')

    args = parser.parse_args()

    # Run workflow
    runner = WorkflowRunner(args.workflow, headless=args.headless, browser_type=args.browser)
    runner.run()


if __name__ == '__main__':
    main()
