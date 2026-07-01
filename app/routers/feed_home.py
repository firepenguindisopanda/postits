from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from . import router, templates


@router.get("/feed", response_class=HTMLResponse)
async def feed_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={
            "user": user
        }
    )
