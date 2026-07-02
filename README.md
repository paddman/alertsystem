# eGov Workflow Platform

Government-grade workflow and case-management foundation for Thai public-sector digital services.

## MVP capabilities

- Multi-agency workflow definitions with versioning
- Citizen/officer case lifecycle and state transitions
- Role-aware human approval steps
- Append-only audit events with correlation IDs
- API-first architecture for portal, mobile, and integration engines
- PostgreSQL persistence and Redis-ready orchestration
- Self-hosted Docker deployment baseline

## Architecture

```text
Citizen / Officer Portal
          |
          v
      API Gateway
          |
          v
 eGov Workflow Core
  - Cases
  - Workflow versions
  - Human approvals
  - Audit trail
          |
          +--> Integration adapter (n8n)
          +--> Edge adapter (Node-RED)
          +--> AI gateway (local models)
```

The platform owns identity, cases, permissions, workflow definitions, audit, and policy. External engines are adapters only and are not exposed directly to end users.

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

API: `http://localhost:8000`

- Health: `GET /health`
- OpenAPI: `GET /docs`
- Workflows: `/api/v1/workflows`
- Cases: `/api/v1/cases`

## Initial API example

Create a workflow:

```bash
curl -X POST http://localhost:8000/api/v1/workflows \
  -H 'Content-Type: application/json' \
  -d '{
    "agency_code": "DGA-DEMO",
    "code": "PERMIT-001",
    "name": "คำขออนุญาตตัวอย่าง",
    "version": 1,
    "definition": {
      "initial_state": "submitted",
      "states": ["submitted", "review", "approved", "rejected"],
      "transitions": [
        {"from": "submitted", "to": "review", "roles": ["reviewer"]},
        {"from": "review", "to": "approved", "roles": ["approver"]},
        {"from": "review", "to": "rejected", "roles": ["approver"]}
      ]
    }
  }'
```

## Security posture

This repository is an MVP foundation, not a production accreditation claim. Before production use, add an external identity provider, secrets manager, immutable audit storage, network segmentation, vulnerability management, backup/DR testing, and agency-specific compliance controls. See [`docs/security-baseline.md`](docs/security-baseline.md).

## License

No license has been selected yet. Keep the repository private or add an approved license before external distribution.
