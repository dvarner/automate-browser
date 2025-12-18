"""Navigation and waiting actions"""

import time
from .base import BaseAction


class NavigateAction(BaseAction):
    """Navigate to a URL"""

    def description(self):
        return f"Navigate to {self.step.get('url', 'URL')}"

    def execute(self):
        url = self.step.get('url')
        if not url:
            raise ValueError("Navigate action requires 'url' field")

        self.page.goto(url)
        return f"Navigated to {url}"


class WaitAction(BaseAction):
    """Wait for element or time"""

    def description(self):
        if 'selector' in self.step:
            return f"Wait for element: {self.step['selector']}"
        elif 'seconds' in self.step:
            return f"Wait {self.step['seconds']} seconds"
        return "Wait"

    def execute(self):
        # Wait for selector
        if 'selector' in self.step:
            selector = self.step['selector']
            timeout = self.step.get('timeout', 30) * 1000  # Convert to ms
            self.page.wait_for_selector(selector, timeout=timeout)
            return f"Element appeared: {selector}"

        # Wait for time
        elif 'seconds' in self.step:
            seconds = self.step['seconds']
            time.sleep(seconds)
            return f"Waited {seconds}s"

        else:
            raise ValueError("Wait action requires 'selector' or 'seconds' field")
