"""
Playwright Codegen to YAML Converter

Converts Playwright-generated Python code into YAML workflow format
"""

import re
import sys
import yaml
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


class PlaywrightCodegenConverter:
    """Convert Playwright codegen Python code to YAML workflow"""

    def __init__(self):
        self.steps = []
        self.workflow_name = "Generated Workflow"
        self.browser = "chromium"

    def parse_python_code(self, code):
        """Parse Playwright Python code and extract actions"""
        lines = code.split('\n')

        for line in lines:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Extract actions from page method calls
            step = self._parse_line(line)
            if step:
                self.steps.append(step)

    def _parse_line(self, line):
        """Parse a single line of Playwright code"""

        # page.goto("url") or page.goto('url')
        goto_match = re.search(r'page\.goto\(["\'](.+?)["\']\)', line)
        if goto_match:
            return {
                'action': 'navigate',
                'url': goto_match.group(1)
            }

        # page.fill("selector", "value") - handle mixed quotes
        fill_match = re.search(r'page\.fill\(["\'](.+?)["\']\s*,\s*["\'](.+?)["\']\)', line)
        if fill_match:
            return {
                'action': 'fill',
                'selector': fill_match.group(1),
                'value': fill_match.group(2)
            }

        # page.click("selector")
        click_match = re.search(r'page\.click\(["\'](.+?)["\']\)', line)
        if click_match:
            return {
                'action': 'click',
                'selector': click_match.group(1)
            }

        # page.press("selector", "key")
        press_match = re.search(r'page\.press\(["\'](.+?)["\']\s*,\s*["\'](.+?)["\']\)', line)
        if press_match:
            selector = press_match.group(1)
            key = press_match.group(2)
            if key == 'Enter':
                # Convert to fill with press_enter
                return {
                    'action': 'fill',
                    'selector': selector,
                    'value': '',  # Will need manual editing
                    'press_enter': True,
                    '_comment': 'UPDATE VALUE FIELD'
                }

        # page.wait_for_selector("selector")
        wait_match = re.search(r'page\.wait_for_selector\(["\'](.+?)["\']\)', line)
        if wait_match:
            return {
                'action': 'wait',
                'selector': wait_match.group(1)
            }

        # page.screenshot(path="file.png")
        screenshot_match = re.search(r'page\.screenshot\(path=["\'](.+?)["\']\)', line)
        if screenshot_match:
            return {
                'action': 'screenshot',
                'file': screenshot_match.group(1)
            }

        # page.locator("selector").click()
        locator_click = re.search(r'page\.locator\(["\'](.+?)["\']\)\.click\(\)', line)
        if locator_click:
            return {
                'action': 'click',
                'selector': locator_click.group(1)
            }

        # page.locator("selector").fill("value")
        locator_fill = re.search(r'page\.locator\(["\'](.+?)["\']\)\.fill\(["\'](.+?)["\']\)', line)
        if locator_fill:
            return {
                'action': 'fill',
                'selector': locator_fill.group(1),
                'value': locator_fill.group(2)
            }

        # page.get_by_role("role", name="name").click()
        role_click = re.search(r'page\.get_by_role\(["\']([^"\']+)["\'](?:,\s*name=["\']([^"\']+)["\']\))?\)\.click\(\)', line)
        if role_click:
            role = role_click.group(1)
            name = role_click.group(2) if role_click.group(2) else None

            if name:
                # Try to create a more specific selector
                selector = f'role={role}[name="{name}"]'
            else:
                selector = f'role={role}'

            return {
                'action': 'click',
                'selector': selector,
                '_comment': 'Convert role selector to CSS selector for better compatibility'
            }

        # page.get_by_placeholder("text").fill("value")
        placeholder_fill = re.search(r'page\.get_by_placeholder\(["\']([^"\']+)["\']\)\.fill\(["\']([^"\']+)["\']\)', line)
        if placeholder_fill:
            placeholder = placeholder_fill.group(1)
            value = placeholder_fill.group(2)
            return {
                'action': 'fill',
                'selector': f'[placeholder="{placeholder}"]',
                'value': value
            }

        # page.get_by_text("text").click()
        text_click = re.search(r'page\.get_by_text\(["\']([^"\']+)["\']\)\.click\(\)', line)
        if text_click:
            text = text_click.group(1)
            return {
                'action': 'click',
                'selector': f'text="{text}"',
                '_comment': 'Convert text selector to CSS selector for better compatibility'
            }

        return None

    def generate_yaml(self, output_file=None):
        """Generate YAML workflow file"""
        workflow = {
            'name': self.workflow_name,
            'browser': self.browser,
            'timeout': 30,
            'steps': self.steps
        }

        # Add comments for steps that need manual editing
        yaml_output = yaml.dump(workflow, sort_keys=False, allow_unicode=True)

        # Add helpful header
        header = "# Auto-generated from Playwright codegen\n"
        header += "# Review and edit as needed:\n"
        header += "#   - Update workflow name\n"
        header += "#   - Add wait_for_human steps for logins/CAPTCHAs\n"
        header += "#   - Add extract/extract_table for data scraping\n"
        header += "#   - Convert role/text selectors to CSS selectors\n\n"

        full_output = header + yaml_output

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_output)
            print(f"✅ YAML workflow saved to: {output_file}")
        else:
            print(full_output)

        return full_output

    def convert_file(self, input_file, output_file=None):
        """Convert a Playwright Python file to YAML"""
        with open(input_file, 'r', encoding='utf-8') as f:
            code = f.read()

        self.parse_python_code(code)

        # Auto-generate output filename if not provided
        if not output_file:
            input_path = Path(input_file)
            output_file = f"workflows/{input_path.stem}.yaml"

        self.generate_yaml(output_file)
        print(f"✅ Converted {len(self.steps)} actions")

    def convert_string(self, code, output_file=None):
        """Convert Playwright Python code string to YAML"""
        self.parse_python_code(code)

        if output_file:
            self.generate_yaml(output_file)
        else:
            return self.generate_yaml()

        print(f"✅ Converted {len(self.steps)} actions")


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Convert Playwright codegen Python code to YAML workflow',
        epilog="""
Examples:
  # Convert a Python file
  python codegen_converter.py recorded.py

  # Specify output file
  python codegen_converter.py recorded.py -o workflows/my-workflow.yaml

  # Read from stdin
  playwright codegen https://example.com | python codegen_converter.py --stdin
        """
    )

    parser.add_argument('input_file', nargs='?', help='Playwright Python file to convert')
    parser.add_argument('-o', '--output', help='Output YAML file (default: workflows/<input>.yaml)')
    parser.add_argument('--stdin', action='store_true', help='Read from stdin')
    parser.add_argument('--name', help='Workflow name', default='Generated Workflow')
    parser.add_argument('--browser', help='Browser type', default='chromium',
                       choices=['chromium', 'chrome', 'firefox', 'webkit'])

    args = parser.parse_args()

    converter = PlaywrightCodegenConverter()
    converter.workflow_name = args.name
    converter.browser = args.browser

    if args.stdin:
        # Read from stdin
        code = sys.stdin.read()
        converter.convert_string(code, args.output)

    elif args.input_file:
        # Read from file
        converter.convert_file(args.input_file, args.output)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
