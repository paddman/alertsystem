# Security Baseline

## Mandatory before production

- Connect officers through an approved OIDC/SAML identity provider with MFA.
- Enforce tenant/agency isolation in authorization and database access.
- Use a secrets manager; never store credentials in workflow definitions.
- Place public endpoints behind WAF, API gateway, rate limits, and DDoS controls.
- Restrict connector egress by destination allowlist and private network policy.
- Send audit events to immutable/WORM storage and a central SIEM.
- Encrypt data in transit and at rest using organization-managed keys.
- Define data classification, retention, deletion, and legal-hold rules.
- Perform SAST, dependency scanning, image scanning, DAST, and penetration testing.
- Produce an SBOM and sign build artifacts/container images.
- Establish tested backups, restore procedures, RPO/RTO, and a DR exercise schedule.

## High-impact decision rule

AI or automation may prepare, classify, summarize, or recommend. It must not independently issue a legally significant approval, rejection, sanction, entitlement, or deletion without a recorded policy gate and authorized human action.

## n8n and external engine controls

- Keep engines on private networks.
- Do not expose engine editors to citizens or ordinary officers.
- Disable unrestricted command execution, local file access, and unapproved community nodes.
- Store only adapter references in the core platform; the system of record remains this platform.
- Review licensing before embedding or reselling an external workflow engine.
