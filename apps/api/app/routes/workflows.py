from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import WorkflowDefinition
from app.schemas import WorkflowCreate, WorkflowRead

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowRead, status_code=status.HTTP_201_CREATED)
def create_workflow(payload: WorkflowCreate, db: Session = Depends(get_db)) -> WorkflowDefinition:
    workflow = WorkflowDefinition(**payload.model_dump())
    db.add(workflow)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Workflow version already exists") from exc
    db.refresh(workflow)
    return workflow


@router.get("", response_model=list[WorkflowRead])
def list_workflows(
    agency_code: str | None = None, db: Session = Depends(get_db)
) -> list[WorkflowDefinition]:
    query = select(WorkflowDefinition).order_by(
        WorkflowDefinition.agency_code,
        WorkflowDefinition.code,
        WorkflowDefinition.version.desc(),
    )
    if agency_code:
        query = query.where(WorkflowDefinition.agency_code == agency_code)
    return list(db.scalars(query).all())
