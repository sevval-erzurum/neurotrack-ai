"""Yetişkin kullanıcı ekranları: tarama, günlük kayıt, klinik form, geçmiş, analiz."""

import pandas as pd
import streamlit as st

from web.services import api
from web.ui import components as ui

QUESTIONS = {
    "A1_Score": "Sosyal ortamlarda diğer insanlarla iletişim kurmakta zorlanırım.",
    "A2_Score": "Göz teması kurmakta veya sürdürmekte zorlanırım.",
    "A3_Score": "Rutinlerimin değişmesi beni rahatsız eder.",
    "A4_Score": "Başkalarının duygu ve düşüncelerini anlamakta zorlanırım.",
    "A5_Score": "Belirli konulara yoğun ve uzun süreli ilgi duyarım.",
    "A6_Score": "Kalabalık veya gürültülü ortamlarda rahatsız olurum.",
    "A7_Score": "Sohbet sırasında karşımdaki kişinin ima veya şakalarını anlamakta zorlanırım.",
    "A8_Score": "Tekrarlayan davranışlar veya alışkanlıklarım vardır.",
    "A9_Score": "Yeni insanlarla tanışmak benim için zorlayıcıdır.",
    "A10_Score": "Duyusal uyaranlara karşı hassasiyet yaşarım.",
}

MOODS = ["mutlu", "üzgün", "kaygılı", "sakin", "öfkeli"]


def _render_assessment_result(result: dict, total: int) -> None:
    with ui.card("Sonuç"):
        if result.get("prediction") == 1:
            ui.note(
                "Model, otizm spektrumuyla ilişkili belirtiler açısından dikkat edilmesi "
                "gereken bir örüntü tespit etti. Bu bir tanı değildir — bir uzmanla "
                "görüşmeniz önerilir.",
                "warning",
            )
        else:
            ui.note(
                "Model belirgin bir risk örüntüsü tespit etmedi. Takibi sürdürmeniz önerilir.",
                "success",
            )

        col1, col2 = st.columns(2)
        with col1:
            ui.stat("Toplam puan", f"{total}/10", "evet yanıtı sayısı")
        with col2:
            ui.stat("Kayıt", "Tamamlandı", "geçmişinize eklendi")

        with st.expander("Ham model çıktısı"):
            st.json(result)


def page_assessment() -> None:
    ui.page_head(
        "Otizm tarama testi",
        "10 soruluk kısa tarama. Yanıtlarınız makine öğrenmesi modeliyle değerlendirilir.",
    )
    ui.disclaimer()

    # Sonuç, formun ÜSTÜNDE gösterilir; aksi halde kullanıcı 10 sorunun altına
    # kaydırmadan sonucu göremez.
    if "assessment_result" in st.session_state:
        payload = st.session_state.assessment_result
        _render_assessment_result(payload["result"], payload["total"])

        if st.button("Yeni test yap", type="secondary"):
            del st.session_state.assessment_result
            st.rerun()
        return

    with st.form("adult_assessment"):
        answers = {}

        for index, (key, question) in enumerate(QUESTIONS.items(), start=1):
            st.markdown(f"**{index}.** {question}")
            answer = st.radio(
                question,
                ["Hayır", "Evet"],
                horizontal=True,
                key=f"test_{key}",
                label_visibility="collapsed",
            )
            answers[key] = 1 if answer == "Evet" else 0
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        st.divider()
        age = st.number_input("Yaşınız", min_value=1, max_value=100, value=25)
        submitted = st.form_submit_button("Testi tamamla ve değerlendir", type="primary")

    if not submitted:
        return

    ok, result = api.post(
        "/predict-and-save",
        params={"user_id": st.session_state.user_id},
        json={**answers, "age": age},
    )

    if not ok:
        st.error(result)
        return

    st.session_state.assessment_result = {"result": result, "total": sum(answers.values())}
    st.rerun()


def page_daily_log() -> None:
    ui.page_head(
        "Günlük kayıt",
        "Gününüzü kaydedin. Düzenli kayıtlar AI önerilerini ve gelişim analizini besler.",
    )

    with st.form("daily_log_form"):
        col1, col2 = st.columns(2)

        with col1:
            mood = st.selectbox("Duygu durumu", MOODS)
            sleep_hours = st.number_input("Uyku saati", min_value=0, max_value=24, value=8)
        with col2:
            social_interaction = st.slider("Sosyal etkileşim seviyesi", 0, 10, 5)

        note_text = st.text_area("Günün notu", placeholder="Bugün nasıl geçti?")
        submitted = st.form_submit_button("Kaydı ekle", type="primary")

    if not submitted:
        return

    ok, result = api.post(
        "/daily-log",
        json={
            "user_id": st.session_state.user_id,
            "mood": mood,
            "sleep_hours": sleep_hours,
            "social_interaction": social_interaction,
            "note": note_text,
        },
    )

    if ok:
        st.success("Günlük kayıt eklendi.")
    else:
        st.error(result)


