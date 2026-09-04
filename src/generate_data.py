import csv
import random
from pathlib import Path

random.seed(42)


# Find the main project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define where the raw data will be saved
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# Make sure the folder exists
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


teams = ["Team A", "Team B", "Team C", "Team D", "Team E"]

agents = []

for agent_number in range(1, 51):
    agent = {
        "agent_id": f"AG{agent_number:03d}",
        "agent_name": f"Agent {agent_number:02d}",
        "team": random.choice(teams),
        "status": "Active"
    }

    agents.append(agent)


output_file = RAW_DATA_DIR / "agents.csv"

with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["agent_id", "agent_name", "team", "status"]
    )

    writer.writeheader()
    writer.writerows(agents)


print(f"Created {len(agents)} agents.")
print(f"Saved to: {output_file}")