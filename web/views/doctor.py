"""Doktor ekranları: yetişkin ve çocuk hasta takibi, klinik not."""

import pandas as pd
import streamlit as st

from web.services import api
from web.ui import components as ui


def _require_doctor() -> bool:
    if st.session_state.role != "doctor":
        ui.note("Bu alan yalnızca doktor hesapları içindir.", "danger")
        return False
    return True


def _note_form(target_label: str, key: str, patient_id: int | None, child_id: int | None) -> None:
    with st.form(f"note_form_{key}"):
        st.markdown(f"**{target_label}** için klinik not")
        note_text = st.text_area("Doktor notu", key=f"note_{key}")
        recommendation = st.text_area("Öneri / takip planı", key=f"rec_{key}")
        next_visit = st.text_input(
            "Sonraki görüşme tarihi", placeholder="2026-05-10", key=f"visit_{key}"
        )
        submitted = st.form_submit_button("Notu kaydet", type="primary")

    if not submitted:
        return

    if not note_text.strip():
        st.error("Doktor notu boş bırakılamaz.")
        return

    ok, result = api.post(
        "/doctor-note",
        json={
            "doctor_id": st.session_state.user_id,
            "patient_id": patient_id,
            "child_id": child_id,
            "note": note_text,
            "recommendation": recommendation,
            "next_visit_date": next_visit,
        },
    )

    if ok:
        st.success("Klinik not kaydedildi.")
    else:
        st.error(result)


def _adult_details(patient_id: int) -> None:
    ok, details = api.get("/patient-details", params={"patient_id": patient_id})

    if not ok:
        st.error(details)
        return

    predictions = details.get("predictions", [])
    logs = details.get("daily_logs", [])

    tests_tab, logs_tab = st.tabs(["Tarama geçmişi", "Günlük kayıtlar"])

    with tests_tab:
        if not predictions:
            ui.empty("Bu hastanın tarama kaydı yok.")
        else:
            st.dataframe(pd.DataFrame(predictions), use_container_width=True, hide_index=True)

    with logs_tab:
        if not logs:
            ui.empty("Bu hastanın günlük kaydı yok.")
            return

        logs_df = pd.DataFrame(logs)
        st.dataframe(logs_df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)

        with col1:
            if "sleep_hours" in logs_df.columns:
                st.markdown("###### Uyku saati")
                st.line_chart(logs_df["sleep_hours"], height=180)
        with col2:
            if "social_interaction" in logs_df.columns:
                st.markdown("###### Sosyal etkileşim")
                st.line_chart(logs_df["social_interaction"], height=180)

        if "mood" in logs_df.columns:
            st.markdown("###### Duygu durumu dağılımı")
            st.bar_chart(logs_df["mood"].value_counts(), height=180)


