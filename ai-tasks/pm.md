# Project Management & Task Tracking System

**Shared across all projects using AI Project Manager GUI**

This file defines the PM (Project Manager) persona and logging system used by Claude Code when breaking down features into actionable tickets and tracking progress.

---

## Quick Start with AI PM GUI

### Using This System

1. **Multiple Access Methods** - Use GUI for visual management, CLI for quick operations, or Python API for automation
2. **Log Files Still Matter** - Create `.log` files in ticket folders for detailed session tracking
3. **Ticket Templates** - Use templates below when creating tickets
4. **Folder Structure** - Organize work in timestamped feature folders

### Accessing the GUI

```bash
cd D:\Claude\YourProject\ai-tasks
python run-pm.py
```

Visit `http://localhost:8000` for:
- 📋 Kanban board (drag & drop tickets)
- 📋 List view (tabular data)
- 📊 Stats view (progress tracking)

### Using CLI Commands (Fast Operations)

```bash
# Quick add a ticket (no GUI needed)
python run-pm.py add --type FEAT --number 5 --title "Add feature X" --priority high

# List tickets with filters
python run-pm.py list --status todo --priority high
python run-pm.py list --tag backend --format list

# Show ticket details
python run-pm.py show FEAT-005

# Update a ticket
python run-pm.py update FEAT-005 --status in_progress

# Delete a ticket
python run-pm.py delete FEAT-005 --yes

# Interactive mode (prompts for all fields)
python run-pm.py quick-add
```

**CLI Benefits:**
- ⚡ **Faster** - No need to launch GUI for simple operations
- 📝 **Scriptable** - Use in automation/CI/CD pipelines
- 🔍 **Flexible output** - table, list, or json formats

**Available Commands:**
- `add` - Create a new ticket
- `list` - List tickets with optional filters (--status, --priority, --tag, --search)
- `show` - Show detailed ticket information
- `update` - Update an existing ticket
- `delete` - Delete a ticket
- `quick-add` - Interactive ticket creation with prompts

### Using Python API (Automation)

```python
from backend.api_client import TicketManager, PhaseManager, ProjectManager

# Initialize with database path
tm = TicketManager("ai-tasks/pm.db")

# Create a ticket
ticket = tm.create_ticket(
    ticket_id="FEAT-073",
    title="Implement feature X",
    priority="high",
    tags=["backend", "api"],
    description="Detailed description here",
    estimate_hours="3-4h"
)

# List tickets with filters
todo_tickets = tm.list_tickets(status="todo", priority="high")
backend_tickets = tm.list_tickets(tag="backend")

# Update a ticket
tm.update_ticket("FEAT-073", status="in_progress", priority="critical")

# Get ticket details
ticket = tm.get_ticket("FEAT-073")
print(f"{ticket.title} - {ticket.status}")

# Delete a ticket
tm.delete_ticket("FEAT-073")

# Auto-generate ticket IDs
next_num = tm.get_next_ticket_number("FEAT")
new_ticket_id = f"FEAT-{next_num:03d}"  # "FEAT-074"
```

**API Benefits:**
- 🤖 **Automation** - Import from GitHub, Jira, etc.
- 📊 **Reporting** - Generate custom reports programmatically
- 🔗 **Integration** - Connect with CI/CD, monitoring tools

**Available Managers:**
- `TicketManager` - Full CRUD for tickets
- `PhaseManager` - Full CRUD for phases
- `LogManager` - Session log management
- `ProjectManager` - Unified API combining all managers

See `backend/api_client.py` for complete API documentation.

---

## Core Philosophy

### Guiding Principles
1. **KISS (Keep It Simple Stupid)** - Break complex features into simple, atomic tasks
2. **Logs are Primary, GUI is Visual** - Detailed logs in files, visual overview in GUI
3. **Clear Acceptance Criteria** - Every ticket must have explicit success criteria
4. **Dependencies First** - Identify and sequence dependencies properly
5. **Database First** - Always start with data model changes before application logic
6. **Test as You Go** - Include testing steps in every ticket
7. **Security by Default** - Never skip security considerations
8. **Future-Proof but Pragmatic** - Consider future needs but deliver working features NOW
9. **Session Continuity** - Always maintain context across sessions with detailed logs
10. **Git Commit After Each Feature** - Commit and push after completing each major feature ticket

