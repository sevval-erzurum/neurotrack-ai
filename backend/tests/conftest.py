import os
from collections.abc import Callable, Iterator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_db, make_engine
from app.core.security import hash_password
from app.main import create_app
from app.models import AuditEvent, DoctorStatus, Role, User
from app.services.ratelimit import assistant_limiter, login_ip_limiter, login_limiter

API = "/api/v1"


TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite://")


@pytest.fixture
def app():
    if TEST_DATABASE_URL == "sqlite://":
        # Tek bağlantı: bellek içi veritabanı test boyunca yaşar.
        engine = make_engine(TEST_DATABASE_URL, poolclass=StaticPool)
    else:
        engine = make_engine(TEST_DATABASE_URL)
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_db():
        with Session() as session:
            yield session

    application = create_app()
    application.dependency_overrides[get_db] = override_db
    application.state.test_session = Session
    login_limiter.reset()
    login_ip_limiter.reset()
    assistant_limiter.reset()
    yield application
    engine.dispose()


@pytest.fixture
def anon(app) -> Iterator[TestClient]:
    with TestClient(app, base_url="http://testserver" + API) as client:
        yield client


@pytest.fixture
def make_user(app) -> Callable[..., TestClient]:
    """Kayıt olup oturum açmış ayrı bir istemci döndürür (her kullanıcının kendi cookie'si)."""
    clients: list[TestClient] = []

    def factory(role: str, email: str | None = None, birth_date: date | None = None, approved: bool = True) -> TestClient:
        """Doktorlar varsayılan olarak onaylanır; onay akışını sınayan testler approved=False verir."""
        client = TestClient(app, base_url="http://testserver" + API)
        payload = {
            "full_name": f"Test {role.title()}",
            "email": email or f"{role}{len(clients)}@example.com",
            "password": "correct-horse-1",
            "role": role,
        }
        if birth_date:
            payload["birth_date"] = birth_date.isoformat()
        if role == "doctor":
            payload |= {"license_number": f"TR-{1000 + len(clients)}", "institution": "Test Hastanesi"}
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 201, response.text
        client.user = response.json()
        if role == "doctor" and approved:
            set_doctor_status(app, client.user["id"], DoctorStatus.APPROVED)
        clients.append(client)
        return client

    yield factory
    for client in clients:
        client.close()


def set_doctor_status(app, user_id: int, status: DoctorStatus) -> None:
    with app.state.test_session() as db:
        db.get(User, user_id).doctor_status = status
        db.commit()


def audit_events(app, **filters) -> list[AuditEvent]:
    with app.state.test_session() as db:
        query = db.query(AuditEvent).filter_by(**filters).order_by(AuditEvent.id)
        return query.all()


@pytest.fixture
def admin(app) -> Iterator[TestClient]:
    """Yönetici kayıt formundan açılamaz; CLI'ın yaptığı gibi doğrudan veritabanına yazılır."""
    with app.state.test_session() as db:
        db.add(
            User(email="admin@example.com", full_name="Yönetici", role=Role.ADMIN, password_hash=hash_password("admin-pass-123"))
        )
        db.commit()
    with TestClient(app, base_url="http://testserver" + API) as client:
        response = client.post("/auth/login", json={"email": "admin@example.com", "password": "admin-pass-123"})
        assert response.status_code == 200, response.text
        client.user = response.json()
        yield client


def months_ago(months: int, today: date | None = None) -> date:
    today = today or date.today()
    year, month = divmod(today.year * 12 + today.month - 1 - months, 12)
    return date(year, month + 1, min(today.day, 28))


@pytest.fixture
def parent_with_toddler(make_user):
    parent = make_user("parent")
    child = parent.post("/subjects", json={"name": "Deniz", "birth_date": months_ago(20).isoformat(), "sex": "male"})
    assert child.status_code == 201, child.text
    return parent, child.json()
