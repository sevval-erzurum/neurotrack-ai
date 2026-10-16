from collections.abc import Callable, Iterator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_db, make_engine
from app.main import create_app
from app.services.ratelimit import assistant_limiter, login_limiter

API = "/api/v1"


@pytest.fixture
def app():
    # Tek bağlantı: bellek içi veritabanı test boyunca yaşar.
    engine = make_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_db():
        with Session() as session:
            yield session

    application = create_app()
    application.dependency_overrides[get_db] = override_db
    login_limiter.reset()
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

    def factory(role: str, email: str | None = None, birth_date: date | None = None) -> TestClient:
        client = TestClient(app, base_url="http://testserver" + API)
        payload = {
            "full_name": f"Test {role.title()}",
            "email": email or f"{role}{len(clients)}@example.com",
            "password": "correct-horse-1",
            "role": role,
        }
        if birth_date:
            payload["birth_date"] = birth_date.isoformat()
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 201, response.text
        client.user = response.json()
        clients.append(client)
        return client

    yield factory
    for client in clients:
        client.close()


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
