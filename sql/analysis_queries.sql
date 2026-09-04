-- Customer Support Analytics Automation
-- Management KPI Analysis


-- =========================================================
-- 1. OVERALL TICKET KPIs
-- =========================================================

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

-- =========================================================
-- 2. TEAM PERFORMANCE
-- =========================================================

SELECT
    a.team,

    COUNT(*) AS total_tickets,

    COUNT(*) FILTER (
        WHERE t.status = 'Open'
    ) AS open_tickets,

    COUNT(*) FILTER (
        WHERE t.status = 'Open'
        AND t.sla_breached = TRUE
    ) AS overdue_open_tickets,

    ROUND(
        AVG(t.resolution_hours)
        FILTER (
            WHERE t.status = 'Closed'
        ),
        2
    ) AS avg_resolution_hours,

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
    ) AS closed_sla_compliance_pct

FROM tickets t

JOIN agents a
    ON t.agent_id = a.agent_id

GROUP BY a.team

ORDER BY closed_sla_compliance_pct ASC;

-- =========================================================
-- 3. QA PERFORMANCE BY TEAM
-- =========================================================

SELECT
    a.team,

    COUNT(q.evaluation_id) AS qa_evaluations,

    ROUND(
        AVG(q.qa_score),
        2
    ) AS avg_qa_score,

    COUNT(*) FILTER (
        WHERE q.passed_qa = FALSE
    ) AS failed_qa,

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
    ) AS qa_pass_rate_pct,

    COUNT(*) FILTER (
        WHERE q.critical_error = TRUE
    ) AS critical_errors

FROM qa_evaluations q

JOIN agents a
    ON q.agent_id = a.agent_id

GROUP BY a.team

ORDER BY qa_pass_rate_pct ASC;

-- =========================================================
-- 4. COMBINED TEAM PERFORMANCE
-- =========================================================

WITH ticket_metrics AS (

    SELECT
        a.team,

        COUNT(*) AS total_tickets,

        COUNT(*) FILTER (
            WHERE t.status = 'Open'
        ) AS open_tickets,

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
        ) AS qa_pass_rate_pct,

        COUNT(*) FILTER (
            WHERE q.critical_error = TRUE
        ) AS critical_errors

    FROM qa_evaluations q

    JOIN agents a
        ON q.agent_id = a.agent_id

    GROUP BY a.team
)

SELECT
    t.team,
    t.total_tickets,
    t.open_tickets,
    t.overdue_open_tickets,
    t.sla_compliance_pct,
    q.avg_qa_score,
    q.qa_pass_rate_pct,
    q.critical_errors

FROM ticket_metrics t

JOIN qa_metrics q
    ON t.team = q.team

ORDER BY
    t.overdue_open_tickets DESC;

    -- =========================================================
-- 5. PRIORITIZED OPEN-TICKET EXCEPTION REGISTER
-- =========================================================

SELECT
    t.ticket_id,
    a.agent_name,
    a.team,
    t.category,
    t.priority,
    t.opened_at,
    t.age_hours,
    t.sla_target_hours,

    GREATEST(
        t.age_hours - t.sla_target_hours,
        0
    ) AS hours_over_sla,

    CASE
        WHEN t.priority = 'Critical'
             AND t.sla_breached = TRUE
            THEN 'Critical'

        WHEN t.priority = 'High'
             AND t.sla_breached = TRUE
            THEN 'High'

        WHEN t.sla_breached = TRUE
             AND (t.age_hours - t.sla_target_hours) >= 168
            THEN 'High'

        WHEN t.sla_breached = TRUE
            THEN 'Warning'

        ELSE 'On Track'
    END AS management_priority

FROM tickets t

JOIN agents a
    ON t.agent_id = a.agent_id

WHERE t.status = 'Open'

ORDER BY
    CASE
        WHEN t.priority = 'Critical'
             AND t.sla_breached = TRUE
            THEN 1

        WHEN t.priority = 'High'
             AND t.sla_breached = TRUE
            THEN 2

        WHEN t.sla_breached = TRUE
             AND (t.age_hours - t.sla_target_hours) >= 168
            THEN 3

        WHEN t.sla_breached = TRUE
            THEN 4

        ELSE 5
    END,

    hours_over_sla DESC;