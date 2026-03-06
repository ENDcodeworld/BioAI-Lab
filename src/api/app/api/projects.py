"""
Projects Router
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    organism: Optional[str] = None


class Project(BaseModel):
    id: str
    name: str
    description: Optional[str]
    organism: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime


@router.get("/", response_model=List[Project])
async def list_projects():
    """
    List all projects for the current user.
    """
    # TODO: Implement
    return []


@router.post("/", response_model=Project)
async def create_project(project: ProjectCreate):
    """
    Create a new project.
    """
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """
    Get project details.
    """
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, project: ProjectCreate):
    """
    Update project.
    """
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """
    Delete project.
    """
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not implemented yet")
