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
