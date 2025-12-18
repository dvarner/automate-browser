"""Base action class for all workflow actions"""

class BaseAction:
    """Base class for all workflow actions"""

    def __init__(self, step, page, data_store):
        """
        Initialize action

        Args:
            step: YAML step definition (dict)
            page: Playwright page object
            data_store: Shared data storage dict
        """
        self.step = step
        self.page = page
        self.data_store = data_store

    def description(self):
        """Return human-readable description of action"""
        return "Action"

    def execute(self):
        """Execute the action. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement execute()")
