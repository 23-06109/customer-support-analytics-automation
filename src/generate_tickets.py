import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

agents_file = RAW_DATA_DIR / "agents.csv"
tickets_file = RAW_DATA_DIR / "tickets.csv"

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

historical_start = datetime(2026, 1, 1)


for ticket_number in range(1, 501):

    priority = random.choices(
        priorities,
        weights=priority_weights,
        k=1
    )[0]

    sla_hours = sla_targets[priority]

    status = random.choices(
        ["Closed", "Open"],
        weights=[82, 18],
        k=1
    )[0]

    if status == "Closed":

        # Historical closed tickets
        opened_at = historical_start + timedelta(
            days=random.randint(0, 230),
            hours=random.randint(0, 23)
        )

        # About 75% resolve within SLA
        if random.random() < 0.75:
            resolution_hours = random.randint(
                1,
                sla_hours
            )
        else:
            resolution_hours = random.randint(
                sla_hours + 1,
                sla_hours + 72
            )

        closed_at = opened_at + timedelta(
            hours=resolution_hours
        )

        age_hours = resolution_hours

        sla_breached = (
            resolution_hours > sla_hours
        )

    else:

        # Open backlog is kept recent and realistic
        backlog_type = random.choices(
            [
                "On Track",
                "Breached",
                "Stale"
            ],
            weights=[
                45,
                40,
                15
            ],
            k=1
        )[0]

        if backlog_type == "On Track":

            age_hours = random.randint(
                1,
                max(1, sla_hours - 1)
            )

        elif backlog_type == "Breached":

            age_hours = random.randint(
                sla_hours + 1,
                sla_hours + 48
            )

        else:

            age_hours = random.randint(
                sla_hours + 49,
                sla_hours + 168
            )

        opened_at = REPORT_DATE - timedelta(
            hours=age_hours
        )

        closed_at = ""
        resolution_hours = ""

        sla_breached = (
            age_hours > sla_hours
        )

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