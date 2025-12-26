"""Data extraction actions"""

from .base import BaseAction


class ExtractAction(BaseAction):
    """Extract single value from page"""

    def description(self):
        name = self.step.get('name', 'value')
        selector = self.step.get('selector', 'element')
        return f"Extract '{name}' from {selector}"

    def execute(self):
        selector = self.step.get('selector')
        name = self.step.get('name', 'extracted_value')
        attribute = self.step.get('attribute', 'text')  # text, href, src, etc.

        if not selector:
            raise ValueError("Extract action requires 'selector' field")

        # Wait for element
        self.page.wait_for_selector(selector)

        # Extract value
        if attribute == 'text':
            value = self.page.inner_text(selector)
        else:
            value = self.page.get_attribute(selector, attribute)

        # Store in data store
        self.data_store[name] = value

        return f"Extracted '{name}' = '{value[:50]}...'" if len(str(value)) > 50 else f"Extracted '{name}' = '{value}'"


class ExtractTableAction(BaseAction):
    """Extract table/list data from page"""

    def description(self):
        name = self.step.get('name', 'table')
        rows_selector = self.step.get('rows', 'row')
        return f"Extract table '{name}' (selector: {rows_selector})"

    def execute(self):
        name = self.step.get('name', 'table_data')
        rows_selector = self.step.get('rows')
        columns = self.step.get('columns', {})

        if not rows_selector:
            raise ValueError("Extract_table action requires 'rows' field")
        if not columns:
            raise ValueError("Extract_table action requires 'columns' field")

        # Wait for first row
        self.page.wait_for_selector(rows_selector)

        # Get all row elements
        row_elements = self.page.query_selector_all(rows_selector)

        # Extract data from each row
        table_data = []
        for row_elem in row_elements:
            row_data = {}

            for col_name, col_selector in columns.items():
                try:
                    # Query within this row
                    elem = row_elem.query_selector(col_selector)
                    if elem:
                        row_data[col_name] = elem.inner_text().strip()
                    else:
                        row_data[col_name] = None
                except Exception:
                    row_data[col_name] = None

            table_data.append(row_data)

        # Store in data store
        self.data_store[name] = table_data

        return f"Extracted {len(table_data)} rows into '{name}'"


class TemplateExtractAction(BaseAction):
    """Extract data using saved template"""

    def description(self):
        template_file = self.step.get('template', 'template.json')
        name = self.step.get('name', 'template_data')
        return f"Extract using template '{template_file}' into '{name}'"

    def execute(self):
        import json
        from pathlib import Path

        template_file = self.step.get('template')
        name = self.step.get('name', 'template_data')
        max_pages = self.step.get('max_pages', 1)

        if not template_file:
            raise ValueError("template_extract requires 'template' field")

        # Load template
        template_path = Path('templates') / template_file
        if not template_path.exists():
            template_path = Path('workflows') / template_file

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_file}")

        with open(template_path, 'r') as f:
            template = json.load(f)

        # Extract data
        all_data = []
        page_num = 1

        while page_num <= max_pages:
            print(f"    📄 Extracting page {page_num}...")

            # Wait for container
            container_selector = template['container']['selector']
            self.page.wait_for_selector(container_selector, timeout=10000)

            # Get all container instances
            containers = self.page.query_selector_all(container_selector)
            print(f"    Found {len(containers)} items on page {page_num}")

            # Extract from each container
            for idx, container in enumerate(containers):
                item_data = {}

                for field in template['fields']:
                    field_name = field['name']
                    field_selector = field['selector']
                    attribute = field.get('attribute', 'text')
                    required = field.get('required', True)

                    try:
                        elem = container.query_selector(field_selector)
                        if elem:
                            if attribute == 'text':
                                item_data[field_name] = elem.inner_text().strip()
                            else:
                                item_data[field_name] = elem.get_attribute(attribute)
                        else:
                            if required:
                                if self.step.get('continue_on_missing', False):
                                    item_data[field_name] = None
                                else:
                                    raise ValueError(f"Required field '{field_name}' not found")
                            else:
                                item_data[field_name] = None
                    except Exception as e:
                        if required and not self.step.get('continue_on_missing', False):
                            raise
                        item_data[field_name] = None

                all_data.append(item_data)

            # Pagination handling
            if page_num < max_pages and template.get('pagination', {}).get('enabled'):
                next_selector = template['pagination'].get('next_button')
                if next_selector:
                    try:
                        next_btn = self.page.query_selector(next_selector)
                        if next_btn:
                            if template['pagination'].get('type') == 'manual':
                                print(f"    ⏸️  Please click 'Next Page' button...")
                                input("    Press Enter after clicking...")
                            else:
                                self.page.click(next_selector)
                                self.page.wait_for_load_state('networkidle')
                            page_num += 1
                        else:
                            break
                    except:
                        break
                else:
                    break
            else:
                break

        # Store in data store
        self.data_store[name] = all_data

        return f"Extracted {len(all_data)} items using template"


class ScrapeAllTabsAction(BaseAction):
    """Scrape all open tabs using template with group filtering"""

    def description(self):
        template = self.step.get('template', 'template.json')
        filter_type = self.step.get('filter', 'all')
        return f"Scrape all tabs using '{template}' (filter: {filter_type})"

    def execute(self):
        import sys
        from pathlib import Path

        # Add utils to path
        utils_path = Path(__file__).parent.parent / 'utils'
        if str(utils_path) not in sys.path:
            sys.path.insert(0, str(utils_path))

        from multi_tab_scraper import MultiTabScraper, TabGroupFilter

        # Parse parameters
        template_file = self.step.get('template')
        if not template_file:
            raise ValueError("scrape_all_tabs requires 'template' field")

        output_name = self.step.get('name', 'multi_tab_data')
        filter_type = self.step.get('filter', 'all')
        group_pattern = self.step.get('group_pattern')
        continue_on_error = self.step.get('continue_on_error', True)

        # Load template
        template_path = Path('templates') / template_file
        if not template_path.exists():
            template_path = Path('workflows') / template_file
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_file}")

        # Create filter
        group_filter = None
        if filter_type != 'all':
            group_filter = TabGroupFilter(filter_type, group_pattern)

        # Create scraper
        scraper = MultiTabScraper(template_path, group_filter, continue_on_error)

        # Get browser context pages
        context = self.page.context
        pages = context.pages

        print(f"    Found {len(pages)} open tabs")

        # Scrape with progress
        results = scraper.scrape_pages(
            pages,
            progress_callback=lambda c, t, u: print(f"    [{c}/{t}] {u[:60]}...")
        )

        # Store results
        self.data_store[output_name] = results

        # Summary
        total_items = sum(len(r['items']) for r in results['results'] if r['status'] == 'success')
        return f"Scraped {results['successful']} tabs ({results['failed']} failed), {total_items} items"
