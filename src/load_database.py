import csv
import getpass
from pathlib import Path

import psycopg


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

DB_NAME = "customer_support_analytics"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"


password = getpass.getpass("PostgreSQL password: ")


with psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=password,
    host=DB_HOST,
    port=DB_PORT
) as connection:

    with connection.cursor() as cursor:

        print("Connected to PostgreSQL.")

        # Clear existing data in the correct dependency order
        cursor.execute("""
            TRUNCATE TABLE
                qa_evaluations,
                tickets,
                agents
            RESTART IDENTITY;
        """)

        # -------------------------
        # Load agents
        # -------------------------

        agents_file = RAW_DATA_DIR / "agents.csv"

        with open(agents_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                cursor.execute("""
                    INSERT INTO agents (
                        agent_id,
                        agent_name,
                        team,
                        status
                    )
                    VALUES (%s, %s, %s, %s);
                """, (
                    row["agent_id"],
                    row["agent_name"],
                    row["team"],
                    row["status"]
                ))

        print("Agents loaded.")

        # -------------------------
        # Load tickets
        # -------------------------

        tickets_file = RAW_DATA_DIR / "tickets.csv"

        with open(tickets_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:

                closed_at = row["closed_at"] or None

                resolution_hours = (
                    int(row["resolution_hours"])
                    if row["resolution_hours"]
                    else None
                )

                sla_breached = (
                    row["sla_breached"] == "True"
                )

                cursor.execute("""
                    INSERT INTO tickets (
                        ticket_id,
                        agent_id,
                        category,
                        channel,
                        priority,
                        status,
                        opened_at,
                        closed_at,
                        sla_target_hours,
                        age_hours,
                        resolution_hours,
                        sla_breached
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s
                    );
                """, (
                    row["ticket_id"],
                    row["agent_id"],
                    row["category"],
                    row["channel"],
                    row["priority"],
                    row["status"],
                    row["opened_at"],
                    closed_at,
                    int(row["sla_target_hours"]),
                    int(row["age_hours"]),
                    resolution_hours,
                    sla_breached
                ))

        print("Tickets loaded.")

        # -------------------------
        # Load QA evaluations
        # -------------------------

        qa_file = RAW_DATA_DIR / "qa_evaluations.csv"

        with open(qa_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:

                critical_error = (
                    row["critical_error"] == "True"
                )

                passed_qa = (
                    row["passed_qa"] == "True"
                )

                cursor.execute("""
                    INSERT INTO qa_evaluations (
                        evaluation_id,
                        ticket_id,
                        agent_id,
                        qa_score,
                        defect_category,
                        critical_error,
                        passed_qa
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s
                    );
                """, (
                    row["evaluation_id"],
                    row["ticket_id"],
                    row["agent_id"],
                    int(row["qa_score"]),
                    row["defect_category"],
                    critical_error,
                    passed_qa
                ))

        print("QA evaluations loaded.")

        # -------------------------
        # Verify row counts
        # -------------------------

        cursor.execute("SELECT COUNT(*) FROM agents;")
        agent_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tickets;")
        ticket_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM qa_evaluations;")
        qa_count = cursor.fetchone()[0]

        print()
        print("Database load complete.")
        print(f"Agents: {agent_count}")
        print(f"Tickets: {ticket_count}")
        print(f"QA evaluations: {qa_count}")