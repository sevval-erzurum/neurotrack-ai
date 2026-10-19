from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import select

from app.core.config import get_settings
from app.core.deps import DB, CurrentUser
from app.core.security import DUMMY_HASH, create_access_token, decode_access_token, hash_password, verify_password
from app.models import DoctorStatus, Role, Subject, SubjectKind, User
from app.schemas import LoginIn, RegisterIn, UserOut
from app.services.audit import set_actor
from app.services.notify import notify
from app.services.ratelimit import login_ip_limiter, login_limiter

router = APIRouter(prefix="/auth", tags=["auth"])


def _start_session(response: Response, user: User) -> None:
    settings = get_settings()
    response.set_cookie(
        settings.cookie_name,
        create_access_token(user.id),
        max_age=settings.access_token_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, request: Request, response: Response, db: DB) -> User:
    email = data.email.lower()
    request.state.audit_label = email
    if db.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Bu e-posta ile kayıtlı bir hesap var.")

    user = User(email=email, full_name=data.full_name, role=data.role, password_hash=hash_password(data.password))
    db.add(user)
    if data.role == Role.ADULT:
        user.subjects.append(Subject(kind=SubjectKind.SELF, name=data.full_name, birth_date=data.birth_date))
    if data.role == Role.DOCTOR:
        # Doktor hesabı onay bekler: oturum açabilir ama yönetici onaylayana kadar hiçbir
        # bakım ekibine eklenemez ve veri göremez.
        user.doctor_status = DoctorStatus.PENDING
        user.license_number = data.license_number
        user.institution = data.institution
        for admin_id in db.scalars(select(User.id).where(User.role == Role.ADMIN)):
            notify(
                db,
                admin_id,
                "doctor_application",
                "Yeni doktor başvurusu",
                f"{data.full_name} ({data.institution}) onay bekliyor.",
                "/admin/doctors",
            )
    db.commit()

    set_actor(request, user)
    _start_session(response, user)
    return user


@router.post("/login", response_model=UserOut)
def login(data: LoginIn, request: Request, response: Response, db: DB) -> User:
    email = data.email.lower()
    client = request.client.host if request.client else "unknown"
    account_key, ip_key = f"account:{email}", f"ip:{client}"
    request.state.audit_label = email
    # Yalnızca başarısız denemeler sayılır; meşru kullanıcı sık giriş yaptı diye kilitlenmez.
    login_limiter.check(account_key, record=False)
    login_ip_limiter.check(ip_key, record=False)

    user = db.scalar(select(User).where(User.email == email))
    valid = verify_password(data.password, user.password_hash if user else DUMMY_HASH)
    if user is None or not valid:
        login_limiter.hit(account_key)
        login_ip_limiter.hit(ip_key)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-posta veya şifre hatalı.")

    login_limiter.clear(account_key)
    set_actor(request, user)
    _start_session(response, user)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: DB) -> None:
    token = request.cookies.get(get_settings().cookie_name)
    user_id = decode_access_token(token) if token else None
    user = db.get(User, user_id) if user_id else None
    if user is not None:
        set_actor(request, user)
    response.delete_cookie(get_settings().cookie_name, path="/")


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> User:
    return user
