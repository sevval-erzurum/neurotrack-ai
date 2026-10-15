"""Uygulama kabuğu: marka, sidebar navigasyon, rol bazlı menü."""

import streamlit as st

from web.services import api
from web.ui import state
from web.ui.theme import APP_NAME, APP_SUBTITLE

# Rol -> (menü grubu başlığı, [(sayfa anahtarı, etiket)])
NAV: dict[str, list[tuple[str, list[tuple[str, str]]]]] = {
    "adult": [
        ("Genel", [("home", "Ana sayfa"), ("history", "Geçmiş kayıtlarım")]),
        (
            "Takip",
            [
                ("assessment", "Otizm tarama testi"),
                ("daily_log", "Günlük kayıt"),
                ("clinical", "Klinik takip formu"),
            ],
        ),
        ("Analiz", [("ai_suggestion", "AI önerileri"), ("progress", "Gelişim analizi")]),
        (
            "İletişim",
            [
                ("doctor_notes", "Doktor notlarım"),
                ("messages", "Mesajlar"),
                ("notifications", "Bildirimler"),
            ],
        ),
    ],
    "parent": [
        ("Genel", [("home", "Ana sayfa")]),
        ("Çocuk takibi", [("parent_panel", "Çocuklarım"), ("child_test", "Çocuk tarama testi")]),
        (
            "İletişim",
            [
                ("doctor_notes", "Doktor notlarım"),
                ("messages", "Mesajlar"),
                ("notifications", "Bildirimler"),
            ],
        ),
    ],
    "doctor": [
        ("Genel", [("home", "Ana sayfa")]),
        ("Klinik", [("doctor_panel", "Hasta takibi"), ("doctor_notes", "Notlarım")]),
        ("İletişim", [("messages", "Mesajlar"), ("notifications", "Bildirimler")]),
    ],
}


def brand() -> None:
    st.markdown(
        f"""
        <div class="nt-brand">
            <div class="nt-brand-mark">NT</div>
            <div class="nt-brand-name">{APP_NAME}</div>
        </div>
        <p class="nt-brand-sub">{APP_SUBTITLE}</p>
        """,
        unsafe_allow_html=True,
    )


def _backend_status() -> None:
    if api.health():
        return
    st.markdown(
        '<div class="nt-note danger">Backend bağlantısı yok. Port 8003 dinleniyor mu?</div>',
        unsafe_allow_html=True,
    )


def sidebar() -> None:
    """Oturum açmış kullanıcı için kalıcı navigasyon."""
    with st.sidebar:
        brand()

        st.markdown(
            f"""
            <div class="nt-user">
                <div class="nt-user-name">{st.session_state.full_name}</div>
                <div class="nt-user-role">{state.role_label()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for group_title, items in NAV.get(st.session_state.role, NAV["adult"]):
            st.markdown(f'<div class="nt-navlabel">{group_title}</div>', unsafe_allow_html=True)

            for page_key, label in items:
                is_active = st.session_state.page == page_key
                if st.button(
                    label,
                    key=f"nav_{page_key}",
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                ):
                    if not is_active:
                        state.go_to(page_key)

        st.markdown('<div class="nt-navlabel">Asistan</div>', unsafe_allow_html=True)
        if st.button("Deva AI", key="nav_deva", type="primary" if st.session_state.page == "deva" else "secondary", use_container_width=True):
            if st.session_state.page != "deva":
                state.go_to("deva")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        _backend_status()

        if st.button("Çıkış yap", key="nav_logout", type="secondary", use_container_width=True):
            state.logout()
