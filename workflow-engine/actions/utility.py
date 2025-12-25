"""Utility actions (screenshot, save, etc.)"""

import csv
from pathlib import Path
from datetime import datetime
from .base import BaseAction


class ScreenshotAction(BaseAction):
    """Take a screenshot"""

    def description(self):
        filename = self.step.get('file', 'screenshot.png')
        return f"Screenshot: {filename}"

    def execute(self):
        filename = self.step.get('file', f'screenshot-{datetime.now():%Y%m%d-%H%M%S}.png')
        filepath = Path('results') / filename

        # Ensure results directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Take screenshot
        if self.step.get('full_page', False):
            self.page.screenshot(path=str(filepath), full_page=True)
        else:
            self.page.screenshot(path=str(filepath))

        return f"Screenshot saved: {filepath}"


class SaveCSVAction(BaseAction):
    """Save extracted data to CSV file"""

    def description(self):
        data_name = self.step.get('data', 'data')
        filename = self.step.get('file', 'output.csv')
        return f"Save '{data_name}' to {filename}"

    def execute(self):
        data_name = self.step.get('data')
        filename = self.step.get('file', 'output.csv')

        if not data_name:
            raise ValueError("Save_csv action requires 'data' field")

        # Get data from store
        if data_name not in self.data_store:
            raise ValueError(f"Data '{data_name}' not found in data store")

        data = self.data_store[data_name]

        if not data:
            return f"No data to save ('{data_name}' is empty)"

        # Ensure results directory exists
        filepath = Path('results') / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Write CSV
        if isinstance(data, list) and isinstance(data[0], dict):
            # Table data
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

            return f"Saved {len(data)} rows to {filepath}"

        else:
            # Single value
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['value'])
                writer.writerow([data])

            return f"Saved value to {filepath}"


class SaveJSONAction(BaseAction):
    """Save extracted data to JSON file"""

    def description(self):
        data_name = self.step.get('data', 'data')
        filename = self.step.get('file', 'output.json')
        return f"Save '{data_name}' to {filename}"

    def execute(self):
        import json

        data_name = self.step.get('data')
        filename = self.step.get('file', 'output.json')
        destination = self.step.get('destination', 'results')

        if not data_name or data_name not in self.data_store:
            raise ValueError(f"Data '{data_name}' not found")

        data = self.data_store[data_name]

        filepath = Path(destination) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return f"Saved {len(data) if isinstance(data, list) else 1} items to {filepath}"


class ConditionalAction(BaseAction):
    """Conditional execution (if/else logic)"""

    def description(self):
        condition = self.step.get('if', 'condition')
        return f"If: {condition}"

    def execute(self):
        # Check if element exists
        if 'element_exists' in self.step:
            selector = self.step['element_exists']
            exists = self.page.query_selector(selector) is not None

            if exists:
                return f"Element exists: {selector} (condition TRUE)"
            else:
                # Could skip next steps or handle differently
                return f"Element not found: {selector} (condition FALSE)"

        # Check if data exists
        elif 'data_exists' in self.step:
            data_name = self.step['data_exists']
            exists = data_name in self.data_store

            if exists:
                return f"Data exists: {data_name} (condition TRUE)"
            else:
                return f"Data not found: {data_name} (condition FALSE)"

        else:
            raise ValueError("Conditional action requires 'element_exists' or 'data_exists'")


class RateLimitAction(BaseAction):
    """Add delay with optional jitter (polite scraping)"""

    def description(self):
        mode = self.step.get('mode', 'polite')
        seconds = self.step.get('seconds')
        if seconds:
            return f"Wait {seconds}s"
        return f"Rate limit: {mode} mode"

    def execute(self):
        import time
        import random

        mode = self.step.get('mode', 'polite')
        seconds = self.step.get('seconds')
        jitter = self.step.get('jitter', True)

        if seconds:
            delay = seconds
            if jitter:
                delay += random.uniform(-0.5, 0.5)
        else:
            # Predefined modes (respecting "HEAVILY SLOW DOWN" requirement)
            delays = {
                'polite': (1.0, 3.0),
                'normal': (0.5, 1.5),
                'fast': (0.1, 0.5),
                'slow': (3.0, 6.0)
            }
            min_delay, max_delay = delays.get(mode, (1.0, 3.0))
            delay = random.uniform(min_delay, max_delay)

        time.sleep(max(0, delay))
        return f"Waited {delay:.2f}s ({mode} mode)"
