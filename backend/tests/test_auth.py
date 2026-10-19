def test_register_starts_session_and_creates_self_profile_for_adult(make_user):
    adult = make_user("adult")

    me = adult.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["role"] == "adult"

    subjects = adult.get("/subjects").json()
    assert [s["kind"] for s in subjects] == ["self"]


def test_session_cookie_is_http_only(anon):
    response = anon.post(
        "/auth/register",
        json={"full_name": "Ayşe Yılmaz", "email": "ayse@example.com", "password": "correct-horse-1", "role": "parent"},
    )
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=lax" in cookie


def test_duplicate_email_is_rejected_case_insensitively(make_user, anon):
    make_user("parent", email="dup@example.com")
    response = anon.post(
        "/auth/register",
        json={"full_name": "Başka Biri", "email": "DUP@example.com", "password": "correct-horse-1", "role": "adult"},
    )
    assert response.status_code == 409


def test_login_does_not_reveal_whether_email_exists(make_user, anon):
    make_user("adult", email="known@example.com")
    wrong_password = anon.post("/auth/login", json={"email": "known@example.com", "password": "wrong-password"})
    unknown_email = anon.post("/auth/login", json={"email": "nobody@example.com", "password": "wrong-password"})
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


def test_login_and_logout(make_user, anon):
    make_user("doctor", email="doc@example.com")
    assert anon.post("/auth/login", json={"email": "doc@example.com", "password": "correct-horse-1"}).status_code == 200
    assert anon.get("/auth/me").status_code == 200
    anon.post("/auth/logout")
    assert anon.get("/auth/me").status_code == 401


def test_login_is_rate_limited(make_user, anon):
    make_user("adult", email="target@example.com")
    codes = [anon.post("/auth/login", json={"email": "target@example.com", "password": "guess"}).status_code for _ in range(11)]
    assert codes[:10] == [401] * 10
    assert codes[10] == 429


def test_rate_limit_cannot_be_bypassed_by_changing_ip(app, make_user):
    """İstemci IP'si X-Forwarded-For'dan gelir ve taklit edilebilir; hesap sınırı IP'den bağımsızdır."""
    from fastapi.testclient import TestClient

    make_user("adult", email="spoof@example.com")
    codes = []
    for i in range(11):
        with TestClient(app, base_url="http://testserver/api/v1", client=(f"10.0.0.{i}", 5000)) as client:
            codes.append(client.post("/auth/login", json={"email": "spoof@example.com", "password": "guess"}).status_code)
    assert codes[:10] == [401] * 10
    assert codes[10] == 429


def test_one_ip_cannot_spray_many_accounts(app, make_user):
    from fastapi.testclient import TestClient

    with TestClient(app, base_url="http://testserver/api/v1", client=("10.9.9.9", 5000)) as client:
        attempts = [{"email": f"user{i}@example.com", "password": "x"} for i in range(51)]
        codes = [client.post("/auth/login", json=body).status_code for body in attempts]
    assert codes[:50] == [401] * 50
    assert codes[50] == 429


def test_successful_logins_do_not_count_towards_rate_limit(make_user, anon):
    make_user("parent", email="frequent@example.com")
    credentials = {"email": "frequent@example.com", "password": "correct-horse-1"}
    codes = [anon.post("/auth/login", json=credentials).status_code for _ in range(15)]
    assert set(codes) == {200}


def test_short_password_is_rejected(anon):
    response = anon.post(
        "/auth/register",
        json={"full_name": "Kısa Şifre", "email": "short@example.com", "password": "1234567", "role": "adult"},
    )
    assert response.status_code == 422


def test_protected_endpoints_require_session(anon):
    assert anon.get("/subjects").status_code == 401
    assert anon.get("/notifications").status_code == 401


def test_forged_token_is_rejected(anon):
    anon.cookies.set("nt_session", "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.invalid")
    assert anon.get("/auth/me").status_code == 401
