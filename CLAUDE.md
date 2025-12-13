# Claude Code - AI Assistant

## What I Do

I'm Claude Code, an AI-powered assistant that helps you with software engineering tasks including:

- Writing, editing, and refactoring code
- Debugging and fixing issues
- Explaining codebases and architectures
- Automating workflows and tasks
- Managing git repositories
- Running tests and builds
- Creating documentation

All task logs are saved to `ai-tasks/{YYMMDD}-{HHMMSS}.log` files for your reference.

## Project Management System

This project uses the AI PM GUI system for task tracking and feature management. The system provides multiple ways to manage work:

### Quick Start

```bash
# Launch the GUI
cd ai-tasks
python run-py.py

# Or use CLI commands (no GUI needed)
python run-py.py list --status todo
python run-py.py add --type FEAT --number 1 --title "Feature name" --priority high
```

### Three Ways to Use the System

1. **GUI (Visual Management)**
   - Kanban board with drag-and-drop
   - List view for tabular data
   - Stats view for progress tracking
   - Visit `http://localhost:8000` after running `python run-py.py`

2. **CLI (Quick Operations)**
   ```bash
   # Add a ticket
   python run-py.py add --type FEAT --number 5 --title "Add feature X" --priority high

   # List tickets with filters
   python run-py.py list --status todo --priority high
   python run-py.py list --tag backend --format json

   # Update a ticket
   python run-py.py update FEAT-005 --status in_progress

   # Show ticket details
   python run-py.py show FEAT-005

   # Interactive mode
   python run-py.py quick-add
   ```

3. **Python API (Automation)**
   ```python
   from backend.api_client import TicketManager

   tm = TicketManager("ai-tasks/pm.db")

   # Create a ticket
   ticket = tm.create_ticket(
       ticket_id="FEAT-073",
       title="Implement feature X",
       priority="high",
       tags=["backend", "automation"]
   )

   # List and filter
   todo_tickets = tm.list_tickets(status="todo", priority="high")

   # Update ticket
   tm.update_ticket("FEAT-073", status="in_progress")
   ```

### Ticket Types

- **FEAT** - New features (e.g., FEAT-001)
- **BUG** - Bug fixes (e.g., BUG-001)
- **TASK** - General tasks, refactoring, chores
- **HOTFIX** - Urgent production fixes
- **RESEARCH** - Investigation, POC, discovery
- **INFRA** - Infrastructure, deployment, DevOps

### Workflow Guidelines

1. **Break Down Features** - Use the ticket system to break large features into 1-4 hour tasks
2. **Track Progress** - Update ticket status as work progresses (todo → in_progress → done)
3. **Log Sessions** - Create detailed log files in ticket folders for each work session
4. **Use Tags** - Organize tickets with tags like `browser-automation`, `selenium`, `scraping`
5. **Set Priorities** - Mark urgent work as `high` or `critical`

### Folder Structure

```
ai-tasks/
├── pm.db                                    # SQLite database (ticket data)
├── run-py.py                               # Launcher script
├── pm.md                                   # Full PM system documentation
├── README.md                               # AI PM GUI documentation
├── QUICKSTART.md                           # Quick reference guide
└── YYMMDD-HHMM_feature-name/              # Feature folders (timestamped)
    ├── TICKET-ID-description/
    │   ├── TICKET-ID-description.md       # Ticket specification
    │   ├── YYMMDD-HHMMSS.log             # Work session logs
    │   └── notes.md                       # Optional notes
    └── ...
```

### Documentation References

- **pm.md** - Complete PM system guide, templates, and best practices
- **README.md** - AI PM GUI technical documentation
- **QUICKSTART.md** - Quick reference for common operations

### When to Use Which Method

- **Use GUI** when visualizing project progress, dragging tickets, or reviewing stats
- **Use CLI** when quickly adding tickets from terminal or filtering during development
- **Use Python API** when automating ticket creation or building custom workflows

### Database Location

The project database is located at `ai-tasks/pm.db` and tracks:
- Tickets (features, bugs, tasks)
- Phases (project milestones)
- Logs (work session history)
- Tags and priorities

## Browser Automation with Python

For detailed guides on automating browser tasks with Python, see [BROWSER_AUTOMATION.md](BROWSER_AUTOMATION.md).

Quick overview of available automation tasks:

1. **Getting list of open browser tabs** - Connect to running browsers and retrieve tab information
2. **Opening browsers with multiple tabs and groups** - Programmatically launch browsers with organized tab sets
3. **Extracting webpage content** - Scrape articles and data from websites

Supported libraries: Selenium, BeautifulSoup, Playwright, Newspaper3k
