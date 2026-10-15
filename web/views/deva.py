"""Deva AI tam sayfa sohbet görünümü.

Uzun sohbetler için geniş görünüm. Sohbet mantığı web/services/deva.py içindedir;
sağ alttaki widget ile aynı geçmişi paylaşır.
"""

import streamlit as st

from web.services import deva
from web.ui import components as ui


def page_deva() -> None:
    ui.page_head(
        "Deva AI asistan",
        "Takip sürecinizle ilgili sorularınızı yanıtlar. Tanı koymaz, karar desteği sunar.",
    )

    with ui.card():
        ui.message_bubble("Deva", deva.welcome_text(), is_me=False)

        for msg in st.session_state.chat_history:
            is_me = msg["role"] == "user"
            ui.message_bubble("Sen" if is_me else "Deva", msg["content"], is_me)

        if not st.session_state.chat_history:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.caption("Örnek sorular")

            suggestions = deva.prompts()
            cols = st.columns(len(suggestions))

            for col, prompt in zip(cols, suggestions):
                with col:
                    if st.button(prompt, key=f"prompt_{prompt}", type="secondary", use_container_width=True):
                        deva.send_message(prompt)
                        st.rerun()

        with st.form("deva_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])

            with col1:
                message = st.text_input(
                    "Mesaj", label_visibility="collapsed", placeholder="Deva'ya bir soru sorun..."
                )
            with col2:
                submitted = st.form_submit_button("Gönder", type="primary", use_container_width=True)

        if submitted and message.strip():
            with st.spinner("Deva yanıtlıyor..."):
                deva.send_message(message)
            st.rerun()

        if st.session_state.chat_history:
            if st.button("Sohbeti temizle", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()

    st.caption("Deva tanı koymaz. Takip, bilgilendirme ve karar destek amacıyla yardımcı olur.")
