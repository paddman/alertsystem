# Architecture

## Design principles

1. The platform owns case state, identity context, policy, workflow versions, and audit evidence.
2. Integration engines are replaceable adapters, not the system of record.
3. Every agency boundary is explicit in data, authorization, logs, and deployment policy.
4. Human approval is mandatory for high-impact administrative decisions.
5. Workflow publication is versioned; existing cases remain bound to their original version.

## Target components

```text
Portal / Officer Console
        |
API Gateway + WAF
        |
Identity and Policy Enforcement
        |
Workflow Core ---------------- Audit Service --> SIEM / WORM storage
        |
Execution Router
  |         |          |
Custom    n8n      Node-RED
workers  adapter    adapter
        |
Government APIs / ERP / DMS / Notification / AI Gateway
```

## MVP boundaries

This first commit implements the workflow and case API skeleton, transition authorization by role, workflow version binding, and chained HMAC audit events. It intentionally excludes production identity federation, BPMN editing, document storage, task inboxes, and external integration adapters.

## Suggested production split

- `identity-service`: OIDC/SAML integration, delegation, MFA context
- `workflow-service`: workflow definitions, publication, migration policy
- `case-service`: case state and data
- `task-service`: human task inbox, SLA, escalation, substitution
- `audit-service`: append-only events and immutable export
- `integration-service`: connector allowlists, egress control, n8n adapter
- `document-service`: templates, signatures, evidence, retention
- `notification-service`: email, SMS, LINE, government channels
- `ai-gateway`: classification, redaction, local-model routing, approval gates
