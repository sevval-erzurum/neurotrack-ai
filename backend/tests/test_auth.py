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
