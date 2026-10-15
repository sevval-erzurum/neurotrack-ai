"""Ebeveyn ekranları: çocuk profilleri, günlük takip, çocuk ön tarama testi."""

import pandas as pd
import streamlit as st

from web.services import api
from web.ui import components as ui

CHILD_QUESTIONS = {
    "A1_Score": "Çocuk sosyal ortamlarda diğer çocuklarla etkileşim kurmakta zorlanıyor mu?",
    "A2_Score": "Göz teması kurmakta veya sürdürmekte zorlanıyor mu?",
    "A3_Score": "Rutin değişikliklerine karşı belirgin tepki gösteriyor mu?",
    "A4_Score": "İsmi söylendiğinde her zaman tepki vermiyor mu?",
    "A5_Score": "Tekrarlayan hareketler veya davranışlar gözlemleniyor mu?",
    "A6_Score": "Ses, ışık, kalabalık gibi duyusal uyaranlardan fazla etkileniyor mu?",
    "A7_Score": "Yaşıtlarına göre iletişim kurma isteği düşük mü?",
    "A8_Score": "Oyuncakları amacına uygun oynamak yerine sıralama veya döndürme gibi davranışlar gösteriyor mu?",
    "A9_Score": "Duygularını ifade etmekte veya karşı tarafın duygularını anlamakta zorlanıyor mu?",
    "A10_Score": "Belirli nesne, konu veya davranışlara yoğun şekilde takılıyor mu?",
}

MOODS = ["mutlu", "üzgün", "kaygılı", "sakin", "öfkeli"]


def _require_parent() -> bool:
    if st.session_state.role != "parent":
        ui.note("Bu alan yalnızca ebeveyn hesapları içindir.", "danger")
        return False
    return True


def _fetch_children() -> list[dict]:
    ok, children = api.get("/children", params={"parent_id": st.session_state.user_id})

    if not ok:
        st.error(children)
        return []

    return children if isinstance(children, list) else []


def _child_picker(children: list[dict], key: str) -> dict:
    options = {
        f"{child.get('name', 'Çocuk')} · {child.get('age', '-')} yaş": child for child in children
    }
    label = st.selectbox("Çocuk seç", list(options.keys()), key=key)
    return options[label]


def _add_child_form() -> None:
    with st.form("add_child_form"):
        col1, col2, col3 = st.columns([2, 1, 1.4])

        with col1:
            name = st.text_input("Çocuğun adı")
        with col2:
            age = st.number_input("Yaş", min_value=1, max_value=18, value=7)
        with col3:
            gender = st.selectbox("Cinsiyet", ["Kız", "Erkek", "Belirtmek istemiyorum"])

        submitted = st.form_submit_button("Çocuk ekle", type="primary")

    if not submitted:
        return

    if not name:
        st.error("Çocuğun adı zorunludur.")
        return

    ok, result = api.post(
        "/children",
        json={
            "parent_id": st.session_state.user_id,
            "name": name,
            "age": age,
            "gender": gender,
        },
    )

    if ok:
        st.success(f"{name} eklendi.")
        st.rerun()
    else:
        st.error(result)


def _child_daily_log(child_id: int) -> None:
    with st.form(f"child_log_{child_id}"):
        col1, col2 = st.columns(2)

        with col1:
            mood = st.selectbox("Duygu durumu", MOODS, key=f"cmood_{child_id}")
            sleep_hours = st.number_input(
                "Uyku saati", min_value=0, max_value=24, value=8, key=f"csleep_{child_id}"
            )
        with col2:
            social = st.slider("Sosyal etkileşim", 0, 10, 5, key=f"csocial_{child_id}")

        note_text = st.text_area("Not", key=f"cnote_{child_id}")
        submitted = st.form_submit_button("Günlük kaydı ekle", type="primary")

    if not submitted:
        return

    ok, result = api.post(
        "/child-daily-log",
        json={
            "child_id": child_id,
            "mood": mood,
            "sleep_hours": sleep_hours,
            "social_interaction": social,
            "note": note_text,
        },
    )

    if ok:
        st.success("Çocuk günlük kaydı eklendi.")
    else:
        st.error(result)


def _child_history(child_id: int) -> None:
    ok, logs = api.get("/child-daily-logs", params={"child_id": child_id})

    if not ok:
        st.error(logs)
        return

    if not logs:
        ui.empty("Bu çocuk için henüz günlük kayıt yok.")
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


