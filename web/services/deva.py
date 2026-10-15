"""Deva AI sohbet mantığı.

Hem sağ alttaki yüzen widget hem de tam sayfa görünüm buradan beslenir;
mantık tek yerde durur.
"""

import streamlit as st

from web.services import api

WELCOME = {
    "doctor": "Merhaba, ben Deva. Hasta takibi, klinik yorumlama veya kayıt analizi konusunda yardımcı olabilirim.",
    "parent": "Merhaba, ben Deva. Çocuk takibi, günlük kayıtlar veya uyarı analizi konusunda yardımcı olabilirim.",
    "adult": "Merhaba, ben Deva. Günlük takip, duygu durumu, risk analizi veya öneriler konusunda yardımcı olabilirim.",
}

PROMPTS = {
    "doctor": ["Hasta kayıtlarını nasıl yorumlarım?", "Takip planı nasıl oluşturmalıyım?"],
    "parent": ["Çocuğumun uyku düzeni nasıl iyileşir?", "Günlük kayıt neden önemli?"],
    "adult": ["Bugün kaygılıyım, ne yapabilirim?", "Rutin değişikliğiyle nasıl başa çıkarım?"],
}


def welcome_text() -> str:
    return WELCOME.get(st.session_state.role, WELCOME["adult"])


def prompts() -> list[str]:
    return PROMPTS.get(st.session_state.role, PROMPTS["adult"])


def send_message(user_message: str) -> None:
    if not user_message.strip():
        return

    st.session_state.chat_history.append({"role": "user", "content": user_message})

    ok, result = api.post(
        "/chatbot",
        json={
            "user_id": st.session_state.user_id,
            "message": user_message,
            "role": st.session_state.role,
        },
    )

    if ok and isinstance(result, dict):
        reply = (
            result.get("bot_response")
            or result.get("reply")
            or result.get("message")
            or "Deva şu anda yanıt oluşturamadı."
        )
    else:
        reply = result if isinstance(result, str) else "Deva şu anda yanıt oluşturamadı."

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
