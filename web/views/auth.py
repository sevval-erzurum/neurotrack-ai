"""Giriş ve kayıt ekranları."""

import streamlit as st

from web.services import api
from web.ui import components as ui
from web.ui import state
from web.ui.theme import APP_NAME

ROLE_OPTIONS = {
    "adult": "Yetişkin kullanıcı — kendi takibimi yapacağım",
    "parent": "Ebeveyn — çocuğumun takibini yapacağım",
    "doctor": "Doktor — hastalarımı takip edeceğim",
}

# Demo/sunum hesapları. Giriş ekranında açıkça listelenir; gerçek kullanıma
# alınacaksa bu blok ve _demo_accounts() kaldırılmalıdır.
DEMO_ACCOUNTS = [
    ("Yetişkin", "adult@test.com", "test1234"),
    ("Ebeveyn", "parent@test.com", "test1234"),
    ("Doktor", "doctor@test.com", "test1234"),
]


def _hero() -> None:
    st.markdown(
        f"""
        <div class="nt-brand" style="margin-bottom:10px">
            <div class="nt-brand-mark">NT</div>
            <div class="nt-brand-name">{APP_NAME}</div>
        </div>
        <h1 style="margin:0 0 10px 0">Otizm takibi ve<br>karar destek platformu</h1>
        <p class="page-sub">
            Yapay zekâ destekli ön tarama, günlük takip ve uzman iletişimi tek yerde.
            Yetişkin, ebeveyn ve doktor rolleri için ayrı çalışma alanları.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    ui.note(
        "NeuroTrack AI tanı koymaz. Ön değerlendirme ve takip desteği sunar; "
        "otizm tanısı yalnızca uzman hekim değerlendirmesiyle konulabilir.",
        "info",
    )


def _sign_in(email: str, password: str) -> None:
    ok, result = api.post("/login", json={"email": email, "password": password})

    if ok:
        state.login(result["user_id"], result["role"], result["full_name"])
        st.rerun()
    else:
        st.error(result)


def _demo_accounts() -> None:
    """Sunum için hazır hesaplar. Alanları doldurmak yerine doğrudan giriş yaparlar."""
    st.markdown(
        '<div class="nt-note info" style="margin-bottom:12px">'
        "<b>Demo hesapları</b><br>Şifre tümünde: <code>test1234</code>"
        "</div>",
        unsafe_allow_html=True,
    )

    for role_label, email, password in DEMO_ACCOUNTS:
        col1, col2 = st.columns([1.6, 1])

        with col1:
            st.markdown(
                f'<div style="padding-top:6px"><b>{role_label}</b><br>'
                f'<span style="color:var(--ink-subtle);font-size:0.8rem">{email}</span></div>',
                unsafe_allow_html=True,
            )
        with col2:
            if st.button("Giriş yap", key=f"demo_{email}", type="secondary", use_container_width=True):
                _sign_in(email, password)


def page_login() -> None:
    left, right = st.columns([1, 1], gap="large")

    with left:
        _hero()

    with right:
        with ui.card():
            st.markdown("### Giriş yap")
            st.markdown(
                '<p class="page-sub" style="margin-bottom:16px">Hesabınıza erişmek için bilgilerinizi girin.</p>',
                unsafe_allow_html=True,
            )

            with st.form("login_form"):
                email = st.text_input("E-posta", placeholder="ornek@eposta.com")
                password = st.text_input("Şifre", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Giriş yap", type="primary", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("E-posta ve şifre alanları zorunludur.")
                else:
                    _sign_in(email, password)

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            st.caption("Hesabınız yok mu?")
            if st.button("Yeni hesap oluştur", type="secondary", use_container_width=True):
                state.go_to(state.REGISTER)

        _demo_accounts()


def page_register() -> None:
    left, right = st.columns([1, 1], gap="large")

    with left:
        _hero()

    with right:
        with ui.card():
            st.markdown("### Hesap oluştur")
            st.markdown(
                '<p class="page-sub" style="margin-bottom:16px">Rolünüzü seçin — arayüz seçiminize göre şekillenir.</p>',
                unsafe_allow_html=True,
            )

            with st.form("register_form"):
                full_name = st.text_input("Ad soyad")
                email = st.text_input("E-posta", placeholder="ornek@eposta.com")
                password = st.text_input("Şifre", type="password")
                role = st.radio(
                    "Rol",
                    list(ROLE_OPTIONS.keys()),
                    format_func=lambda key: ROLE_OPTIONS[key],
                )
                submitted = st.form_submit_button("Hesabı oluştur", type="primary", use_container_width=True)

            if submitted:
                if not full_name or not email or not password:
                    st.error("Tüm alanların doldurulması gerekir.")
                else:
                    ok, result = api.post(
                        "/register",
                        json={
                            "full_name": full_name,
                            "email": email,
                            "password": password,
                            "role": role,
                        },
                    )

                    if ok:
                        st.success("Kayıt başarılı. Şimdi giriş yapabilirsiniz.")
                    else:
                        st.error(result)

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            st.caption("Zaten hesabınız var mı?")
            if st.button("Giriş ekranına dön", type="secondary", use_container_width=True):
                state.go_to(state.LOGIN)
