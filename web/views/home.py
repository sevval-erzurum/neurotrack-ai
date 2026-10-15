"""Rol bazlı ana sayfa / özet paneli."""

import streamlit as st

from web.services import api
from web.ui import components as ui
from web.ui import state


def _gamification() -> dict:
    ok, result = api.get("/adult-gamification-v2", params={"user_id": st.session_state.user_id})

    if not ok:
        ok, result = api.get("/adult-gamification", params={"user_id": st.session_state.user_id})

    return result if ok and isinstance(result, dict) else {}


def _unread_count() -> int:
    ok, result = api.get("/notifications", params={"user_id": st.session_state.user_id})

    if not ok or not isinstance(result, list):
        return 0

    return sum(1 for item in result if not item.get("is_read"))


def _adult_summary() -> None:
    motivation = _gamification()
    streak = motivation.get("current_streak", 0)
    badges = motivation.get("badges", [])

    ok_logs, logs = api.get("/my-daily-logs", params={"user_id": st.session_state.user_id})
    ok_tests, tests = api.get("/my-predictions", params={"user_id": st.session_state.user_id})

    log_count = len(logs) if ok_logs and isinstance(logs, list) else 0
    test_count = len(tests) if ok_tests and isinstance(tests, list) else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        ui.stat("Günlük seri", f"{streak}", "gün üst üste kayıt")
    with col2:
        ui.stat("Günlük kayıt", f"{log_count}", "toplam giriş")
    with col3:
        ui.stat("Tarama testi", f"{test_count}", "tamamlanan test")
    with col4:
        ui.stat("Rozet", f"{len(badges)}", "kazanılan rozet")

    message = motivation.get("message")
    if message:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        ui.note(message, "success" if streak > 0 else "neutral")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    with ui.card("Sıradaki adım"):
        st.markdown(
            "Günlük kaydını girerek serini sürdür, ardından AI önerilerinden "
            "bugüne özel geri bildirim al."
        )
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("Günlük kayıt gir", type="primary", use_container_width=True):
                state.go_to("daily_log")
        with col_b:
            if st.button("AI önerilerini gör", type="secondary", use_container_width=True):
                state.go_to("ai_suggestion")


def _parent_summary() -> None:
    ok, children = api.get("/children", params={"parent_id": st.session_state.user_id})
    child_list = children if ok and isinstance(children, list) else []

    col1, col2, col3 = st.columns(3)

    with col1:
        ui.stat("Kayıtlı çocuk", f"{len(child_list)}", "profil")
    with col2:
        ui.stat("Bildirim", f"{_unread_count()}", "okunmamış")
    with col3:
        ages = [str(child.get("age", "-")) for child in child_list[:3]]
        ui.stat("Yaş dağılımı", ", ".join(ages) if ages else "—", "kayıtlı çocuklar")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if not child_list:
        with ui.card("Başlangıç"):
            st.markdown("Takibe başlamak için önce bir çocuk profili oluşturun.")
            if st.button("Çocuk profili ekle", type="primary"):
                state.go_to("parent_panel")
        return

    with ui.card("Sıradaki adım"):
        st.markdown("Çocuğunuz için günlük kayıt girin veya ön tarama testini tamamlayın.")
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("Çocuk takibine git", type="primary", use_container_width=True):
                state.go_to("parent_panel")
        with col_b:
            if st.button("Tarama testi yap", type="secondary", use_container_width=True):
                state.go_to("child_test")


def _doctor_summary() -> None:
    ok_adults, adults = api.get("/my-patients", params={"doctor_id": st.session_state.user_id})
    ok_children, children = api.get("/my-child-patients", params={"doctor_id": st.session_state.user_id})
    ok_reqs, reqs = api.get("/message-requests", params={"user_id": st.session_state.user_id})

    adult_count = len(adults) if ok_adults and isinstance(adults, list) else 0
    child_count = len(children) if ok_children and isinstance(children, list) else 0
    pending = (
        sum(1 for item in reqs if item.get("status") == "pending")
        if ok_reqs and isinstance(reqs, list)
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        ui.stat("Yetişkin hasta", f"{adult_count}", "takipte")
    with col2:
        ui.stat("Çocuk hasta", f"{child_count}", "takipte")
    with col3:
        ui.stat("Mesaj isteği", f"{pending}", "yanıt bekliyor")
    with col4:
        ui.stat("Bildirim", f"{_unread_count()}", "okunmamış")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    with ui.card("Sıradaki adım"):
        st.markdown("Hasta kayıtlarını inceleyin, klinik not ve takip planı ekleyin.")
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("Hasta takibine git", type="primary", use_container_width=True):
                state.go_to("doctor_panel")
        with col_b:
            if pending > 0 and st.button(f"{pending} mesaj isteğini yanıtla", type="secondary", use_container_width=True):
                state.go_to("messages")


SUBTITLES = {
    "adult": "Tarama testleri, günlük kayıtlar ve AI destekli geri bildirimler burada toplanır.",
    "parent": "Çocuğunuzun günlük takibi, ön tarama sonuçları ve doktor iletişimi.",
    "doctor": "Atanmış yetişkin ve çocuk hastalarınızın takip özeti.",
}


def page_home() -> None:
    role = st.session_state.role
    first_name = (st.session_state.full_name or "").split(" ")[0]

    ui.page_head(
        f"Hoş geldin, {first_name}",
        SUBTITLES.get(role, SUBTITLES["adult"]),
    )

    if role == "doctor":
        _doctor_summary()
    elif role == "parent":
        _parent_summary()
    else:
        _adult_summary()
