import sqlite3
import json

conn = sqlite3.connect('ai-tasks/pm.db')
cursor = conn.cursor()

# Show all tickets with details
print("\n" + "="*100)
print("TICKETS IN PM.DB")
print("="*100)
cursor.execute('SELECT id, title, status, priority, estimate_hours, tags, description, created_at FROM tickets ORDER BY id')
tickets = cursor.fetchall()

for ticket in tickets:
    ticket_id, title, status, priority, estimate, tags, description, created = ticket
    print(f"\n[{ticket_id}] {title}")
    print(f"  Status: {status} | Priority: {priority} | Estimate: {estimate}")
    if tags:
        try:
            tag_list = json.loads(tags)
            print(f"  Tags: {', '.join(tag_list)}")
        except:
            print(f"  Tags: {tags}")
    if description:
        desc_preview = description[:100] + "..." if len(description) > 100 else description
        print(f"  Description: {desc_preview}")
    print(f"  Created: {created}")

print(f"\n{'='*100}")
print(f"Total tickets: {len(tickets)}")
print(f"Done: {len([t for t in tickets if t[2] == 'done'])}")
print(f"In Progress: {len([t for t in tickets if t[2] == 'in_progress'])}")
print(f"Todo: {len([t for t in tickets if t[2] == 'todo'])}")

# Show phases
print(f"\n{'='*100}")
print("PHASES")
print("="*100)
cursor.execute('SELECT * FROM phases')
phases = cursor.fetchall()
if phases:
    for phase in phases:
        print(phase)
else:
    print("No phases defined")

# Show log count
cursor.execute('SELECT COUNT(*) FROM logs')
log_count = cursor.fetchone()[0]
print(f"\n{'='*100}")
print(f"LOGS: {log_count} entries in database")
print("="*100)

conn.close()
