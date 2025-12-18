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
