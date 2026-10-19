"""Erişim günlüğü.

Kayıt, router'lara dağılmış çağrılarla değil tek bir ara katmanla tutulur: hangi isteklerin
günlüğe gireceği aşağıdaki ACTIONS tablosundadır. Yeni bir endpoint eklenirken buraya bir satır
eklemek yeterlidir; erişim reddedilen (401/403/404) istekler de aynı yoldan kaydedilir.

İstek gövdesi saklanmaz, yani günlükte sağlık verisi yoktur. Gerektiğinde router bir isteğin
kaydını `request.state` üzerinden zenginleştirir (ör. asistan isteğinde gövdedeki subject_id).
"""

import logging
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import AuditEvent, Subject, User

log = logging.getLogger(__name__)

# (HTTP metodu, router yolu) -> eylem kodu. Burada olmayan istekler (sağlık kontrolü, bildirim
# listesi, model kartı, yöneticinin doktor listesi gibi sağlık verisi içermeyenler) günlüğe yazılmaz.
ACTIONS: dict[tuple[str, str], str] = {
    ("POST", "/auth/register"): "auth.register",
    ("POST", "/auth/login"): "auth.login",
    ("POST", "/auth/logout"): "auth.logout",
    ("GET", "/subjects"): "subject.list",
    ("POST", "/subjects"): "subject.create",
    ("GET", "/subjects/{subject_id}"): "subject.view",
    ("PATCH", "/subjects/{subject_id}"): "subject.update",
    ("DELETE", "/subjects/{subject_id}"): "subject.delete",
    ("GET", "/subjects/{subject_id}/insights"): "insights.view",
    ("GET", "/subjects/{subject_id}/access-log"): "access_log.view",
    ("POST", "/subjects/{subject_id}/care-team"): "care_team.add",
    ("DELETE", "/subjects/{subject_id}/care-team/{doctor_id}"): "care_team.remove",
    ("GET", "/subjects/{subject_id}/logs"): "log.list",
    ("PUT", "/subjects/{subject_id}/logs"): "log.write",
    ("DELETE", "/subjects/{subject_id}/logs/{log_id}"): "log.delete",
    ("GET", "/subjects/{subject_id}/observations"): "observation.list",
    ("POST", "/subjects/{subject_id}/observations"): "observation.create",
    ("GET", "/subjects/{subject_id}/notes"): "note.list",
    ("POST", "/subjects/{subject_id}/notes"): "note.create",
    ("GET", "/subjects/{subject_id}/screenings"): "screening.list",
    ("POST", "/subjects/{subject_id}/screenings"): "screening.create",
    ("GET", "/subjects/{subject_id}/screenings/{screening_id}"): "screening.view",
    ("POST", "/assistant/chat"): "assistant.chat",
    ("GET", "/conversations/{peer_id}/messages"): "message.read",
    ("POST", "/conversations/{peer_id}/messages"): "message.send",
    ("POST", "/admin/doctors/{user_id}/approve"): "admin.doctor.approve",
    ("POST", "/admin/doctors/{user_id}/reject"): "admin.doctor.reject",
    ("POST", "/admin/doctors/{user_id}/suspend"): "admin.doctor.suspend",
    ("GET", "/admin/audit"): "admin.audit.view",
}

_TARGET_PARAMS = ("doctor_id", "peer_id", "user_id")


def outcome_for(status_code: int) -> str:
    if status_code < 400:
        return "ok"
    if status_code in (401, 403, 404):
        return "denied"
    return "error"


def set_actor(request: Request, user: User) -> None:
    request.state.audit_actor = (user.id, str(user.role), user.full_name)


def record(
    db: Session,
    *,
    action: str,
    status_code: int = 200,
    actor: User | None = None,
    actor_label: str | None = None,
    subject_id: int | None = None,
    target_user_id: int | None = None,
    ip: str | None = None,
    created_at=None,
) -> AuditEvent:
    """Olayı oturuma ekler (commit çağırana aittir). Seed ve testler de bunu kullanır."""
    event = AuditEvent(
        actor_id=actor.id if actor else None,
        actor_role=str(actor.role) if actor else None,
        actor_label=actor.full_name if actor else actor_label,
        action=action,
        outcome=outcome_for(status_code),
        status_code=status_code,
        subject_id=subject_id,
        target_user_id=target_user_id,
        ip=ip,
    )
    if created_at is not None:
        event.created_at = created_at
    db.add(event)
    return event


def _int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def install(app: FastAPI) -> None:
    @app.middleware("http")
    async def audit_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)
        route = request.scope.get("route")
        action = ACTIONS.get((request.method, getattr(route, "path", "")))
        if action is None:
            return response

        params = request.scope.get("path_params") or {}
        state = request.state
        actor = getattr(state, "audit_actor", None)
        target = next((_int(params[k]) for k in _TARGET_PARAMS if k in params), None)
        event = AuditEvent(
            actor_id=actor[0] if actor else None,
            actor_role=actor[1] if actor else None,
            actor_label=actor[2] if actor else getattr(state, "audit_label", None),
            action=action,
            outcome=outcome_for(response.status_code),
            status_code=response.status_code,
            subject_id=_int(params.get("subject_id")) or getattr(state, "audit_subject_id", None),
            target_user_id=target or getattr(state, "audit_target_user_id", None),
            ip=request.client.host if request.client else None,
        )
        # Testlerdeki get_db değişimine uyması için oturum bağımlılık üzerinden alınır.
        session_factory = request.app.dependency_overrides.get(get_db, get_db)
        sessions = session_factory()
        try:
            db = next(sessions)
            db.add(event)
            db.commit()
        except Exception:  # günlük hatası kullanıcı isteğini bozmamalı
            log.exception("Erişim günlüğü yazılamadı: %s", action)
        finally:
            sessions.close()
        return response


def subject_history(db: Session, subject: Subject, limit: int = 100) -> list[AuditEvent]:
    """Sahibin göreceği geçmiş: sahibin kendisi dışındaki kişilerin bu kayıttaki başarılı işlemleri."""
    stmt = (
        select(AuditEvent)
        .where(
            AuditEvent.subject_id == subject.id,
            AuditEvent.outcome == "ok",
            AuditEvent.actor_id.is_not(None),
            AuditEvent.actor_id != subject.owner_id,
        )
        .order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))
