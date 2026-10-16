from sqlalchemy.orm import Session

from app.models import Notification


def notify(db: Session, user_id: int, kind: str, title: str, body: str, link: str | None = None) -> None:
    """Bildirimi oturuma ekler; commit çağıranın işlemine dahildir."""
    db.add(Notification(user_id=user_id, kind=kind, title=title, body=body, link=link))
