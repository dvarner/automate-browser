# AI Project Manager GUI

**A lightweight, shared project management tool for all Claude projects**

---

## Vision

Create a super-light project management GUI to replace the growing `ai-tasks/ROADMAP.md` files and folder structure across all Claude projects. This tool provides:

- 📋 **Kanban board** for visual task management
- 🔍 **Search & filtering** across tickets, phases, and tags
- 📊 **Progress tracking** with metrics and charts
- 📝 **Session logging** to track daily work
- 🏷️ **Tag management** for organization
- 📤 **Export to markdown** for sharing/archiving

## Architecture

### Shared Tool, Per-Project Data

```
D:\Claude\
├── ai-pm-gui/                   # Shared tool (THIS REPO)
│   ├── backend/                 # FastAPI server
│   ├── frontend/                # Vanilla JS + Tailwind
│   ├── migrations/              # Import/export scripts
│   └── run.py                   # Main entry point
│
├── MeetKale/
│   └── ai-tasks/
│       ├── pm.db                # Project-specific database
│       └── run-pm.py            # Launcher (calls ai-pm-gui)
│
└── OtherProject/
    └── ai-tasks/
        ├── pm.db                # Separate database
        └── run-pm.py            # Same launcher script
```

**Key Design:**
- **One codebase** in `D:\Claude\ai-pm-gui` (easy to update/maintain)
- **Per-project databases** in each `ai-tasks/pm.db` (data isolation)
- **Launcher script** in each project sets DB path via environment variable
- **No code duplication** - all projects share the same FE/BE/logic

### How It Works

1. User navigates to `D:\Claude\MeetKale\ai-tasks\`
2. Runs `python run-pm.py`
3. Launcher script:
   - Finds `D:\Claude\ai-pm-gui` (shared tool)
   - Sets `PM_DB_PATH` to current project's `pm.db`
   - Starts FastAPI backend
   - Opens browser to GUI
4. GUI talks to backend, which uses project-specific database

---

## Tech Stack

### Backend: FastAPI

**Why FastAPI over Flask?**

| Feature | Flask | FastAPI |
|---------|-------|---------|
| Simplicity | ✅ Simpler | ⚠️ Slightly more verbose |
| API Docs | ❌ Manual | ✅ **Auto-generated Swagger** |
| Validation | ❌ Manual | ✅ **Built-in Pydantic** |
| Type Safety | ⚠️ Optional | ✅ **Required (type hints)** |
| Async Support | ⚠️ Extensions | ✅ Native |
| Modern Python | ⚠️ Optional | ✅ **Enforced (3.7+)** |

**Decision: FastAPI**
- Auto-generated API docs at `/docs` (amazing for debugging)
- Built-in validation = fewer bugs
- Type hints make code self-documenting
- Room to grow (async if needed)
- Modern Python best practices

### Frontend: Vanilla JS + Tailwind CSS

**Why Vanilla JS over React?**

✅ **Vanilla JS is perfect for this because:**
- Simple CRUD operations (no complex state)
- Local-only tool (no real-time collaboration)
- Want it lightweight and fast to build
- No build tooling overhead (npm, webpack, etc.)
- Modern vanilla JS is powerful (ES6+, fetch, template literals)
- Easy to integrate with Python backend

❌ **React would be overkill:**
- Don't need complex nested component state
- No plans for real-time collaboration
- Not sharing UI components across apps
- Adds build complexity for minimal benefit

**Tailwind CSS:**
- Using **CDN** (no build step required)
- Rapid UI development with utility classes
- Consistent styling across the app
- Dark/light theme support

### Database: SQLite

- **Lightweight** - Single file per project
- **ACID compliant** - Data integrity guaranteed
- **Built into Python** - No external dependencies
- **Fast** - More than enough for local PM tool
- **Portable** - Easy backups and sharing

---

## Directory Structure

```
ai-pm-gui/
├── backend/
│   ├── app.py              # FastAPI server with all endpoints
│   ├── database.py         # SQLite connection & queries
│   ├── models.py           # Pydantic models (request/response)
│   └── schema.sql          # Database schema
│
├── frontend/
│   ├── index.html          # Main UI (single-page app)
│   ├── css/
│   │   └── styles.css      # Tailwind + custom styles
│   └── js/
│       ├── app.js          # Main application logic
│       ├── api.js          # Backend API client
│       └── components.js   # Reusable UI builders
│
├── migrations/
│   └── import_roadmap.py   # Import from ROADMAP.md → SQLite
│
├── run.py                  # Main entry point
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Database Schema

