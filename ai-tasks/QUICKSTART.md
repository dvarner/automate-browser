# Quick Start Guide

## First-Time Setup

### 1. Install Dependencies

```bash
cd D:\Claude\ai-pm-gui
python setup.py
```

Or manually:
```bash
pip install -r requirements.txt
```

### 2. Test Locally (Optional)

```bash
python run.py
```

Visit `http://localhost:8000` to see the GUI.

---

## Setting Up a Project

### 1. Create Launcher Script

Copy the launcher template to your project:

```bash
# From D:\Claude\ai-pm-gui
copy run-pm-template.py D:\Claude\YourProject\ai-tasks\run-pm.py

# Or on Linux/Mac
cp run-pm-template.py D:\Claude\YourProject/ai-tasks/run-pm.py
```

**Auto-Update Feature:**
The launcher automatically updates itself when the template changes. No manual updates needed!

### 2. Import Existing ROADMAP.md (Optional)

If you have an existing `ROADMAP.md`:

```bash
cd D:\Claude\YourProject\ai-tasks
python run-pm.py --import ROADMAP.md
```

This creates `pm.db` with all your phases and tickets.

### 3. Launch the GUI

```bash
cd D:\Claude\YourProject\ai-tasks
python run-pm.py
```

Opens browser to `http://localhost:8000` automatically.

---

## Daily Usage

### Start the GUI

```bash
cd D:\Claude\YourProject\ai-tasks
python run-pm.py
```

### Use CLI Commands

Manage tickets without launching the GUI:

```bash
# Quick add a ticket
python run-pm.py add --type FEAT --number 5 --title "Add feature X" --priority high

# List all todo tickets
python run-pm.py list --status todo

# Update a ticket
python run-pm.py update FEAT-005 --status in_progress

# Show ticket details
python run-pm.py show FEAT-005

# Interactive mode (prompts for all fields)
python run-pm.py quick-add
```

**Benefits:**
- ⚡ Faster than launching GUI for simple operations
- 📝 Scriptable (use in automation/CI/CD)
- 🔍 JSON output for parsing (`--format json`)

### View API Docs

Visit `http://localhost:8000/docs` for auto-generated API documentation.

### Change Port

```bash
python run-pm.py --port 8080
```

### Don't Open Browser

```bash
python run-pm.py --no-browser
```

---

## MeetKale Example

The MeetKale project already has a launcher set up:

```bash
cd D:\Claude\MeetKale\ai-tasks
python run-pm.py --import ROADMAP.md  # First time only
python run-pm.py                       # Daily use
```

---

## Features

### Kanban Board
- Drag and drop tickets between columns (Todo, In Progress, Done, Blocked)
- Search and filter by status, priority, or tags
- Color-coded priority badges

### List View
- Tabular view of all tickets
- Quick edit and delete actions
- Sortable columns

### Stats View
- Project progress overview
- Phase completion percentages
- Recent activity log

### Create/Edit
- **+ Phase** button: Create new phases
- **+ Ticket** button: Create new tickets
- Click edit icon on any card to modify

### Dark/Light Theme
- Click moon icon to toggle theme
- Preference saved automatically

---

## Keyboard Shortcuts (Coming Soon)

- `Ctrl+N`: New ticket
- `Ctrl+F`: Focus search
- `/`: Quick command palette

---

## Troubleshooting

### Port Already in Use

```bash
python run-pm.py --port 8001
```

### Database Locked

Close other instances of the app using the same `pm.db`.

### Module Not Found

Make sure you ran `python setup.py` to install dependencies.

---

## Next Steps

1. Customize phases for your workflow
2. Import existing tickets from ROADMAP.md
3. Start tracking progress visually!

For full documentation, see [README.md](README.md).
