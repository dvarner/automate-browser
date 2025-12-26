"""
Multi-tab scraping utility module.
Provides tab filtering and template-based scraping across multiple browser tabs.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Callable


class TabGroupFilter:
    """Filter tabs based on group criteria"""

    FILTER_ALL = 'all'
    FILTER_UNGROUPED = 'ungrouped'
    FILTER_GROUPED = 'grouped'
    FILTER_REGEX = 'regex'

    def __init__(self, filter_type='all', group_pattern=None):
        """
        Initialize tab group filter.

        Args:
            filter_type: One of FILTER_* constants
            group_pattern: Regex pattern string (only for FILTER_REGEX)
        """
        self.filter_type = filter_type
        self.group_pattern = group_pattern

        if filter_type == self.FILTER_REGEX and not group_pattern:
            raise ValueError("group_pattern required when filter_type is 'regex'")

    def matches(self, tab_data: Dict) -> bool:
        """Check if tab matches filter criteria.

        Args:
            tab_data: Dict with 'group_name' key (None if ungrouped)

        Returns:
            True if tab matches filter criteria
        """
        if self.filter_type == self.FILTER_ALL:
            return True

        elif self.filter_type == self.FILTER_UNGROUPED:
            return tab_data.get('group_name') is None

        elif self.filter_type == self.FILTER_GROUPED:
            return tab_data.get('group_name') is not None

        elif self.filter_type == self.FILTER_REGEX:
            group_name = tab_data.get('group_name')
            if not group_name:
                return False
            return re.match(self.group_pattern, group_name) is not None

        return False


class MultiTabScraper:
    """Core multi-tab scraping engine using templates"""

    def __init__(self, template_path: Path, group_filter: Optional[TabGroupFilter] = None,
                 continue_on_error: bool = True):
        """
        Initialize multi-tab scraper.

        Args:
            template_path: Path to template JSON file
            group_filter: Optional TabGroupFilter instance
            continue_on_error: If True, continue scraping on errors
        """
        self.template_path = template_path
        self.group_filter = group_filter
        self.continue_on_error = continue_on_error

        # Load template
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = json.load(f)

    def scrape_pages(self, pages: List, progress_callback: Optional[Callable] = None) -> Dict:
        """Scrape multiple Playwright pages using the template.

        Args:
            pages: List of Playwright Page objects
            progress_callback: Optional function(current, total, tab_url)

        Returns:
            {
                'total_tabs': int,
                'successful': int,
                'failed': int,
                'results': [
                    {
                        'tab_index': 0,
                        'tab_url': 'https://...',
                        'tab_title': '...',
                        'tab_group': 'Dev' or None,
                        'status': 'success' | 'error',
                        'error_message': '...' (if failed),
                        'items': [...]  # Extracted data
                    }
                ]
            }
        """
        results = []
        successful = 0
        failed = 0

        total = len(pages)

        for idx, page in enumerate(pages):
            try:
                # Get page info
                url = page.url
                title = page.title()

                # Call progress callback
                if progress_callback:
                    progress_callback(idx + 1, total, url)

                # Apply template to this page
                items = self._apply_template_to_page(page, self.template)

                # Success
                results.append({
                    'tab_index': idx,
                    'tab_url': url,
                    'tab_title': title,
                    'tab_group': None,  # TODO: Get group from page metadata
                    'status': 'success',
                    'items': items
                })
                successful += 1

            except Exception as e:
                # Error handling
                error_msg = str(e)

                results.append({
                    'tab_index': idx,
                    'tab_url': getattr(page, 'url', 'unknown'),
                    'tab_title': getattr(page, 'title', lambda: 'unknown')() if callable(getattr(page, 'title', None)) else 'unknown',
                    'tab_group': None,
                    'status': 'error',
                    'error_message': error_msg,
                    'items': []
                })
                failed += 1

                if not self.continue_on_error:
                    raise

        return {
            'total_tabs': total,
            'successful': successful,
            'failed': failed,
            'results': results
        }

    def _apply_template_to_page(self, page, template: Dict) -> List[Dict]:
        """Apply template to a single page.

        Args:
            page: Playwright Page object
            template: Template dict with container and fields

        Returns:
            List of extracted item dicts
        """
        # Wait for container
        container_selector = template['container']['selector']
        page.wait_for_selector(container_selector, timeout=10000)

        # Query all containers
        containers = page.query_selector_all(container_selector)

        # Extract from each container
        items = []
        for container in containers:
            item_data = {}

            for field in template['fields']:
                field_name = field['name']
                field_selector = field['selector']
                attribute = field.get('attribute', 'text')
                required = field.get('required', True)

                try:
                    elem = container.query_selector(field_selector)

                    if elem:
                        # Extract value
                        if attribute == 'text':
                            item_data[field_name] = elem.inner_text().strip()
                        else:
                            item_data[field_name] = elem.get_attribute(attribute)
                    else:
                        # Element not found
                        if required and not self.continue_on_error:
                            raise ValueError(f"Required field '{field_name}' not found")
                        item_data[field_name] = None

                except Exception as e:
                    if required and not self.continue_on_error:
                        raise
                    item_data[field_name] = None

            items.append(item_data)

        return items