```sql
CREATE TABLE phases (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT CHECK(status IN ('pending', 'active', 'completed')),
    order_num INTEGER,
    description TEXT
);

CREATE TABLE tickets (
    id TEXT PRIMARY KEY,          -- e.g., 'FEAT-073'
    phase_id INTEGER,
    title TEXT NOT NULL,
    status TEXT CHECK(status IN ('todo', 'in_progress', 'done', 'blocked')),
    priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'critical')),
    estimate_hours TEXT,          -- e.g., '3-4h'
    tags TEXT,                    -- JSON array
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (phase_id) REFERENCES phases(id)
);

CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    ticket_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    entry TEXT,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
);
```

---

## Features

### Phase 1: Core Functionality
- ✅ Kanban board view (phases as columns, tickets as draggable cards)
- ✅ CRUD operations (create, edit, delete tickets & phases)
- ✅ Search/filter (by status, tag, text)
- ✅ Import from existing ROADMAP.md files
- ✅ Basic REST API with auto-generated docs

### Phase 2: Polish
- 📊 Progress metrics (% complete per phase)
- 📝 Session logging (daily work log)
- 📤 Export to ROADMAP.md (regenerate from DB)
- 🏷️ Tag management UI
- ⌨️ Keyboard shortcuts

### Phase 3: Nice-to-Have
- 🌓 Dark/light theme toggle
- ⏱️ Time tracking per ticket
- 📈 Burndown charts
- 🔔 Reminders/notifications
- 📋 Templates for common ticket types

---

## Usage

### Setup (One-Time)

1. **Install dependencies:**
   ```bash
   cd D:\Claude\ai-pm-gui
   pip install -r requirements.txt
   ```

2. **Verify installation:**
   ```bash
   python run.py --help
   ```

### Per-Project Setup

1. **Create launcher script** by copying the template:

```bash
# From ai-pm-gui directory
cd D:\Claude\ai-pm-gui
copy run-pm-template.py D:\Claude\YourProject\ai-tasks\run-pm.py

# Or on Linux/Mac
cp run-pm-template.py D:\Claude\YourProject\ai-tasks/run-pm.py
```

The launcher automatically:
- ✅ **Auto-updates** itself when the template changes
- ✅ Creates project-specific database (`pm.db`)
- ✅ Supports both GUI and CLI modes

**Manual Setup (Alternative):**

If you prefer to create manually, copy the contents of `run-pm-template.py` to `D:\Claude\YourProject\ai-tasks\run-pm.py`

2. **Import existing ROADMAP.md** (optional):
   ```bash
   cd D:\Claude\YourProject\ai-tasks
   python run-pm.py --import ROADMAP.md
   ```

3. **Launch the GUI:**
   ```bash
   python run-pm.py
   ```
   - Opens browser to `http://localhost:8000`
   - Backend API docs at `http://localhost:8000/docs`

### CLI Commands

Manage tickets from the command line without launching the GUI:

```bash
# Add a ticket
python run-pm.py add --type FEAT --number 73 --title "Add dark mode" --priority high

# List tickets with filters
python run-pm.py list --status todo
python run-pm.py list --priority high --format list
python run-pm.py list --tag backend --format json

# Show ticket details
python run-pm.py show FEAT-073

# Update a ticket
python run-pm.py update FEAT-073 --status in_progress --priority critical

# Delete a ticket
python run-pm.py delete FEAT-073 --yes

# Interactive quick-add (prompts for all fields)
python run-pm.py quick-add
```

**Available Commands:**
- `add` - Create a new ticket
- `list` - List tickets with optional filters
- `show` - Show detailed ticket information
- `update` - Update an existing ticket
- `delete` - Delete a ticket
- `quick-add` - Interactive ticket creation

**List Formats:**
- `table` (default) - Tabular view
- `list` - Detailed list with descriptions
- `json` - JSON output for scripts

### Python API

Use the Python API for programmatic ticket management:

```python
from backend.api_client import TicketManager, PhaseManager, ProjectManager

# Initialize with database path
tm = TicketManager("ai-tasks/pm.db")

# Create a ticket
ticket = tm.create_ticket(
    ticket_id="FEAT-073",
    title="Add dark mode",
    priority="high",
    tags=["frontend", "ui"],
    description="Implement dark theme toggle"
)

# List tickets with filters
todo_tickets = tm.list_tickets(status="todo", priority="high")

# Update a ticket
tm.update_ticket("FEAT-073", status="in_progress")

# Get ticket details
ticket = tm.get_ticket("FEAT-073")

# Delete a ticket
tm.delete_ticket("FEAT-073")

# Auto-generate ticket IDs
next_num = tm.get_next_ticket_number("FEAT")
new_id = f"FEAT-{next_num:03d}"  # "FEAT-074"
```

**Available Managers:**
- `TicketManager` - Manage tickets
- `PhaseManager` - Manage phases
- `LogManager` - Manage session logs
- `ProjectManager` - Unified API for all operations

See `backend/api_client.py` for full API documentation.

---

## Updating Launchers

### Automatic Updates

Launchers automatically check for updates on every run. When the template changes:
1. Launcher detects hash mismatch
2. Creates backup (`.py.bak`)
3. Copies new template
4. Restarts seamlessly

**You don't need to do anything** - updates happen automatically!

### Manual Bulk Update

To update all project launchers at once:

```bash
cd D:\Claude\ai-pm-gui
python update-all-launchers.py

# Or preview changes first
python update-all-launchers.py --dry-run
```

This finds all projects in `D:\Claude\` and updates their launchers from the template.

---

## Migration Strategy

### From Current System

**Keep as reference:**
- `ai-tasks/guide.md` - Logging standards (still useful)
- `ai-tasks/pm.md` - Project management templates (still useful)

**Import to database:**
- `ai-tasks/ROADMAP.md` → Parse into `phases` and `tickets` tables
- Session folders → Import into `logs` table (optional)

**Workflow going forward:**
1. Use **GUI** for day-to-day PM tasks
2. **Export to ROADMAP.md** when needed (for sharing, GitHub, etc.)
3. Keep `guide.md` and `pm.md` as documentation

**Advantages:**
- 🔍 Search across all tickets/phases/logs
- 📊 Visual progress tracking
- 🏷️ Tag-based organization
- ⚡ Faster than editing markdown files
- 📈 Metrics and insights
- 🗄️ Structured data (queryable)

---

## API Endpoints

**Phases:**
- `GET /api/phases` - List all phases
- `POST /api/phases` - Create phase
- `PUT /api/phases/{id}` - Update phase
- `DELETE /api/phases/{id}` - Delete phase

**Tickets:**
- `GET /api/tickets` - List tickets (with filters)
- `GET /api/tickets/{id}` - Get ticket details
- `POST /api/tickets` - Create ticket
- `PUT /api/tickets/{id}` - Update ticket
- `DELETE /api/tickets/{id}` - Delete ticket
- `PATCH /api/tickets/{id}/move` - Move to different phase/status

**Logs:**
- `GET /api/logs` - List logs (with filters)
- `POST /api/logs` - Add log entry
- `GET /api/logs/today` - Today's work log

**Utilities:**
- `GET /api/stats` - Project statistics
- `GET /api/export/markdown` - Export to ROADMAP.md format
- `POST /api/import/markdown` - Import from ROADMAP.md

**Full API docs:** `http://localhost:8000/docs` (auto-generated by FastAPI)

---

## Development

### Running Locally

```bash
cd D:\Claude\ai-pm-gui

# Set test DB path
set PM_DB_PATH=test.db
set PM_PROJECT_NAME=TestProject

# Run server
python run.py

# Or with auto-reload (dev mode)
uvicorn backend.app:app --reload
```

### Testing

```bash
# Run tests (once implemented)
pytest

# Check API endpoints
curl http://localhost:8000/api/phases
```

---

## Future Enhancements

- **Multi-project dashboard** - View all projects at once
- **Cross-project search** - Find tickets across all projects
- **Time tracking** - Pomodoro integration
- **GitHub integration** - Sync with GitHub Issues/Projects
- ✅ **CLI commands** - Quick ticket creation from terminal (IMPLEMENTED)
- **Mobile app** - React Native companion app
- **Collaboration** - Optional cloud sync (privacy-first)
- **Batch operations** - Import/export CSV, bulk updates
- **CLI auto-completion** - Bash/Zsh completion scripts

---

## License

TBD

---

## Credits

Built for managing AI-assisted development projects across the `D:\Claude\` workspace.

**Version:** 0.2.0-alpha
**Last Updated:** 2025-12-02
