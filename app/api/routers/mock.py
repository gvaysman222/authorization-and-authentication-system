from fastapi import APIRouter, Depends
from app.core.dependencies import require_permission

router = APIRouter(prefix="", tags=["mock"])

MOCK_PROJECTS = [{"id": 1, "name": "Alpha"}, {"id": 2, "name": "Beta"}, {"id": 3, "name": "Gamma"}]

@router.get("/projects")
def list_projects(ctx=Depends(require_permission("project", "read"))):
    return MOCK_PROJECTS

@router.post("/projects")
def create_project(ctx=Depends(require_permission("project", "create"))):
    return {"detail": "project created (mock)"}

@router.get("/reports")
def list_reports(ctx=Depends(require_permission("report", "read"))):
    return [{"id": 1, "title": "Q1"}, {"id": 2, "title": "Q2"}]