def _child_alerts(child_id: int) -> None:
    ok, result = api.get("/child-alerts", params={"child_id": child_id})

    if not ok:
        st.error(result)
        return

    alerts = result.get("alerts", [])

    if not alerts:
        ui.empty("Uyarı bulunmuyor.")
        return

    for alert in alerts:
        is_clear = "belirgin bir takip uyarısı görünmüyor" in alert
        ui.note(alert, "success" if is_clear else "warning")


def page_parent_panel() -> None:
    if not _require_parent():
        return

    ui.page_head(
        "Çocuklarım",
        "Çocuk profillerini yönetin, günlük kayıt girin ve takip geçmişini inceleyin.",
    )

    children = _fetch_children()

    with ui.card("Yeni çocuk profili"):
        _add_child_form()

    if not children:
        ui.empty("Henüz kayıtlı çocuk profili yok. Takibe başlamak için yukarıdan ekleyin.")
        return

    with ui.card("Takip"):
        child = _child_picker(children, key="parent_panel_child")
        child_id = child["id"]

        col1, col2, col3 = st.columns(3)
        with col1:
            ui.stat("Ad", str(child.get("name", "—")))
        with col2:
            ui.stat("Yaş", str(child.get("age", "—")))
        with col3:
            ui.stat("Cinsiyet", str(child.get("gender", "—")))

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        log_tab, history_tab, alert_tab = st.tabs(["Günlük kayıt", "Geçmiş", "Uyarılar"])

        with log_tab:
            _child_daily_log(child_id)
        with history_tab:
            _child_history(child_id)
        with alert_tab:
            _child_alerts(child_id)


def _render_child_result(result: dict) -> None:
    risk_level = result.get("risk_level", "—")
    probability = result.get("probability")

    with ui.card("Sonuç"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f'<div class="nt-stat"><div class="nt-stat-label">Risk düzeyi</div>'
                f'<div style="margin-top:6px">{ui.badge(risk_level, ui.risk_tone(risk_level))}</div></div>',
                unsafe_allow_html=True,
            )
        with col2:
            ui.stat("Toplam puan", f"{result.get('total_score', '—')}/10", "evet yanıtı")
        with col3:
            ui.stat(
                "Model güveni",
                f"{probability:.0%}" if probability is not None else "—",
                "tahmin olasılığı",
            )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        if result.get("result_text"):
            ui.note(result["result_text"], ui.risk_tone(risk_level))

        with st.expander("Ham model çıktısı"):
            st.json(result)


def page_child_test() -> None:
    if not _require_parent():
        return

    ui.page_head(
        "Çocuk tarama testi",
        "Çocuğunuz için 10 soruluk ön tarama. Sonuç makine öğrenmesi modeliyle değerlendirilir.",
    )
    ui.disclaimer()

    # Sonuç, soruların altında kalmaması için formun üstünde gösterilir.
    if "child_test_result" in st.session_state:
        _render_child_result(st.session_state.child_test_result)

        if st.button("Yeni test yap", type="secondary"):
            del st.session_state.child_test_result
            st.rerun()
        return

    children = _fetch_children()

    if not children:
        ui.empty("Test yapabilmek için önce Çocuklarım sayfasından bir profil ekleyin.")
        return

    child = _child_picker(children, key="child_test_child")
    child_id = child["id"]
    child_age = int(child.get("age", 0) or 0)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    with st.form(f"child_test_form_{child_id}"):
        st.markdown(f"**{child.get('name', 'Çocuk')}** · {child_age} yaş için değerlendirme")
        st.divider()

        answers = {}

        for index, (key, question) in enumerate(CHILD_QUESTIONS.items(), start=1):
            st.markdown(f"**{index}.** {question}")
            answer = st.radio(
                question,
                ["Hayır", "Evet"],
                horizontal=True,
                key=f"child_test_{child_id}_{key}",
                label_visibility="collapsed",
            )
            answers[key] = 1 if answer == "Evet" else 0
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        submitted = st.form_submit_button("Testi tamamla ve değerlendir", type="primary")

    if not submitted:
        return

    ok, result = api.post(
        "/child-autism-test",
        json={"child_id": child_id, **answers, "age": child_age},
    )

    if not ok:
        st.error(result)
        return

    st.session_state.child_test_result = result
    st.rerun()
