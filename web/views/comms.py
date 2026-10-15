"""İletişim ekranları: mesajlaşma, istekler, bildirimler."""

import streamlit as st

from web.services import api
from web.ui import components as ui

REQUEST_STATUS = {
    "pending": ("Onay bekliyor", "warning"),
    "accepted": ("Onaylandı", "success"),
    "rejected": ("Reddedildi", "danger"),
    "none": ("İstek gönderilmedi", "neutral"),
}


def _respond_to_request(request_id: int, status: str) -> None:
    ok, result = api.post(
        "/respond-message-request",
        params={
            "request_id": request_id,
            "status": status,
            "user_id": st.session_state.user_id,
        },
    )

    if ok:
        st.rerun()
    else:
        st.error(result)


def _incoming_requests() -> None:
    ok, requests_data = api.get("/message-requests", params={"user_id": st.session_state.user_id})

    if not ok:
        st.error(requests_data)
        return

    if not requests_data:
        ui.empty("Mesajlaşma isteği bulunmuyor.")
        return

    for req in requests_data:
        status = req.get("status", "none")
        label, tone = REQUEST_STATUS.get(status, (status, "neutral"))
        request_id = req.get("id")

        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown(
                f"**{req.get('sender_name', '—')}** → {req.get('receiver_name', '—')} &nbsp; "
                f"{ui.badge(label, tone)}",
                unsafe_allow_html=True,
            )

        is_mine_to_answer = (
            st.session_state.role == "doctor"
            and req.get("receiver_id") == st.session_state.user_id
            and status == "pending"
        )

        if is_mine_to_answer:
            with col2:
                accept_col, reject_col = st.columns(2)
                with accept_col:
                    if st.button("Kabul et", key=f"accept_{request_id}", type="primary", use_container_width=True):
                        _respond_to_request(request_id, "accepted")
                with reject_col:
                    if st.button("Reddet", key=f"reject_{request_id}", type="secondary", use_container_width=True):
                        _respond_to_request(request_id, "rejected")

        st.divider()


def _available_doctors() -> None:
    ok, doctors = api.get(
        "/available-doctors-for-message", params={"user_id": st.session_state.user_id}
    )

    if not ok or not isinstance(doctors, list):
        ui.empty("Mesaj isteği gönderebileceğiniz doktor bulunamadı.")
        return

    if not doctors:
        ui.empty(
            "Atanmış doktorunuz yok. Mesajlaşabilmek için önce bir doktorun sizi "
            "hasta listesine eklemesi gerekir."
        )
        return

    for doctor in doctors:
        doctor_id = doctor.get("user_id")
        status = doctor.get("request_status", "none")
        label, tone = REQUEST_STATUS.get(status, (status, "neutral"))

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(
                f"**{doctor.get('full_name', 'Doktor')}** &nbsp; {ui.badge(label, tone)}  \n"
                f"<span style='color:var(--ink-subtle);font-size:0.8rem'>{doctor.get('email', '—')}</span>",
                unsafe_allow_html=True,
            )

        if status == "none":
            with col2:
                if st.button("İstek gönder", key=f"send_req_{doctor_id}", type="primary", use_container_width=True):
                    ok_send, result = api.post(
                        "/send-message-request",
                        json={"sender_id": st.session_state.user_id, "receiver_id": doctor_id},
                    )
                    if ok_send:
                        st.rerun()
                    else:
                        st.error(result)

        st.divider()


def _conversation() -> None:
    ok, contacts = api.get("/message-contacts", params={"user_id": st.session_state.user_id})

    if not ok:
        st.error(contacts)
        return

    if not contacts:
        ui.empty("Henüz onaylanmış bir sohbet kişiniz yok.")
        return

    options = {
        f"{contact.get('full_name', 'Kullanıcı')} · {contact.get('role', '—')}": contact.get("user_id")
        for contact in contacts
    }
    label = st.selectbox("Sohbet", list(options.keys()))
    other_user_id = options[label]

    ok_conv, messages = api.get(
        "/secure-conversation",
        params={"user1_id": st.session_state.user_id, "user2_id": other_user_id},
    )

    if not ok_conv:
        st.error(messages)
        return

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if not messages:
        ui.empty("Henüz mesaj yok. İlk mesajı siz gönderin.")
    else:
        for msg in messages:
            is_me = msg.get("sender_id") == st.session_state.user_id
            ui.message_bubble(
                "Sen" if is_me else msg.get("sender_name", "—"),
                msg.get("content", ""),
                is_me,
                msg.get("created_at", ""),
            )

    with st.form("send_message_form", clear_on_submit=True):
        content = st.text_area("Mesajınız", label_visibility="collapsed", placeholder="Mesaj yazın...")
        submitted = st.form_submit_button("Gönder", type="primary")

    if submitted:
        if not content.strip():
            st.error("Boş mesaj gönderilemez.")
            return

        ok_send, result = api.post(
            "/secure-send-message",
            json={
                "sender_id": st.session_state.user_id,
                "receiver_id": other_user_id,
                "content": content,
            },
        )

        if ok_send:
            st.rerun()
        else:
            st.error(result)


def page_messages() -> None:
    is_doctor = st.session_state.role == "doctor"

    ui.page_head(
        "Mesajlar",
        "Doktor–hasta mesajlaşması. Sohbet başlaması için hastanın istek göndermesi ve "
        "doktorun onaylaması gerekir.",
    )

    chat_tab, request_tab = st.tabs(["Sohbetler", "İstekler"])

    with chat_tab:
        with ui.card():
            _conversation()

    with request_tab:
        with ui.card("Gelen istekler"):
            _incoming_requests()

        if not is_doctor:
            with ui.card("Atanmış doktorlarım"):
                _available_doctors()


def page_notifications() -> None:
    ui.page_head("Bildirimler", "Sistem ve doktor kaynaklı bildirimleriniz.")

    ok, notifications = api.get("/notifications", params={"user_id": st.session_state.user_id})

    if not ok:
        st.error(notifications)
        return

    if not notifications:
        ui.empty("Bildiriminiz yok.")
        return

    unread = [item for item in notifications if not item.get("is_read")]

    if unread:
        ui.note(f"{len(unread)} okunmamış bildiriminiz var.", "info")

    for notification in notifications:
        is_read = notification.get("is_read")

        with ui.card():
            col1, col2 = st.columns([4, 1])

            with col1:
                badge_html = "" if is_read else ui.badge("Yeni", "info")
                st.markdown(
                    f"**{notification.get('title', '—')}** &nbsp; {badge_html}",
                    unsafe_allow_html=True,
                )
                st.markdown(notification.get("message", "—"))
                st.caption(notification.get("created_at", "—"))

            with col2:
                if not is_read:
                    if st.button(
                        "Okundu",
                        key=f"read_{notification['id']}",
                        type="secondary",
                        use_container_width=True,
                    ):
                        ok_mark, result = api.post(
                            "/mark-notification-read",
                            params={"notification_id": notification["id"]},
                        )
                        if ok_mark:
                            st.rerun()
                        else:
                            st.error(result)
