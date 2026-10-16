from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import and_, func, or_, select, update

from app.core.deps import DB, CurrentUser
from app.models import CareTeamMember, Message, Role, Subject, User, utcnow
from app.schemas import ConversationOut, MessageIn, MessageOut, UserBrief
from app.services.access import can_message
from app.services.notify import notify

router = APIRouter(prefix="/conversations", tags=["messages"])


def _between(a: int, b: int):
    return or_(
        and_(Message.sender_id == a, Message.recipient_id == b),
        and_(Message.sender_id == b, Message.recipient_id == a),
    )


def _contacts(db: DB, user: User) -> list[User]:
    if user.role == Role.DOCTOR:
        stmt = (
            select(User)
            .join(Subject, Subject.owner_id == User.id)
            .join(CareTeamMember, CareTeamMember.subject_id == Subject.id)
            .where(CareTeamMember.doctor_id == user.id)
        )
    else:
        stmt = (
            select(User)
            .join(CareTeamMember, CareTeamMember.doctor_id == User.id)
            .join(Subject, Subject.id == CareTeamMember.subject_id)
            .where(Subject.owner_id == user.id)
        )
    return list(db.scalars(stmt.distinct().order_by(User.full_name)))


def _peer(db: DB, user: User, peer_id: int) -> User:
    peer = db.get(User, peer_id)
    if peer is None or not can_message(db, user, peer):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bu kullanıcıyla mesajlaşma izniniz yok.")
    return peer


@router.get("", response_model=list[ConversationOut])
def conversations(user: CurrentUser, db: DB) -> list[ConversationOut]:
    result = []
    for contact in _contacts(db, user):
        last = db.scalar(select(Message).where(_between(user.id, contact.id)).order_by(Message.id.desc()).limit(1))
        unread = db.scalar(
            select(func.count())
            .select_from(Message)
            .where(Message.sender_id == contact.id, Message.recipient_id == user.id, Message.read_at.is_(None))
        )
        result.append(
            ConversationOut(
                user=UserBrief.model_validate(contact),
                last_message=MessageOut.model_validate(last) if last else None,
                unread=unread or 0,
            )
        )
    never = datetime.min.replace(tzinfo=UTC)
    return sorted(result, key=lambda c: c.last_message.created_at if c.last_message else never, reverse=True)


@router.get("/{peer_id}/messages", response_model=list[MessageOut])
def read_messages(peer_id: int, user: CurrentUser, db: DB, limit: int = 200) -> list[Message]:
    peer = _peer(db, user, peer_id)
    db.execute(
        update(Message)
        .where(Message.sender_id == peer.id, Message.recipient_id == user.id, Message.read_at.is_(None))
        .values(read_at=utcnow())
    )
    db.commit()
    messages = db.scalars(select(Message).where(_between(user.id, peer.id)).order_by(Message.id.desc()).limit(min(limit, 500)))
    return list(reversed(list(messages)))


@router.post("/{peer_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def send_message(peer_id: int, data: MessageIn, user: CurrentUser, db: DB) -> Message:
    peer = _peer(db, user, peer_id)
    message = Message(sender_id=user.id, recipient_id=peer.id, body=data.body)
    db.add(message)
    preview = data.body if len(data.body) <= 80 else data.body[:77] + "…"
    notify(db, peer.id, "message", f"{user.full_name} mesaj gönderdi", preview, f"/messages?with={user.id}")
    db.commit()
    return message