def _child_details(child_id: int) -> None:
    ok, details = api.get("/child-patient-details", params={"child_id": child_id})

    if not ok:
        st.error(details)
        return

    logs = details.get("daily_logs", [])

    logs_tab, tests_tab = st.tabs(["Günlük kayıtlar", "Tarama geçmişi"])

    with logs_tab:
        if not logs:
            ui.empty("Bu çocuk hasta için günlük kayıt yok.")
        else:
            logs_df = pd.DataFrame(logs)
            st.dataframe(logs_df, use_container_width=True, hide_index=True)

            col1, col2 = st.columns(2)
            with col1:
                if "sleep_hours" in logs_df.columns:
                    st.markdown("###### Uyku saati")
                    st.line_chart(logs_df["sleep_hours"], height=180)
            with col2:
                if "social_interaction" in logs_df.columns:
                    st.markdown("###### Sosyal etkileşim")
                    st.line_chart(logs_df["social_interaction"], height=180)

    with tests_tab:
        ok_tests, tests = api.get("/child-autism-tests", params={"child_id": child_id})

        if not ok_tests:
            st.error(tests)
            return

        if not tests:
            ui.empty("Bu çocuk hasta için tarama kaydı yok.")
            return

        for test in tests:
            risk = test.get("risk_level", "—")
            st.markdown(
                f"{ui.badge(risk, ui.risk_tone(risk))} &nbsp; "
                f"**{test.get('total_score', '—')}/10** &nbsp;·&nbsp; "
                f"<span style='color:var(--ink-subtle);font-size:0.8rem'>{test.get('created_at', '—')}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(test.get("result_text", "—"))
            st.divider()


def _adult_section() -> None:
    ok, patients = api.get("/my-patients", params={"doctor_id": st.session_state.user_id})

    if not ok:
        st.error(patients)
        return

    with ui.card("Hasta ekle"):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_id = st.number_input(
                "Yetişkin hasta ID", min_value=1, step=1, key="add_adult_id"
            )
        with col2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("Ekle", type="primary", use_container_width=True, key="add_adult_btn"):
                ok_add, result = api.post(
                    "/add-patient",
                    params={"doctor_id": st.session_state.user_id, "patient_id": new_id},
                )
                if ok_add:
                    st.success("Hasta eklendi.")
                    st.rerun()
                else:
                    st.error(result)

    if not patients:
        ui.empty("Henüz takip ettiğiniz yetişkin hasta yok.")
        return

    with ui.card("Yetişkin hastalarım"):
        st.dataframe(pd.DataFrame(patients), use_container_width=True, hide_index=True)

        options = {
            f"{patient.get('full_name', 'Hasta')} · ID {patient.get('id') or patient.get('user_id')}": (
                patient.get("id") or patient.get("user_id")
            )
            for patient in patients
        }
        label = st.selectbox("İncelenecek hasta", list(options.keys()), key="adult_detail_pick")
        patient_id = options[label]

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        _adult_details(patient_id)

        st.divider()
        _note_form(label.split(" · ")[0], f"adult_{patient_id}", patient_id, None)


def _child_section() -> None:
    ok, children = api.get("/my-child-patients", params={"doctor_id": st.session_state.user_id})

    if not ok:
        st.error(children)
        return

    with ui.card("Çocuk hasta ekle"):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_id = st.number_input("Çocuk hasta ID", min_value=1, step=1, key="add_child_id")
        with col2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("Ekle", type="primary", use_container_width=True, key="add_child_btn"):
                ok_add, result = api.post(
                    "/add-child-patient",
                    params={"doctor_id": st.session_state.user_id, "child_id": new_id},
                )
                if ok_add:
                    st.success("Çocuk hasta eklendi.")
                    st.rerun()
                else:
                    st.error(result)

    if not children:
        ui.empty("Henüz takip ettiğiniz çocuk hasta yok.")
        return

    with ui.card("Çocuk hastalarım"):
        st.dataframe(pd.DataFrame(children), use_container_width=True, hide_index=True)

        options = {
            f"{child.get('name', 'Çocuk')} · {child.get('age', '-')} yaş · ID {child.get('id')}": child["id"]
            for child in children
        }
        label = st.selectbox("İncelenecek çocuk hasta", list(options.keys()), key="child_detail_pick")
        child_id = options[label]

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        _child_details(child_id)

        st.divider()
        _note_form(label.split(" · ")[0], f"child_{child_id}", None, child_id)


def page_doctor_panel() -> None:
    if not _require_doctor():
        return

    ui.page_head(
        "Hasta takibi",
        "Atanmış hastalarınızın kayıtlarını inceleyin, klinik not ve takip planı ekleyin.",
    )

    adult_tab, child_tab = st.tabs(["Yetişkin hastalar", "Çocuk hastalar"])

    with adult_tab:
        _adult_section()
    with child_tab:
        _child_section()


def page_doctor_notes() -> None:
    is_doctor = st.session_state.role == "doctor"

    ui.page_head(
        "Notlarım" if is_doctor else "Doktor notlarım",
        "Yazdığınız klinik notlar ve takip planları."
        if is_doctor
        else "Doktorunuzun sizin için eklediği notlar ve takip planları.",
    )

    ok, notes = api.get("/my-doctor-notes", params={"user_id": st.session_state.user_id})

    if not ok:
        st.error(notes)
        return

    if not notes:
        ui.empty("Henüz doktor notu bulunmuyor.")
        return

    for note in notes:
        with ui.card():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### {note.get('target_name', 'Hasta')}")
                st.caption(f"{note.get('doctor_name', 'Doktor')} · {note.get('created_at', '—')}")
            with col2:
                next_visit = note.get("next_visit_date")
                if next_visit:
                    st.markdown(
                        f"<div style='text-align:right'>{ui.badge(f'Görüşme: {next_visit}', 'info')}</div>",
                        unsafe_allow_html=True,
                    )

            st.markdown(f"**Not**  \n{note.get('note', '—')}")

            if note.get("recommendation"):
                st.markdown(f"**Öneri / takip planı**  \n{note['recommendation']}")
