"""NeuroTrack AI web arayüzü giriş noktası.

Çalıştırma:
    python -m streamlit run web_app.py --server.port 8501

Backend adresi NEUROTRACK_API_URL ortam değişkeniyle değiştirilebilir
(varsayılan: http://127.0.0.1:8003).
"""

import streamlit as st

from web.ui import deva_widget, shell, state, theme
from web.views import adult, auth, comms, deva, doctor, home
from web.views import parent as parent_views

PUBLIC_ROUTES = {
    state.LOGIN: auth.page_login,
    state.REGISTER: auth.page_register,
}

PRIVATE_ROUTES = {
    state.HOME: home.page_home,
    # Yetişkin
    "assessment": adult.page_assessment,
    "daily_log": adult.page_daily_log,
    "clinical": adult.page_clinical,
    "history": adult.page_history,
    "ai_suggestion": adult.page_ai_suggestion,
    "progress": adult.page_progress,
    # Ebeveyn
    "parent_panel": parent_views.page_parent_panel,
    "child_test": parent_views.page_child_test,
    # Doktor
    "doctor_panel": doctor.page_doctor_panel,
    "doctor_notes": doctor.page_doctor_notes,
    # Ortak
    "messages": comms.page_messages,
    "notifications": comms.page_notifications,
    "deva": deva.page_deva,
}


def main() -> None:
    theme.page_config()
    theme.inject_css()
    state.init()

    if not state.is_authenticated():
        theme.hide_sidebar()
        render = PUBLIC_ROUTES.get(st.session_state.page, auth.page_login)
        render()
        return

    shell.sidebar()
    render = PRIVATE_ROUTES.get(st.session_state.page, home.page_home)
    render()

    # Sohbet balonu sayfa içeriğinden sonra çizilir; CSS ile sağ alta sabitlenir.
    deva_widget.render()


main()
