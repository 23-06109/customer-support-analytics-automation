import getpass
from pathlib import Path

import psycopg


# =========================================================
# PROJECT SETTINGS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    REPORTS_DIR
    / "management_briefing.txt"
)


# =========================================================
# POSTGRESQL SETTINGS
# =========================================================

DB_NAME = "customer_support_analytics"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"


password = getpass.getpass(
    "PostgreSQL password: "
)


# =========================================================
# QUERY 1 — OVERALL KPIs
# =========================================================

KPI_QUERY = """
SELECT
    COUNT(*) AS total_tickets,

    COUNT(*) FILTER (
        WHERE status = 'Open'
    ) AS open_tickets,

    COUNT(*) FILTER (
        WHERE status = 'Open'
        AND sla_breached = TRUE
    ) AS overdue_open_tickets,

    ROUND(
        AVG(resolution_hours)
        FILTER (
            WHERE status = 'Closed'
        ),
        2
    ) AS avg_resolution_hours,

    ROUND(
        100.0 *
        COUNT(*) FILTER (
            WHERE status = 'Closed'
            AND sla_breached = FALSE
        )
        /
        NULLIF(
            COUNT(*) FILTER (
                WHERE status = 'Closed'
            ),
            0
        ),
        2
    ) AS sla_compliance_pct

FROM tickets;
"""


# =========================================================
# QUERY 2 — TEAM PERFORMANCE
# =========================================================

TEAM_QUERY = """
WITH ticket_metrics AS (

    SELECT
        a.team,

        COUNT(*) AS total_tickets,

        COUNT(*) FILTER (
            WHERE t.status = 'Open'
            AND t.sla_breached = TRUE
        ) AS overdue_open_tickets,

        ROUND(
            100.0 *
            COUNT(*) FILTER (
                WHERE t.status = 'Closed'
                AND t.sla_breached = FALSE
            )
            /
            NULLIF(
                COUNT(*) FILTER (
                    WHERE t.status = 'Closed'
                ),
                0
            ),
            2
        ) AS sla_compliance_pct

    FROM tickets t

    JOIN agents a
        ON t.agent_id = a.agent_id

    GROUP BY a.team
),

qa_metrics AS (

    SELECT
        a.team,

        ROUND(
            AVG(q.qa_score),
            2
        ) AS avg_qa_score,

        ROUND(
            100.0 *
            COUNT(*) FILTER (
                WHERE q.passed_qa = TRUE
            )
            /
            NULLIF(
                COUNT(q.evaluation_id),
                0
            ),
            2
        ) AS qa_pass_rate_pct

    FROM qa_evaluations q

    JOIN agents a
        ON q.agent_id = a.agent_id

    GROUP BY a.team
)

SELECT
    t.team,
    t.total_tickets,
    t.overdue_open_tickets,
    t.sla_compliance_pct,
    q.avg_qa_score,
    q.qa_pass_rate_pct

FROM ticket_metrics t

JOIN qa_metrics q
    ON t.team = q.team;
"""


# =========================================================
# QUERY 3 — CRITICAL OPEN TICKETS
# =========================================================

CRITICAL_QUERY = """
SELECT COUNT(*)

FROM tickets

WHERE status = 'Open'
AND priority = 'Critical'
AND sla_breached = TRUE;
"""


# =========================================================
# GET VERIFIED DATA
# =========================================================

with psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=password,
    host=DB_HOST,
    port=DB_PORT
) as connection:

    with connection.cursor() as cursor:

        cursor.execute(KPI_QUERY)
        kpis = cursor.fetchone()

        cursor.execute(TEAM_QUERY)
        team_rows = cursor.fetchall()

        cursor.execute(CRITICAL_QUERY)
        critical_count = cursor.fetchone()[0]


# =========================================================
# IDENTIFY MANAGEMENT SIGNALS
# =========================================================

total_tickets = kpis[0]
open_tickets = kpis[1]
overdue_open = kpis[2]
avg_resolution = kpis[3]
sla_compliance = kpis[4]


highest_backlog_team = max(
    team_rows,
    key=lambda row: row[2]
)

lowest_sla_team = min(
    team_rows,
    key=lambda row: row[3]
)

lowest_qa_team = min(
    team_rows,
    key=lambda row: row[5]
)


# =========================================================
# BUILD BRIEFING
# =========================================================

briefing = f"""
CUSTOMER SUPPORT MANAGEMENT BRIEFING
=====================================

EXECUTIVE SUMMARY

The operation processed {total_tickets} tickets in the current dataset.

There are currently {open_tickets} open tickets, of which
{overdue_open} have exceeded their SLA target.

Closed-ticket SLA compliance is {sla_compliance}% and the
average resolution time is {avg_resolution} hours.


KEY MANAGEMENT RISKS

1. BACKLOG

{highest_backlog_team[0]} currently has the largest overdue
open-ticket backlog with {highest_backlog_team[2]} overdue cases.


2. SLA PERFORMANCE

{lowest_sla_team[0]} has the lowest closed-ticket SLA compliance
at {lowest_sla_team[3]}%.


3. QUALITY PERFORMANCE

{lowest_qa_team[0]} has the lowest QA pass rate at
{lowest_qa_team[5]}%.


4. CRITICAL EXCEPTIONS

There are {critical_count} Critical-priority open tickets that
have already exceeded SLA.


RECOMMENDED MANAGEMENT ACTIONS

1. Prioritize all Critical overdue tickets for immediate review.

2. Review the overdue backlog in {highest_backlog_team[0]} and
identify capacity, workflow, or escalation bottlenecks.

3. Investigate SLA performance in {lowest_sla_team[0]}.

4. Review QA failures and coaching opportunities in
{lowest_qa_team[0]}.

5. Track SLA compliance, backlog, and QA pass rate together
rather than evaluating teams using a single KPI.


DATA GOVERNANCE NOTE

All figures in this briefing are calculated directly from the
PostgreSQL analytics database. The briefing does not calculate
or invent KPI values independently.
""".strip()


# =========================================================
# SAVE BRIEFING
# =========================================================

OUTPUT_FILE.write_text(
    briefing,
    encoding="utf-8"
)


print()
print(briefing)

print()
print(
    f"Management briefing saved to: {OUTPUT_FILE}"
)