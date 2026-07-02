from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.audit import append_audit_event
from app.db import get_db
from app.models import AuditEvent, Case, WorkflowDefinition
from app.schemas import AuditEventRead, CaseCreate, CaseRead, CaseTransition

router = APIRouter(prefix="/cases", tags=["cases"])


def _allowed_transition(
    definition: dict[str, Any], current_state: str, to_state: str, actor_role: str
) -> bool:
    for transition in definition.get("transitions", []):
        if transition.get("from") != current_state or transition.get("to") != to_state:
            continue
        return actor_role in transition.get("roles", [])
    return False


@router.post("", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, db: Session = Depends(get_db)) -> Case:
    workflow = db.get(WorkflowDefinition, payload.workflow_id)
    if not workflow or workflow.agency_code != payload.agency_code:
        raise HTTPException(status_code=404, detail="Workflow not found for agency")

    initial_state = workflow.definition.get("initial_state")
    if not initial_state:
        raise HTTPException(status_code=422, detail="Workflow has no initial_state")

    case = Case(**payload.model_dump(), current_state=initial_state)
    db.add(case)
    db.flush()
    append_audit_event(
        db,
        case_id=case.id,
        agency_code=case.agency_code,
        actor_id=payload.subject_id or "anonymous",
        actor_role="citizen",
        action="case.created",
        correlation_id=case.reference_no,
        payload={"state": initial_state},
    )
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Reference number already exists") from exc
    db.refresh(case)
    return case


@router.get("", response_model=list[CaseRead])
def list_cases(agency_code: str | None = None, db: Session = Depends(get_db)) -> list[Case]:
    query = select(Case).order_by(Case.created_at.desc())
    if agency_code:
        query = query.where(Case.agency_code == agency_code)
    return list(db.scalars(query).all())


@router.post("/{case_id}/transitions", response_model=CaseRead)
def transition_case(
    case_id: str, payload: CaseTransition, db: Session = Depends(get_db)
) -> Case:
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    workflow = db.get(WorkflowDefinition, case.workflow_id)
    if not workflow:
        raise HTTPException(status_code=409, detail="Workflow definition unavailable")

    if not _allowed_transition(
        workflow.definition, case.current_state, payload.to_state, payload.actor_role
    ):
        raise HTTPException(status_code=403, detail="Transition is not allowed for this role")

    from_state = case.current_state
    case.current_state = payload.to_state
    append_audit_event(
        db,
        case_id=case.id,
        agency_code=case.agency_code,
        actor_id=payload.actor_id,
        actor_role=payload.actor_role,
        action="case.transitioned",
        correlation_id=payload.correlation_id,
        payload={
            "from": from_state,
            "to": payload.to_state,
            "comment": payload.comment,
            "workflow_version": workflow.version,
        },
    )
    db.commit()
    db.refresh(case)
    return case


@router.get("/{case_id}/audit", response_model=list[AuditEventRead])
def list_case_audit(case_id: str, db: Session = Depends(get_db)) -> list[AuditEvent]:
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    query = (
        select(AuditEvent)
        .where(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.created_at, AuditEvent.id)
    )
    return list(db.scalars(query).all())
