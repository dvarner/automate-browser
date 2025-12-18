"""Interaction actions (click, fill, etc.)"""

from .base import BaseAction


class ClickAction(BaseAction):
    """Click an element"""

    def description(self):
        return f"Click: {self.step.get('selector', 'element')}"

    def execute(self):
        selector = self.step.get('selector')
        if not selector:
            raise ValueError("Click action requires 'selector' field")

        # Optional: wait for element first
        if self.step.get('wait', True):
            self.page.wait_for_selector(selector)

        # Click
        self.page.click(selector)

        # Optional: wait after click
        if 'wait_after' in self.step:
            import time
            time.sleep(self.step['wait_after'])

        return f"Clicked: {selector}"


class FillAction(BaseAction):
    """Fill a form field"""

    def description(self):
        selector = self.step.get('selector', 'field')
        value = self.step.get('value', '')
        # Mask sensitive data
        if self.step.get('sensitive', False):
            value = '*' * len(str(value))
        return f"Fill {selector} = '{value}'"

    def execute(self):
        selector = self.step.get('selector')
        value = self.step.get('value', '')

        if not selector:
            raise ValueError("Fill action requires 'selector' field")

        # Optional: wait for element first
        if self.step.get('wait', True):
            self.page.wait_for_selector(selector)

        # Clear first (optional)
        if self.step.get('clear', True):
            self.page.fill(selector, '')

        # Fill
        self.page.fill(selector, str(value))

        # Optional: press Enter after fill
        if self.step.get('press_enter', False):
            self.page.press(selector, 'Enter')

        return f"Filled: {selector}"
