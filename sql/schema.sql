-- Customer Support Analytics Automation
-- PostgreSQL database schema

-- Drop child tables first because of foreign-key relationships
DROP TABLE IF EXISTS qa_evaluations;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS agents;


CREATE TABLE agents (
    agent_id VARCHAR(10) PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    team VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL
);


CREATE TABLE tickets (
    ticket_id VARCHAR(12) PRIMARY KEY,
    agent_id VARCHAR(10) NOT NULL,
    category VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    opened_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP,
    sla_target_hours INTEGER NOT NULL,
    age_hours INTEGER NOT NULL,
    resolution_hours INTEGER,
    sla_breached BOOLEAN NOT NULL,

    CONSTRAINT fk_ticket_agent
        FOREIGN KEY (agent_id)
        REFERENCES agents(agent_id)
);


CREATE TABLE qa_evaluations (
    evaluation_id VARCHAR(12) PRIMARY KEY,
    ticket_id VARCHAR(12) NOT NULL,
    agent_id VARCHAR(10) NOT NULL,
    qa_score INTEGER NOT NULL,
    defect_category VARCHAR(50) NOT NULL,
    critical_error BOOLEAN NOT NULL,
    passed_qa BOOLEAN NOT NULL,

    CONSTRAINT fk_qa_ticket
        FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id),

    CONSTRAINT fk_qa_agent
        FOREIGN KEY (agent_id)
        REFERENCES agents(agent_id)
);