
import getpass

import psycopg


DB_NAME = "customer_support_analytics"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"


password = getpass.getpass("PostgreSQL password: ")


query = """
SELECT
    COUNT(*) AS total_tickets,

    COUNT(*) FILTER (
        WHERE status = 'Open'
    ) AS open_tickets,

    COUNT(*) FILTER (
        WHERE status = 'Closed'
    ) AS closed_tickets,

    COUNT(*) FILTER (
        WHERE status = 'Open'
        AND sla_breached = TRUE
    ) AS overdue_open_tickets,

    ROUND(
        AVG(resolution_hours)
        FILTER (WHERE status = 'Closed'),
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
    ) AS closed_sla_compliance_pct

FROM tickets;
"""


with psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=password,
    host=DB_HOST,
    port=DB_PORT
) as connection:

    with connection.cursor() as cursor:

        cursor.execute(query)

        result = cursor.fetchone()

        print()
        print("CUSTOMER SUPPORT MANAGEMENT KPIs")
        print("--------------------------------")
        print(f"Total Tickets: {result[0]}")
        print(f"Open Tickets: {result[1]}")
        print(f"Closed Tickets: {result[2]}")
        print(f"Overdue Open Tickets: {result[3]}")
        print(f"Average Resolution Hours: {result[4]}")
        print(f"Closed SLA Compliance: {result[5]}%")