def page_clinical() -> None:
    ui.page_head(
        "Klinik takip formu",
        "Doktorunuzun takip edebilmesi için ayrıntılı günlük klinik gözlem kaydı.",
    )

    with st.form("clinical_form"):
        col1, col2 = st.columns(2)

        with col1:
            meltdown = st.selectbox("Bugün kriz / meltdown yaşandı mı?", ["Hayır", "Evet", "Kısmen"])
            eating_pattern = st.selectbox(
                "Yemek düzeni",
                ["Normal", "Az yedi", "Çok yedi", "Seçici yeme", "Düzensiz"],
            )
            self_harm_risk = st.selectbox(
                "Kendine zarar verme riski",
                ["Hayır", "Evet", "Gözlemlenmedi"],
            )
            medication_therapy = st.text_input("İlaç / terapi takibi")

        with col2:
            sensory_sensitivity = st.slider("Duyusal hassasiyet", 0, 10, 5)
            eye_contact = st.slider("Göz teması", 0, 10, 5)
            communication_willingness = st.slider("İletişim kurma isteği", 0, 10, 5)
            routine_reaction = st.slider("Rutin değişikliğine tepki", 0, 10, 5)
            school_work_performance = st.slider("Okul / iş performansı", 0, 10, 5)

        note_text = st.text_area("Ek klinik not")
        submitted = st.form_submit_button("Klinik kaydı ekle", type="primary")

    if not submitted:
        return

    ok, result = api.post(
        "/clinical-followup",
        json={
            "user_id": st.session_state.user_id,
            "meltdown": meltdown,
            "sensory_sensitivity": sensory_sensitivity,
            "eye_contact": eye_contact,
            "communication_willingness": communication_willingness,
            "routine_reaction": routine_reaction,
            "eating_pattern": eating_pattern,
            "medication_therapy": medication_therapy,
            "school_work_performance": school_work_performance,
            "self_harm_risk": self_harm_risk,
            "note": note_text,
        },
    )

    if ok:
        st.success("Klinik takip kaydı eklendi.")
    else:
        st.error(result)


def page_history() -> None:
    ui.page_head("Geçmiş kayıtlarım", "Tarama sonuçlarınız ve günlük kayıt geçmişiniz.")

    tests_tab, logs_tab = st.tabs(["Tarama testleri", "Günlük kayıtlar"])

    with tests_tab:
        ok, predictions = api.get("/my-predictions", params={"user_id": st.session_state.user_id})

        if not ok:
            st.error(predictions)
        elif not predictions:
            ui.empty("Henüz tamamlanmış tarama testiniz yok.")
        else:
            st.dataframe(pd.DataFrame(predictions), use_container_width=True, hide_index=True)

    with logs_tab:
        ok, logs = api.get("/my-daily-logs", params={"user_id": st.session_state.user_id})

        if not ok:
            st.error(logs)
        elif not logs:
            ui.empty("Henüz günlük kaydınız yok.")
        else:
            logs_df = pd.DataFrame(logs)
            st.dataframe(logs_df, use_container_width=True, hide_index=True)

            if "sleep_hours" in logs_df.columns:
                st.markdown("###### Uyku saati seyri")
                st.line_chart(logs_df["sleep_hours"], height=200)

            if "social_interaction" in logs_df.columns:
                st.markdown("###### Sosyal etkileşim seyri")
                st.line_chart(logs_df["social_interaction"], height=200)


def page_ai_suggestion() -> None:
    ui.page_head("AI önerileri", "Son günlük kaydınıza göre oluşturulan destekleyici geri bildirim.")

    ok, result = api.get("/daily-log-analysis", params={"user_id": st.session_state.user_id})

    if not ok:
        st.error(result)
        return

    if "suggestions" not in result:
        ui.empty(result.get("message", "Analiz için yeterli kayıt bulunmuyor."))
        return

    with ui.card("Son günlük kaydınız"):
        col1, col2, col3 = st.columns(3)
        with col1:
            ui.stat("Duygu durumu", str(result.get("latest_mood", "—")))
        with col2:
            ui.stat("Uyku", f"{result.get('sleep_hours', '—')} sa")
        with col3:
            ui.stat("Sosyal etkileşim", f"{result.get('social_interaction', '—')}/10")

        if result.get("note"):
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown(f"**Notunuz:** {result['note']}")

    with ui.card("Öneriler"):
        for suggestion in result["suggestions"]:
            ui.note(suggestion, "info")


def page_progress() -> None:
    ui.page_head("Gelişim analizi", "Son kayıtlarınız üzerinden bütünsel bir değerlendirme.")
    ui.disclaimer()

    if not st.button("Analizi oluştur", type="primary"):
        return

    with st.spinner("Kayıtlarınız değerlendiriliyor..."):
        ok, result = api.get("/progress-score", params={"user_id": st.session_state.user_id})

    if not ok:
        st.error(result)
        return

    if "analysis" in result:
        with ui.card("Sonuç"):
            ui.note(result["analysis"], "info")
    else:
        ui.empty(result.get("message", "Analiz için yeterli veri yok."))
