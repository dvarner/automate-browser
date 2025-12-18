"""Human interaction actions"""

import time
from .base import BaseAction


class WaitForHumanAction(BaseAction):
    """Pause workflow and wait for human interaction"""

    def description(self):
        reason = self.step.get('reason', 'Human interaction needed')
        return f"Wait for human: {reason}"

    def execute(self):
        reason = self.step.get('reason', 'Human interaction needed')
        continue_selector = self.step.get('continue_selector')
        continue_url = self.step.get('continue_url')
        timeout = self.step.get('timeout', 300)  # 5 min default

        print(f"\n{'='*60}")
        print(f"⏸️  HUMAN INTERACTION REQUIRED")
        print(f"   Reason: {reason}")

        if continue_selector:
            print(f"   Waiting for element: {continue_selector}")
            print(f"   (Will auto-continue when element appears)")
        elif continue_url:
            print(f"   Waiting for URL: {continue_url}")
            print(f"   (Will auto-continue when URL matches)")
        else:
            print(f"   Press ENTER in terminal to continue...")

        print(f"{'='*60}\n")

        # Wait for condition
        if continue_selector:
            # Wait for element to appear (human completed action)
            try:
                self.page.wait_for_selector(continue_selector, timeout=timeout * 1000)
                return f"Element appeared: {continue_selector}"
            except Exception:
                return f"Timeout waiting for {continue_selector}"

        elif continue_url:
            # Wait for URL to match
            start = time.time()
            while time.time() - start < timeout:
                if continue_url in self.page.url:
                    return f"URL changed to: {self.page.url}"
                time.sleep(0.5)
            return f"Timeout waiting for URL: {continue_url}"

        else:
            # Wait for manual input
            input("   Press ENTER to continue workflow... ")
            return "Human confirmed continuation"
