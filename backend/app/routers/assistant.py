from fastapi import APIRouter, Request

from app.core.deps import DB, CurrentUser
from app.schemas import ChatIn, ChatOut
from app.services import assistant, insights
from app.services.access import get_subject
from app.services.ratelimit import assistant_limiter

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatOut)
def chat(data: ChatIn, request: Request, user: CurrentUser, db: DB) -> ChatOut:
    assistant_limiter.check(f"user:{user.id}")
    context = None
    if data.subject_id is not None:
        request.state.audit_subject_id = data.subject_id
        context = insights.compute(db, get_subject(db, user, data.subject_id), days=14)
    reply, source = assistant.reply(user, data.message, data.history, context)
    return ChatOut(reply=reply, source=source)
