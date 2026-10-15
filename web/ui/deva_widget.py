"""Sağ altta yüzen Deva AI sohbet balonu.

Her sayfada görünür. Açık/kapalı durumu session_state'te tutulur; Streamlit her
etkileşimde sayfayı yeniden çalıştırdığı için panelin açık kalması buna bağlıdır.
"""

import streamlit as st

from web.services import deva
from web.ui import components as ui

OPEN_KEY = "deva_widget_open"
RECENT_MESSAGE_COUNT = 8


def _launcher() -> None:
    """Kapalıyken görünen küçük buton."""
    with st.container(key="deva_fab"):
        if st.button("💬 Deva AI", type="primary", key="deva_open_btn"):
            st.session_state[OPEN_KEY] = True
            st.rerun()


def _panel() -> None:
    """Açıkken görünen sohbet paneli."""
    with st.container(key="deva_panel"):
        header, close = st.columns([3, 1])

        with header:
            st.markdown('<div class="deva-widget-title">Deva AI</div>', unsafe_allow_html=True)
        with close:
            if st.button("✕", key="deva_close_btn", type="secondary", use_container_width=True):
                st.session_state[OPEN_KEY] = False
                st.rerun()

        with st.container(key="deva_log"):
            if not st.session_state.chat_history:
                ui.message_bubble("Deva", deva.welcome_text(), is_me=False)

            for msg in st.session_state.chat_history[-RECENT_MESSAGE_COUNT:]:
                is_me = msg["role"] == "user"
                ui.message_bubble("Sen" if is_me else "Deva", msg["content"], is_me)

        with st.form("deva_widget_form", clear_on_submit=True):
            message = st.text_input(
                "Mesaj", label_visibility="collapsed", placeholder="Deva'ya sorun..."
            )
            submitted = st.form_submit_button("Gönder", type="primary", use_container_width=True)

        if submitted and message.strip():
            with st.spinner("Deva yanıtlıyor..."):
                deva.send_message(message)
            st.rerun()

        st.caption("Deva tanı koymaz, karar desteği sunar.")


def render() -> None:
    """Oturum açık kullanıcılar için widget'ı çizer.

    Deva'nın kendi tam sayfası açıkken widget gösterilmez; aynı sohbet iki kez
    görünmesin.
    """
    if st.session_state.get("page") == "deva":
        return

    if st.session_state.get(OPEN_KEY):
        _panel()
    else:
        _launcher()
