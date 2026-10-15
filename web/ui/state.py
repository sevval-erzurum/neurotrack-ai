"""Oturum durumu ve navigasyon."""

import streamlit as st

LOGIN = "login"
REGISTER = "register"
HOME = "home"

DEFAULTS = {
    "user_id": None,
    "role": None,
    "full_name": None,
    "page": LOGIN,
    "chat_history": [],
}


def init() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def is_authenticated() -> bool:
    return st.session_state.user_id is not None


def login(user_id: int, role: str, full_name: str) -> None:
    st.session_state.user_id = user_id
    st.session_state.role = role
    st.session_state.full_name = full_name
    st.session_state.chat_history = []
    st.session_state.page = HOME


def logout() -> None:
    # Sayfaların bıraktığı geçici veriler (test sonucu, form durumu) bir sonraki
    # kullanıcıya sızmamalı; oturum tamamen temizlenir.
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    for key, value in DEFAULTS.items():
        st.session_state[key] = value

    st.rerun()


def role_label(role: str | None = None) -> str:
    role = role or st.session_state.role
    return {
        "adult": "Yetişkin kullanıcı",
        "parent": "Ebeveyn",
        "doctor": "Doktor",
    }.get(role, "Kullanıcı")