### Git Workflow Best Practice
**⚠️ IMPORTANT:** After completing each feature ticket (FEAT-###), always:
1. Review changed files with `git status`
2. Stage changes with `git add`
3. Create descriptive commit message (see format below)
4. Push to remote: `git push origin master`

**Commit Message Format:**
```
feat: [FEAT-###] Brief description

- Key changes made
- Tests added/passing
- Any breaking changes

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

**When to Commit:**
- ✅ After completing each FEAT ticket
- ✅ After completing a group of related TASK tickets
- ✅ After fixing critical BUGs
- ✅ Before switching to a different feature area
- ⚠️ **Always remind user to commit/push before ending session**

---

## Folder Structure

```
ai-tasks/
├── pm.db                                        ← SQLite database (GUI data)
├── run-pm.py                                    ← GUI launcher
├── guide.md                                     ← Logging reference
└── <YYMMDD-HHMM_{feature-name}>/               ← Feature folder (timestamp + name)
    ├── <TICKET-ID>-{short-description}/
    │   ├── <TICKET-ID>-{short-description}.md  ← Initial ticket spec (template)
    │   ├── YYMMDD-HHMMSS.log                   ← First work session
    │   ├── YYMMDD-HHMMSS.log                   ← Second work session
    │   ├── YYMMDD-HHMMSS.log                   ← Additional sessions
    │   └── notes.md                            ← Optional: Persistent notes, decisions
    └── <TICKET-ID>-{short-description}/
        ├── <TICKET-ID>-{short-description}.md
        └── *.log files
```

### Example Structure
```
ai-tasks/
├── pm.db                                        ← AI PM GUI database
├── run-pm.py                                    ← Launcher script
├── 251120-1134_stripe-onboarding/              ← Feature started Nov 20, 2025 at 11:34 AM
│   ├── FEAT-001-checkout-session/
│   │   ├── FEAT-001-checkout-session.md
│   │   ├── 251120-143022.log
│   │   ├── 251120-160845.log
│   │   └── notes.md
│   └── FEAT-002-webhook-handler/
│       ├── FEAT-002-webhook-handler.md
│       └── 251120-144530.log
└── 251121-0945_payment-flows/                  ← Feature started Nov 21, 2025 at 09:45 AM
    ├── BUG-001-payment-timeout/
    │   ├── BUG-001-payment-timeout.md
    │   └── 251121-120000.log
    └── FEAT-003-refund-api/
        ├── FEAT-003-refund-api.md
        └── 251121-130000.log
```

---

## Ticket Naming Convention

### Format: `[TYPE-###]`

**Ticket Types:**
- `FEAT` - Feature (new functionality)
- `BUG` - Bug fix
- `TASK` - General task, refactoring, chores
- `HOTFIX` - Urgent production fix
- `RESEARCH` - Investigation, proof-of-concept, discovery
- `INFRA` - Infrastructure, deployment, DevOps

**Examples:**
- `[FEAT-001]` - First feature ticket
- `[BUG-042]` - Bug ticket #42
- `[TASK-015]` - Task ticket #15
- `[RESEARCH-003]` - Research ticket #3

**Feature Folder Names:**
Use timestamp + descriptive name format: `YYMMDD-HHMM_{feature-name}`
- `251120-1134_stripe-onboarding/` - Feature started November 20, 2025 at 11:34 AM
- `251121-0945_payment-flows/` - Feature started November 21, 2025 at 09:45 AM
- `251122-1520_user-auth/` - Feature started November 22, 2025 at 3:20 PM

---

## Ticket Template

Create tickets in the GUI or as `<TICKET-ID>.md` files with this structure:

```markdown
# [TYPE-###] Ticket Title

## Priority
- [P0/P1/P2] - Critical/High/Medium

## Estimated Time
- X hours

## Dependencies
- List of tickets that must be completed first (e.g., FEAT-001, BUG-005)
- External dependencies (APIs, services, libraries, etc.)

## Description
Clear, concise description of what needs to be built.

## Technical Approach
High-level technical implementation details:
- Database changes
- Backend changes
- Frontend changes
- Infrastructure changes

## Acceptance Criteria
- [ ] Specific, testable requirement 1
- [ ] Specific, testable requirement 2
- [ ] Specific, testable requirement 3

## Implementation Steps
1. Step-by-step implementation guide
2. Each step should be completable in < 30 minutes
3. Include file paths and specific changes

## Testing Steps
1. How to verify the feature works
2. Edge cases to test
3. Manual testing instructions
4. Automated test requirements

## Security Considerations
- Authentication/Authorization checks
- Input validation
- Data sanitization
- Rate limiting (if applicable)
- SQL injection prevention
- XSS prevention
- CORS configuration

## Rollback Plan
- How to undo changes if something goes wrong
- Database migration rollback (if applicable)

## Notes
- Additional context
- Known limitations
- Future improvements
```

---

## Log File Format

### Log File Naming
**Format:** `YYMMDD-HHMMSS.log`

**Examples:**
- `241111-143022.log` - Nov 11, 2024, 2:30:22 PM
- `241111-090000.log` - Nov 11, 2024, 9:00:00 AM

### Log File Structure

Every `.log` file must include these sections:

```markdown
# AI Session Log - YYYY-MM-DD HH:MM:SS

## Ticket Reference
[TYPE-###] Ticket title

## Task Summary
Brief description of current objective for this session.

## Previous Session Context
What was completed in previous sessions (reference prior .log files if applicable).
If this is the first session, state: "Initial session - no prior context."

## Current Working Directory
The primary directory for this work (e.g., `/backend/nodejs/`, `/frontend/react/`)

## Actions Taken
1. ✅ Completed action 1
2. ✅ Completed action 2
3. 🔄 In-progress action 3
4. ❌ Failed action 4 (explain why)

## Current Status
What's happening RIGHT NOW. What's working, what's not.

## Next Steps
- [ ] Planned action 1
- [ ] Planned action 2
- [ ] Planned action 3

## Issues/Blockers
- Any problems encountered
- Decisions that need to be made
- Questions that came up

## Files Changed
List of files modified during this session:
- `path/to/file1.js` - Description of change
- `path/to/file2.tsx` - Description of change

## Testing Results
- ✅ Test 1 passed
- ❌ Test 2 failed (reason)
- 🔄 Test 3 in progress

## Notes
- Additional context
- Lessons learned
- Technical debt created
- Future refactoring needed
```

### Status Indicators

Use these emojis consistently:
- ✅ - Completed, success, passed
- ❌ - Failed, blocked, error
- 🔄 - In progress, ongoing
- ⚠️ - Warning, caution, needs attention
- 📝 - Note, documentation, decision
- 🔍 - Investigation, research, debugging
- 🚀 - Deployed, shipped, released

---

## Feature Breakdown Guidelines

### 1. Database Changes First
Always create separate tickets for database migrations:
- `[FEAT-001]` - Database migration
- `[FEAT-002]` - Backend API
- `[FEAT-003]` - Frontend UI

### 2. Atomic Tasks
Each ticket should:
- Be completable in 0.5-4 hours
- Have a single, clear objective
- Be independently testable
- Not require multiple Claude sessions to complete (ideally)

### 3. Dependency Sequencing
- Infrastructure before application
- Database before backend
- Backend before frontend
- Core functionality before edge cases

### 4. Testing Requirements
Every ticket must include:
- Unit test expectations (where applicable)
- Integration test steps
- Manual testing checklist
- Edge case scenarios

### 5. Security Checklist (for every ticket)
- [ ] User authentication required?
- [ ] Authorization/permissions checked?
- [ ] Input validation implemented?
- [ ] SQL injection prevented? (use parameterized queries)
- [ ] XSS prevention? (sanitize outputs)
- [ ] Rate limiting needed?
- [ ] Sensitive data encrypted?
- [ ] CORS configured properly?
- [ ] API keys/secrets in environment variables (not hardcoded)?

---

## PM Workflow

### When Breaking Down a Feature:

1. **Understand the Requirement**
   - Read the feature request thoroughly
   - Identify core functionality vs. nice-to-haves
   - Clarify ambiguities with the user before creating tickets

2. **Identify Dependencies**
   - Database schema changes
   - External services (Stripe, payment processors, APIs, etc.)
   - Infrastructure (Redis, queues, CDN, etc.)
   - Other features or tickets

3. **Create Ticket Sequence**
   - Start with infrastructure/database (INFRA, TASK)
   - Build backend APIs (FEAT)
   - Create frontend UI (FEAT)
   - Add polish/edge cases (TASK)
   - Fix issues that arise (BUG)

4. **Estimate Time**
   - Be realistic
   - Account for testing time
   - Include debugging buffer (15-20%)

5. **Write Clear Tickets**
   - Use the ticket template
   - Include file paths
   - Provide code snippets where helpful
   - Link to relevant documentation

6. **Review for Completeness**
   - Can a developer complete this without additional context?
   - Are all edge cases covered?
   - Is security addressed?
   - Is rollback possible?

---

## Quality Gates

Before marking a ticket as complete (in the final .log file):

- [ ] Code is written and tested
- [ ] All acceptance criteria met
- [ ] Security considerations addressed
- [ ] No regressions introduced
- [ ] Documentation updated (if needed)
- [ ] Git committed with clear message
- [ ] Changes deployed to dev environment (if applicable)
- [ ] Manual testing completed
- [ ] All .log files updated with final status
- [ ] Ticket marked as "Done" in AI PM GUI

---

## Anti-Patterns to Avoid

❌ **DON'T:**
- Create tickets that take > 4 hours
- Skip database migrations (just modify schema directly)
- Ignore security in early tickets ("we'll add it later")
- Create vague acceptance criteria ("make it work")
- Skip testing steps
- Forget about error handling
- Ignore mobile responsiveness
- Hardcode API keys or secrets
- Leave TODO comments without tickets

✅ **DO:**
- Break large features into 1-2 hour chunks
- Always create migration files for schema changes
- Include security from day one
- Write specific, measurable acceptance criteria
- Include comprehensive testing steps
- Handle errors gracefully from the start
- Test on mobile viewports
- Use environment variables for all config
- Create tickets for all TODO items

---

## Session Continuity Best Practices

### Starting a New Session
1. Create new `YYMMDD-HHMMSS.log` file in ticket folder
2. Reference previous `.log` files in "Previous Session Context"
3. Summarize what's complete and what's next
4. Copy over any unresolved blockers

### Ending a Session
1. Update "Current Status" with final state
2. Update "Next Steps" with clear action items
3. List all files changed
4. Note any blockers or decisions needed
5. If ticket is complete:
   - Mark all acceptance criteria in ticket `.md` file
   - Update ticket status to "Done" in AI PM GUI

### Resuming After Interruption
1. Read the most recent `.log` file
2. Create new `.log` file with timestamp
3. Use git diff format to show continuation
4. Acknowledge the gap in "Previous Session Context"

---

## Using AI PM GUI, CLI, and API

### Creating Tickets

**Via GUI:**
1. Click **+ Ticket** button
2. Fill in ticket ID (e.g., `FEAT-073`)
3. Add title, description, priority, estimate
4. Assign to phase (if applicable)
5. Add tags for organization

**Via CLI (Faster for quick tickets):**
```bash
# Manual ticket ID
python run-pm.py add --type FEAT --number 73 --title "Add feature" --priority high

# Interactive mode (auto-generates ticket ID)
python run-pm.py quick-add
```

**Via Python API (For automation):**
```python
tm = TicketManager("ai-tasks/pm.db")
next_num = tm.get_next_ticket_number("FEAT")
tm.create_ticket(f"FEAT-{next_num:03d}", "Add feature", priority="high")
```

### Managing Work

**GUI Options:**
1. **Kanban View** - Drag tickets between columns (Todo, In Progress, Blocked, Done)
2. **List View** - See all tickets in table format
3. **Stats View** - Track progress metrics

**CLI Options:**
```bash
# List tickets with filters
python run-pm.py list --status todo --priority high

# Update ticket status
python run-pm.py update FEAT-073 --status in_progress

# Show ticket details
python run-pm.py show FEAT-073
```

**API Options:**
```python
# List and filter
tickets = tm.list_tickets(status="todo", priority="high")

# Update ticket
tm.update_ticket("FEAT-073", status="in_progress")

# Get details
ticket = tm.get_ticket("FEAT-073")
```

### Search & Filter

**GUI:**
- Search by ticket ID, title, or description
- Filter by status, priority, or tags
- Combine filters for precise results

**CLI:**
```bash
python run-pm.py list --status todo --tag backend --search "auth"
python run-pm.py list --format json  # Machine-readable output
```

**API:**
```python
tickets = tm.list_tickets(status="todo", tag="backend", search="auth")
```

### Exporting Data

**Current:**
- Database is in `ai-tasks/pm.db`
- Backup with simple file copy
- CLI JSON output: `python run-pm.py list --format json > tickets.json`

**Future:**
- Export to markdown (planned)
- CSV export (planned)

### When to Use Each Method

**Use GUI when:**
- Visualizing project progress
- Dragging tickets between states
- Creating complex tickets with multiple fields
- Reviewing phase statistics

**Use CLI when:**
- Quick ticket creation from terminal
- Filtering/searching during development
- You're already in the terminal
- Scripting simple operations

**Use Python API when:**
- Automating ticket creation (e.g., from GitHub issues)
- Generating custom reports
- Integrating with CI/CD pipelines
- Building automation scripts

---

## Remember

> "The best ticket is one that Claude can complete in a single session without asking questions."

Make tickets:
- **Clear** - No ambiguity
- **Complete** - All info included
- **Concise** - No unnecessary details
- **Actionable** - Ready to implement immediately

Make logs:
- **Detailed** - Future you needs context
- **Honest** - Document failures and blockers
- **Consistent** - Use emojis and format religiously
- **Continuous** - Never lose session context

---

## Integration with Project Documentation

When working on any project, Claude Code should:

1. **Always reference this file** before starting work on any feature
2. **Choose the right tool** - GUI for visual work, CLI for quick ops, API for automation
3. **Create .log files** for every work session
4. **Follow the folder structure** religiously
5. **Use status emojis** consistently
6. **Maintain session context** across interruptions
7. **Complete quality gates** before marking tickets done
8. **Update ticket status** via GUI, CLI, or API when state changes

This ensures consistency, traceability, and makes it easy to:
- Resume work after breaks
- Onboard new team members
- Audit what was done and why
- Track time spent accurately
- Debug issues by reviewing logs

---

**Last Updated:** 2025-12-02
**Version:** 0.2.0-alpha (with CLI & Python API)
**Managed by:** D:\Claude\ai-pm-gui
**Used by:** All projects in D:\Claude\
