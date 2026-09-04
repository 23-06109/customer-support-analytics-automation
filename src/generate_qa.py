import csv
import random
from pathlib import Path


random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

tickets_file = RAW_DATA_DIR / "tickets.csv"
qa_file = RAW_DATA_DIR / "qa_evaluations.csv"


# Load closed tickets only
closed_tickets = []

with open(tickets_file, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        if row["status"] == "Closed":
            closed_tickets.append(row)


defect_categories = [
    "None",
    "Process Compliance",
    "Incorrect Information",
    "Incomplete Resolution",
    "Communication",
    "Documentation"
]


evaluations = []


# Evaluate around 60% of closed tickets
sample_size = int(len(closed_tickets) * 0.60)

sampled_tickets = random.sample(
    closed_tickets,
    sample_size
)


for evaluation_number, ticket in enumerate(
    sampled_tickets,
    start=1
):

    qa_score = random.choices(
        population=[
            random.randint(90, 100),
            random.randint(80, 89),
            random.randint(70, 79),
            random.randint(50, 69)
        ],
        weights=[45, 30, 15, 10],
        k=1
    )[0]

    if qa_score >= 90:
        defect_category = random.choices(
            defect_categories,
            weights=[80, 5, 4, 4, 4, 3],
            k=1
        )[0]

    else:
        defect_category = random.choice(
            defect_categories[1:]
        )

    critical_error = (
        qa_score < 70
        and random.random() < 0.35
    )

    passed_qa = qa_score >= 80 and not critical_error

    evaluation = {
        "evaluation_id": f"QA{evaluation_number:04d}",
        "ticket_id": ticket["ticket_id"],
        "agent_id": ticket["agent_id"],
        "qa_score": qa_score,
        "defect_category": defect_category,
        "critical_error": critical_error,
        "passed_qa": passed_qa
    }

    evaluations.append(evaluation)


with open(qa_file, "w", newline="", encoding="utf-8") as file:

    fieldnames = [
        "evaluation_id",
        "ticket_id",
        "agent_id",
        "qa_score",
        "defect_category",
        "critical_error",
        "passed_qa"
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(evaluations)


print(f"Created {len(evaluations)} QA evaluations.")
print(f"Saved to: {qa_file}")