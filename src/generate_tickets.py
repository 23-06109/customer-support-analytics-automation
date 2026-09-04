import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

agents_file = RAW_DATA_DIR / "agents.csv"
tickets_file = RAW_DATA_DIR / "tickets.csv"

# Fixed reporting date keeps the analysis reproducible
REPORT_DATE = datetime(2026, 9, 1, 12, 0)


# Load agent IDs
agent_ids = []

with open(agents_file, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        agent_ids.append(row["agent_id"])


categories = [
    "Billing",
    "Technical Support",
    "Account Access",
    "Product Inquiry",
    "Refund Request"
]

channels = [
    "Email",
    "Chat",
    "Phone"
]

priorities = [
    "Low",
    "Medium",
    "High",
    "Critical"
]

priority_weights = [
    35,
    40,
    20,
    5
]

sla_targets = {
    "Low": 72,
    "Medium": 48,
    "High": 24,
    "Critical": 8
}


tickets = []

start_date = datetime(2026, 1, 1)


for ticket_number in range(1, 501):

    priority = random.choices(
        priorities,
        weights=priority_weights,
        k=1
    )[0]

    opened_at = start_date + timedelta(
        days=random.randint(0, 242),
        hours=random.randint(0, 23)
    )

    status = random.choices(
        ["Closed", "Open"],
        weights=[80, 20],
        k=1
    )[0]

    sla_hours = sla_targets[priority]

    if status == "Closed":

        # Most tickets resolve within SLA,
        # while some deliberately become breaches.
        if random.random() < 0.75:
            resolution_hours = random.randint(1, sla_hours)
        else:
            resolution_hours = random.randint(
                sla_hours + 1,
                sla_hours + 72
            )

        closed_at = opened_at + timedelta(hours=resolution_hours)

        age_hours = resolution_hours
        sla_breached = age_hours > sla_hours

    else:

        closed_at = ""
        resolution_hours = ""

        age_hours = int(
            (REPORT_DATE - opened_at).total_seconds() / 3600
        )

        sla_breached = age_hours > sla_hours

    ticket = {
        "ticket_id": f"TKT{ticket_number:04d}",
        "agent_id": random.choice(agent_ids),
        "category": random.choice(categories),
        "channel": random.choice(channels),
        "priority": priority,
        "status": status,
        "opened_at": opened_at.strftime("%Y-%m-%d %H:%M"),
        "closed_at": (
            closed_at.strftime("%Y-%m-%d %H:%M")
            if closed_at
            else ""
        ),
        "sla_target_hours": sla_hours,
        "age_hours": age_hours,
        "resolution_hours": resolution_hours,
        "sla_breached": sla_breached
    }

    tickets.append(ticket)


with open(tickets_file, "w", newline="", encoding="utf-8") as file:

    fieldnames = [
        "ticket_id",
        "agent_id",
        "category",
        "channel",
        "priority",
        "status",
        "opened_at",
        "closed_at",
        "sla_target_hours",
        "age_hours",
        "resolution_hours",
        "sla_breached"
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(tickets)


print(f"Created {len(tickets)} tickets.")
print(f"Saved to: {tickets_file}")