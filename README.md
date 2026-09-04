# Customer Support Analytics Automation

An end-to-end **Python + PostgreSQL analytics automation project** that transforms raw customer-support data into validated operational insights, SLA monitoring, QA performance analysis, prioritized exceptions, automated Excel reporting, and an evidence-grounded management briefing.

---

## Business Problem

Customer-support operations often rely on data coming from multiple sources such as:

- Ticketing systems
- Agent records
- QA evaluations

When these datasets are reviewed manually, reporting can become slow, inconsistent, and difficult to act on.

Management needs quick answers to questions such as:

- How many tickets are currently open?
- Which open cases are already overdue?
- Are teams meeting SLA targets?
- Which teams have quality issues?
- Which cases require immediate management attention?
- What actions should management prioritize?

This project automates that workflow.

---

## Solution Overview

The solution uses Python and PostgreSQL to create an end-to-end analytics pipeline:

```text
Synthetic Operational Data
        ↓
Python Data Generation
        ↓
PostgreSQL Database
        ↓
SQL Analytics
        ↓
KPI & Exception Detection
        ↓
Automated Excel Report
        ↓
Evidence-Grounded Management Briefing
        ↓
Optional Human-in-the-Loop AI Rewrite