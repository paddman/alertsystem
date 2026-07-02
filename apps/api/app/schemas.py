from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkflowCreate(BaseModel):
    agency_code: str = Field(min_length=2, max_length=64)
    code: str = Field(min_length=2, max_length=128)
    name: str = Field(min_length=2, max_length=255)
    version: int = Field(ge=1)
    definition: dict[str, Any]


class WorkflowRead(WorkflowCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    created_at: datetime


class CaseCreate(BaseModel):
    agency_code: str = Field(min_length=2, max_length=64)
    workflow_id: str
    reference_no: str = Field(min_length=2, max_length=128)
    subject_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class CaseRead(CaseCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    current_state: str
    created_at: datetime
    updated_at: datetime


class CaseTransition(BaseModel):
    to_state: str
    actor_id: str
    actor_role: str
    correlation_id: str
    comment: str | None = None


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str | None
    agency_code: str
    actor_id: str
    actor_role: str
    action: str
    correlation_id: str
    payload: dict[str, Any]
    event_hash: str
    created_at: datetime
