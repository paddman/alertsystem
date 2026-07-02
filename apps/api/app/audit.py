import hashlib
import hmac
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AuditEvent


def append_audit_event(
    db: Session,
    *,
    agency_code: str,
    actor_id: str,
    actor_role: str,
    action: str,
    correlation_id: str,
    payload: dict[str, Any],
    case_id: str | None = None,
) -> AuditEvent:
    previous = db.scalar(
        select(AuditEvent)
        .where(AuditEvent.agency_code == agency_code)
        .order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
        .limit(1)
    )
    previous_hash = previous.event_hash if previous else None
    canonical = json.dumps(
        {
            "agency_code": agency_code,
            "actor_id": actor_id,
            "actor_role": actor_role,
            "action": action,
            "correlation_id": correlation_id,
            "payload": payload,
            "case_id": case_id,
            "previous_hash": previous_hash,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    event_hash = hmac.new(
        get_settings().audit_hmac_key.encode(), canonical, hashlib.sha256
    ).hexdigest()

    event = AuditEvent(
        case_id=case_id,
        agency_code=agency_code,
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        correlation_id=correlation_id,
        payload=payload,
        previous_hash=previous_hash,
        event_hash=event_hash,
    )
    db.add(event)
    return event
