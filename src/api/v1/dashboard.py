from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.deps.auth import get_current_user
from src.services.dashboard import Dashboard

router = APIRouter()


@router.get("/layout", tags=["dashboard"])
def get_layout(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    layout = Dashboard().get_layout()
    if layout.success:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return layout
