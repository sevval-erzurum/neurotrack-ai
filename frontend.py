import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8003"

st.set_page_config(
    page_title="NeuroTrack AI | Deva",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    .stApp {
        background: linear-gradient(180deg, #F3F4F6 0%, #EEF2FF 100%);
        color: #111827;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    .brand-card {
        background: linear-gradient(135deg, #2563EB, #7C3AED);
        padding: 28px;
        border-radius: 24px;
        color: white;
        box-shadow: 0 12px 32px rgba(37, 99, 235, 0.25);
        margin-bottom: 22px;
    }

    .brand-title {
        font-size: 34px;
        font-weight: 900;
        margin-bottom: 6px;
    }

    .brand-subtitle {
        font-size: 16px;
        opacity: 0.92;
        line-height: 1.6;
    }

    .main-card {
        background: #FFFFFF;
        padding: 24px;
        border-radius: 22px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
        border: 1px solid #E5E7EB;
        margin-bottom: 18px;
    }

    .mini-card {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 18px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
        min-height: 130px;
        margin-bottom: 12px;
    }

    .mini-title {
        font-size: 15px;
        color: #6B7280;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .mini-value {
        font-size: 24px;
        color: #111827;
        font-weight: 900;
    }

    .motivation-card {
        background: #FFFBEB;
        border: 1px solid #F59E0B;
        padding: 18px;
        border-radius: 20px;
        margin-bottom: 18px;
    }

    .motivation-title {
        color: #92400E;
        font-size: 20px;
        font-weight: 900;
        margin-bottom: 8px;
    }

    .motivation-text {
        color: #78350F;
        font-size: 15px;
        line-height: 1.7;
    }

    .deva-box {
        background: #FFFFFF;
        border: 1px solid #DDD6FE;
        padding: 18px;
        border-radius: 22px;
        box-shadow: 0 10px 28px rgba(124, 58, 237, 0.12);
        position: sticky;
        top: 20px;
    }

    .deva-header {
        background: linear-gradient(135deg, #7C3AED, #2563EB);
        color: white;
        padding: 14px;
        border-radius: 16px;
        margin-bottom: 14px;
        font-weight: 900;
        font-size: 18px;
    }

    .user-msg {
        background: #DBEAFE;
        border: 1px solid #BFDBFE;
        padding: 12px;
        border-radius: 15px;
        margin: 8px 0;
        color: #111827;
    }

    .ai-msg {
        background: #F5F3FF;
        border: 1px solid #DDD6FE;
        padding: 12px;
        border-radius: 15px;
        margin: 8px 0;
        color: #111827;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #2563EB, #7C3AED);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 0.75rem 1rem;
        font-weight: 900;
        width: 100%;
        min-height: 48px;
    }

    div.stButton > button:hover {
        border: none;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25);
    }

    .logout-button button {
        background: #374151 !important;
    }

    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        border-radius: 12px;
    }

    h1, h2, h3 {
        color: #111827;
        font-weight: 900;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def init_state():
    defaults = {
        "user_id": None,
        "role": None,
        "full_name": None,
        "page": "Giriş Yap",
        "chat_history": []
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()


def logout():
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.full_name = None
    st.session_state.chat_history = []
    st.session_state.page = "Giriş Yap"
    st.rerun()


def brand_header():
    st.markdown(
        """
        <div class="brand-card">
            <div class="brand-title">NeuroTrack AI</div>
            <div class="brand-subtitle">
                Yapay zekâ destekli otizm değerlendirme, günlük takip ve uzman destek platformu
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def card_start():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)


def card_end():
    st.markdown('</div>', unsafe_allow_html=True)


def get_role_title(role):
    if role == "adult":
        return "Yetişkin Kullanıcı Paneli"
    if role == "parent":
        return "Ebeveyn Paneli"
    if role == "doctor":
        return "Doktor Paneli"
    return "Kullanıcı Paneli"


def get_role_welcome():
    if st.session_state.role == "doctor":
        return "Merhaba, ben Deva. Bugün hasta takibi, klinik yorumlama veya kayıt analizi konusunda yardımcı olabilirim."
    if st.session_state.role == "parent":
        return "Merhaba, ben Deva. Bugün çocuk takibi, günlük kayıtlar veya uyarı analizi konusunda yardımcı olabilirim."
    return "Merhaba, ben Deva. Bugün günlük takip, duygu durumu, risk analizi veya öneriler konusunda yardımcı olabilirim."


def render_motivation_card():
    if st.session_state.role != "adult" or st.session_state.user_id is None:
        return

    motivation = None

    try:
        response = requests.get(
            f"{API_URL}/adult-gamification-v2",
            params={"user_id": st.session_state.user_id},
            timeout=5
        )

        if response.status_code != 200:
            response = requests.get(
                f"{API_URL}/adult-gamification",
                params={"user_id": st.session_state.user_id},
                timeout=5
            )

        if response.status_code == 200:
            motivation = response.json()
    except Exception:
        motivation = None

    if motivation:
        streak = motivation.get("current_streak", 0)
        badges = motivation.get("badges", [])
        message = motivation.get("message", "Günlük kayıt girerek takip sürecini sürdürebilirsin.")

        if len(badges) > 0:
            badge_text = ", ".join([badge.get("title", "Rozet") for badge in badges])
        else:
            badge_text = "Henüz rozet yok"
    else:
        streak = 0
        badge_text = "Henüz rozet yok"
        message = "Günlük kayıt girerek serini başlatabilirsin."

    st.markdown(
        f"""
        <div class="motivation-card">
            <div class="motivation-title">Günlük Takip Motivasyonu</div>
            <div class="motivation-text">
                🔥 <b>{streak} günlük seri</b><br>
                🏅 <b>Rozetlerin:</b> {badge_text}<br>
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def send_deva_message(user_message):
    if user_message.strip() == "":
        return

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_message
    })

    data = {
        "user_id": st.session_state.user_id,
        "message": user_message,
        "role": st.session_state.role
    }

    try:
        response = requests.post(f"{API_URL}/chatbot", json=data)

        if response.status_code == 200:
            result = response.json()
            bot_msg = (
                result.get("bot_response")
                or result.get("reply")
                or result.get("message")
                or "Deva şu anda yanıt oluşturamadı."
            )
        else:
            bot_msg = "Deva şu anda backend yanıtı alamadı."
    except Exception:
        bot_msg = "Bağlantı hatası oluştu. Backend çalışıyor mu kontrol edilmelidir."

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": bot_msg
    })


def render_deva_side():
    if st.session_state.user_id is None:
        return

    st.markdown('<div class="deva-box">', unsafe_allow_html=True)
    st.markdown('<div class="deva-header">💬 Deva AI Asistan</div>', unsafe_allow_html=True)

    if len(st.session_state.chat_history) == 0:
        st.markdown(
            f"""
            <div class="ai-msg">
                <b>Deva:</b><br>{get_role_welcome()}
            </div>
            """,
            unsafe_allow_html=True
        )

    recent_messages = st.session_state.chat_history[-6:]

    for msg in recent_messages:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="user-msg">
                    <b>Sen:</b><br>{msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="ai-msg">
                    <b>Deva:</b><br>{msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    with st.form("deva_side_form", clear_on_submit=True):
        user_message = st.text_input("Deva'ya mesaj yaz", key="deva_side_input")
        submitted = st.form_submit_button("Gönder")

        if submitted:
            send_deva_message(user_message)
            st.rerun()

    if st.button("Sohbeti Temizle", key="clear_deva_side"):
        st.session_state.chat_history = []
        st.rerun()

    st.caption("Deva tanı koymaz. Takip ve karar destek amacıyla yardımcı olur.")
    st.markdown('</div>', unsafe_allow_html=True)


def home_button(label, page_name, key):
    if st.button(label, key=key):
        go_to(page_name)


def render_home_buttons():
    st.markdown("### İşlem Menüsü")

    if st.session_state.role == "adult":
        buttons = [
            ("Ana Sayfa", "Ana Sayfa"),
            ("Otizm Testi", "Otizm Testi"),
            ("Günlük Kayıt", "Günlük Kayıt"),
            ("Klinik Takip Formu", "Klinik Takip Formu"),
            ("Geçmişim", "Geçmişim"),
            ("Doktor Notlarım", "Doktor Notlarım"),
            ("Mesajlaşma", "Mesajlaşma"),
            ("AI Öneri", "AI Öneri"),
            ("Gelişim Skoru", "Gelişim Skoru"),
            ("Chatbot", "Chatbot"),
            ("Bildirimlerim", "Bildirimlerim"),
        ]
    elif st.session_state.role == "parent":
        buttons = [
            ("Ana Sayfa", "Ana Sayfa"),
            ("Parent Paneli", "Parent Paneli"),
            ("Çocuk Otizm Testi", "Çocuk Otizm Testi"),
            ("Doktor Notlarım", "Doktor Notlarım"),
            ("Mesajlaşma", "Mesajlaşma"),
            ("Chatbot", "Chatbot"),
            ("Bildirimlerim", "Bildirimlerim"),
        ]
    else:
        buttons = [
            ("Ana Sayfa", "Ana Sayfa"),
            ("Doktor Paneli", "Doktor Paneli"),
            ("Doktor Notlarım", "Doktor Notlarım"),
            ("Mesajlaşma", "Mesajlaşma"),
            ("Chatbot", "Chatbot"),
            ("Bildirimlerim", "Bildirimlerim"),
        ]

    for i in range(0, len(buttons), 3):
        cols = st.columns(3)

        for index, item in enumerate(buttons[i:i + 3]):
            label, page_name = item

            with cols[index]:
                home_button(label, page_name, f"home_btn_{page_name}_{i}_{index}")

    st.markdown(" ")
    if st.button("Çıkış Yap", key="home_logout"):
        logout()


def page_login():
    st.markdown("## Giriş Yap")
    card_start()

    email = st.text_input("Email")
    password = st.text_input("Şifre", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Giriş Yap"):
            data = {
                "email": email,
                "password": password
            }

            response = requests.post(f"{API_URL}/login", json=data)

            if response.status_code == 200:
                result = response.json()

                st.session_state.user_id = result["user_id"]
                st.session_state.role = result["role"]
                st.session_state.full_name = result["full_name"]
                st.session_state.page = "Ana Sayfa"

                st.success("Giriş başarılı")
                st.rerun()
            else:
                try:
                    st.error(response.json())
                except Exception:
                    st.error(response.text)

    with col2:
        if st.button("Kayıt Ol Sayfasına Git"):
            go_to("Kayıt Ol")

    card_end()


def page_register():
    st.markdown("## Kayıt Ol")
    card_start()

    full_name = st.text_input("Ad Soyad")
    email = st.text_input("Email")
    password = st.text_input("Şifre", type="password")
    role = st.selectbox("Rol", ["adult", "parent", "doctor"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Kayıt Ol"):
            data = {
                "full_name": full_name,
                "email": email,
                "password": password,
                "role": role
            }

            response = requests.post(f"{API_URL}/register", json=data)

            if response.status_code == 200:
                st.success("Kayıt başarılı. Giriş yapabilirsiniz.")
                st.json(response.json())
            else:
                try:
                    st.error(response.json())
                except Exception:
                    st.error(response.text)

    with col2:
        if st.button("Giriş Sayfasına Git"):
            go_to("Giriş Yap")

    card_end()


def page_home():
    st.markdown("## Ana Sayfa")

    card_start()

    st.markdown(f"### Hoş geldin, {st.session_state.full_name}")
    st.markdown(f"**Aktif Rol:** {get_role_title(st.session_state.role)}")

    if st.session_state.role == "doctor":
        st.info("Bu panelden yetişkin ve çocuk hastalarınızı takip edebilir, doktor notları ekleyebilir ve hasta süreçlerini görüntüleyebilirsiniz.")
    elif st.session_state.role == "parent":
        st.info("Bu panelden çocuğunuzu ekleyebilir, günlük takip kayıtları oluşturabilir ve çocuk gelişim sürecini izleyebilirsiniz.")
    else:
        st.info("Bu panelden otizm tarama testi yapabilir, günlük kayıt girebilir, gelişim durumunuzu takip edebilir ve Deva AI asistanından destek alabilirsiniz.")

    card_end()

    render_motivation_card()
    render_home_buttons()


def page_autism_test():
    st.markdown("## Otizm Tarama Testi")
    card_start()

    st.info(
        "Bu test yalnızca ön tarama amacı taşır. Kesin tanı koymaz. "
        "Sonuçlar uzman değerlendirmesinin yerine geçmez."
    )

    questions = {
        "A1_Score": "Sosyal ortamlarda diğer insanlarla iletişim kurmakta zorlanırım.",
        "A2_Score": "Göz teması kurmakta veya sürdürmekte zorlanırım.",
        "A3_Score": "Rutinlerimin değişmesi beni rahatsız eder.",
        "A4_Score": "Başkalarının duygu ve düşüncelerini anlamakta zorlanırım.",
        "A5_Score": "Belirli konulara yoğun ve uzun süreli ilgi duyarım.",
        "A6_Score": "Kalabalık veya gürültülü ortamlarda rahatsız olurum.",
        "A7_Score": "Sohbet sırasında karşımdaki kişinin ima veya şakalarını anlamakta zorlanırım.",
        "A8_Score": "Tekrarlayan davranışlar veya alışkanlıklarım vardır.",
        "A9_Score": "Yeni insanlarla tanışmak benim için zorlayıcıdır.",
        "A10_Score": "Duyusal uyaranlara karşı hassasiyet yaşarım."
    }

    answers = {}

    for key, question in questions.items():
        answer = st.radio(question, ["Hayır", "Evet"], key=f"test_{key}")
        answers[key] = 1 if answer == "Evet" else 0

    age = st.number_input("Yaş", min_value=1, max_value=100, value=25)

    if st.button("Testi Kaydet ve Tahmin Et"):
        data = {
            "A1_Score": answers["A1_Score"],
            "A2_Score": answers["A2_Score"],
            "A3_Score": answers["A3_Score"],
            "A4_Score": answers["A4_Score"],
            "A5_Score": answers["A5_Score"],
            "A6_Score": answers["A6_Score"],
            "A7_Score": answers["A7_Score"],
            "A8_Score": answers["A8_Score"],
            "A9_Score": answers["A9_Score"],
            "A10_Score": answers["A10_Score"],
            "age": age
        }

        response = requests.post(
            f"{API_URL}/predict-and-save",
            params={"user_id": st.session_state.user_id},
            json=data
        )

        if response.status_code == 200:
            result = response.json()
            st.success("Test sonucu başarıyla kaydedildi.")

            if result["prediction"] == 1:
                st.warning("Model sonucuna göre otizm riski görülebilir. Kesin tanı değildir.")
            else:
                st.success("Model sonucuna göre yüksek risk görünmemektedir.")

            st.json(result)
        else:
            try:
                st.error(response.json())
            except Exception:
                st.error(response.text)

    card_end()


def page_daily_log():
    st.markdown("## Günlük Duygu Durumu Kaydı")
    render_motivation_card()

    card_start()

    mood = st.selectbox("Duygu Durumu", ["mutlu", "üzgün", "kaygılı", "sakin", "öfkeli"])
    sleep_hours = st.number_input("Uyku Saati", min_value=0, max_value=24, value=8)
    social_interaction = st.slider("Sosyal Etkileşim Seviyesi", 0, 10, 5)
    note = st.text_area("Günlük Not")

    if st.button("Günlük Kaydı Ekle"):
        data = {
            "user_id": st.session_state.user_id,
            "mood": mood,
            "sleep_hours": sleep_hours,
            "social_interaction": social_interaction,
            "note": note
        }

        response = requests.post(f"{API_URL}/daily-log", json=data)

        if response.status_code == 200:
            st.success("Günlük kayıt eklendi.")
            st.json(response.json())
        else:
            try:
                st.error(response.json())
            except Exception:
                st.error(response.text)

    card_end()


def page_clinical_followup():
    st.markdown("## Klinik Takip Formu")
    card_start()

    meltdown = st.selectbox("Bugün kriz / meltdown yaşandı mı?", ["Hayır", "Evet", "Kısmen"])
    sensory_sensitivity = st.slider("Duyusal hassasiyet seviyesi", 0, 10, 5)
    eye_contact = st.slider("Göz teması seviyesi", 0, 10, 5)
    communication_willingness = st.slider("İletişim kurma isteği", 0, 10, 5)
    routine_reaction = st.slider("Rutin değişikliğine tepki seviyesi", 0, 10, 5)
    eating_pattern = st.selectbox("Yemek düzeni", ["Normal", "Az yedi", "Çok yedi", "Seçici yeme", "Düzensiz"])
    medication_therapy = st.text_input("İlaç / terapi takibi")
    school_work_performance = st.slider("Okul / iş performansı", 0, 10, 5)
    self_harm_risk = st.selectbox("Kendine zarar verme riski var mı?", ["Hayır", "Evet", "Gözlemlenmedi"])
    note = st.text_area("Ek klinik not")

    if st.button("Klinik Takip Kaydını Ekle"):
        data = {
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
            "note": note
        }

        response = requests.post(f"{API_URL}/clinical-followup", json=data)

        if response.status_code == 200:
            st.success("Klinik takip kaydı başarıyla eklendi.")
            st.json(response.json())
        else:
            try:
                st.error(response.json())
            except Exception:
                st.error(response.text)

    card_end()


def page_history():
    st.markdown("## Geçmiş Kayıtlarım")
    card_start()

    st.subheader("Otizm Test Sonuçlarım")

    prediction_response = requests.get(
        f"{API_URL}/my-predictions",
        params={"user_id": st.session_state.user_id}
    )

    if prediction_response.status_code == 200:
        predictions = prediction_response.json()

        if len(predictions) == 0:
            st.info("Henüz test sonucunuz yok.")
        else:
            prediction_df = pd.DataFrame(predictions)
            st.dataframe(prediction_df, use_container_width=True)
    else:
        st.error(prediction_response.text)

    st.divider()
    st.subheader("Günlük Duygu Durumu Kayıtlarım")

    log_response = requests.get(
        f"{API_URL}/my-daily-logs",
        params={"user_id": st.session_state.user_id}
    )

    if log_response.status_code == 200:
        logs = log_response.json()

        if len(logs) == 0:
            st.info("Henüz günlük kayıt yok.")
        else:
            logs_df = pd.DataFrame(logs)
            st.dataframe(logs_df, use_container_width=True)
    else:
        st.error(log_response.text)

    card_end()


def page_ai_suggestion():
    st.markdown("## AI Destekli Günlük Yorum")
    card_start()

    response = requests.get(
        f"{API_URL}/daily-log-analysis",
        params={"user_id": st.session_state.user_id}
    )

    if response.status_code == 200:
        result = response.json()

        if "suggestions" in result:
            st.subheader("Son Günlük Kaydın")
            st.write(f"**Duygu Durumu:** {result['latest_mood']}")
            st.write(f"**Uyku:** {result['sleep_hours']} saat")
            st.write(f"**Sosyal Etkileşim:** {result['social_interaction']}")
            st.write(f"**Not:** {result['note']}")

            st.subheader("Öneriler")
            for suggestion in result["suggestions"]:
                st.info(suggestion)
        else:
            st.info(result["message"])
    else:
        st.error(response.text)

    card_end()


def page_progress_score():
    st.markdown("## AI Gelişim Analizi")
    card_start()

    st.info(
        "Bu analiz son günlük kayıtlar üzerinden destekleyici bir değerlendirme sunar. "
        "Tanı veya tıbbi karar yerine geçmez."
    )

    if st.button("Analiz Oluştur"):
        response = requests.get(
            f"{API_URL}/progress-score",
            params={"user_id": st.session_state.user_id}
        )

        if response.status_code == 200:
            result = response.json()

            if "analysis" in result:
                st.subheader("Sonuç")
                st.info(result["analysis"])
            else:
                st.warning(result["message"])
        else:
            st.error(response.text)

    card_end()


def page_chatbot():
    st.markdown("## Deva AI Asistan")

    st.markdown(
        f"""
        <div class="ai-msg">
            <b>Deva:</b><br>{get_role_welcome()}
        </div>
        """,
        unsafe_allow_html=True
    )

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="user-msg">
                    <b>Sen:</b><br>{msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="ai-msg">
                    <b>Deva:</b><br>{msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    with st.form("deva_full_form", clear_on_submit=True):
        user_message = st.text_input("Deva'ya mesaj yaz", key="deva_full_input")
        submitted = st.form_submit_button("Gönder")

        if submitted:
            send_deva_message(user_message)
            st.rerun()

    if st.button("Sohbeti Temizle", key="clear_deva_full"):
        st.session_state.chat_history = []
        st.rerun()

    st.caption("Deva tanı koymaz. Sadece takip, bilgilendirme ve karar destek amacıyla yardımcı olur.")


def page_notifications():
    st.markdown("## Bildirimlerim")
    card_start()

    response = requests.get(
        f"{API_URL}/notifications",
        params={"user_id": st.session_state.user_id}
    )

    if response.status_code == 200:
        notifications = response.json()

        if len(notifications) == 0:
            st.info("Bildirim yok.")
        else:
            for notification in notifications:
                created_at = notification.get("created_at", "-")
                title = notification.get("title", "-")
                message = notification.get("message", "-")

                if notification["is_read"]:
                    st.success(f"{title} - {message}")
                else:
                    st.warning(f"{title} - {message}")

                st.caption(f"Tarih: {created_at}")

                if not notification["is_read"]:
                    if st.button(f"Okundu İşaretle #{notification['id']}"):
                        mark_response = requests.post(
                            f"{API_URL}/mark-notification-read",
                            params={"notification_id": notification["id"]}
                        )

                        if mark_response.status_code == 200:
                            st.rerun()
                        else:
                            st.error(mark_response.text)

                st.divider()
    else:
        st.error(response.text)

    card_end()


def page_child_autism_test():
    st.markdown("## Çocuk Otizm Ön Tarama Testi")

    if st.session_state.role != "parent":
        st.error("Bu alan sadece ebeveyn kullanıcılar içindir.")
        return

    card_start()

    st.info(
        "Bu ekran çocuklar için makine öğrenmesi tabanlı ön tarama amacıyla hazırlanmıştır. "
        "Sonuç kesin tanı değildir; uzman değerlendirmesinin yerine geçmez."
    )

    children_response = requests.get(
        f"{API_URL}/children",
        params={"parent_id": st.session_state.user_id}
    )

    if children_response.status_code != 200:
        st.error(children_response.text)
        card_end()
        return

    children = children_response.json()

    if len(children) == 0:
        st.warning("Henüz kayıtlı çocuk bulunmuyor. Önce Parent Paneli üzerinden çocuk ekleyin.")
        card_end()
        return

    child_options = {
        f"{child.get('name', 'Çocuk')} - {child.get('age', '-')} yaş (ID: {child.get('id')})": child
        for child in children
    }

    selected_child_label = st.selectbox("Test yapılacak çocuğu seç", list(child_options.keys()))
    selected_child = child_options[selected_child_label]
    selected_child_id = selected_child["id"]
    selected_child_age = int(selected_child.get("age", 0) or 0)

    st.markdown(f"### Seçilen Çocuk: {selected_child.get('name', '-')}")
    st.write(f"**Yaş:** {selected_child_age}")

    st.divider()
    st.subheader("Çocuk Test Soruları")

    questions = {
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

    answers = {}

    for key, question in questions.items():
        answer = st.radio(
            question,
            ["Hayır", "Evet"],
            horizontal=True,
            key=f"child_test_{selected_child_id}_{key}"
        )
        answers[key] = 1 if answer == "Evet" else 0

    if st.button("Çocuk Testini Kaydet ve ML Tahmini Yap"):
        data = {
            "child_id": selected_child_id,
            "A1_Score": answers["A1_Score"],
            "A2_Score": answers["A2_Score"],
            "A3_Score": answers["A3_Score"],
            "A4_Score": answers["A4_Score"],
            "A5_Score": answers["A5_Score"],
            "A6_Score": answers["A6_Score"],
            "A7_Score": answers["A7_Score"],
            "A8_Score": answers["A8_Score"],
            "A9_Score": answers["A9_Score"],
            "A10_Score": answers["A10_Score"],
            "age": selected_child_age,
        }

        test_response = requests.post(f"{API_URL}/child-autism-test", json=data)

        if test_response.status_code == 200:
            result = test_response.json()
            risk_level = result.get("risk_level", "-")
            result_text = result.get("result_text", "")
            probability = result.get("probability")

            st.success("Çocuk otizm ön tarama testi başarıyla kaydedildi.")

            if risk_level == "Yüksek":
                st.error(f"Risk Düzeyi: {risk_level}")
            elif risk_level == "Orta":
                st.warning(f"Risk Düzeyi: {risk_level}")
            else:
                st.success(f"Risk Düzeyi: {risk_level}")

            st.write(f"**Toplam Soru Puanı:** {result.get('total_score', '-')}/10")

            if probability is not None:
                st.write(f"**Model Güven Skoru:** {probability:.2f}")

            st.info(result_text)
            st.json(result)
        else:
            try:
                st.error(test_response.json())
            except Exception:
                st.error(test_response.text)

    st.divider()
    st.subheader("Çocuk Test Geçmişi")

    history_response = requests.get(
        f"{API_URL}/child-autism-tests",
        params={"child_id": selected_child_id}
    )

    if history_response.status_code == 200:
        history = history_response.json()

        if len(history) == 0:
            st.info("Bu çocuk için henüz test kaydı bulunmuyor.")
        else:
            history_df = pd.DataFrame(history)
            st.dataframe(history_df, use_container_width=True)

            for item in history:
                st.markdown(f"### Test #{item.get('id')}")
                st.write(f"**Risk Düzeyi:** {item.get('risk_level', '-')}")
                st.write(f"**Toplam Puan:** {item.get('total_score', '-')}/10")
                st.write(f"**Sonuç:** {item.get('result_text', '-')}")
                st.caption(f"Tarih: {item.get('created_at', '-')}")
                st.divider()
    else:
        st.error(history_response.text)

    card_end()


def page_parent_panel():
    st.markdown("## Ebeveyn Paneli")

    if st.session_state.role != "parent":
        st.error("Bu alan sadece ebeveynler içindir.")
        return

    card_start()

    st.success(f"Ebeveyn olarak giriş yaptınız: {st.session_state.full_name}")

    st.subheader("Çocuk Ekle")

    child_name = st.text_input("Çocuğun Adı")
    child_age = st.number_input("Çocuğun Yaşı", min_value=1, max_value=18, value=7)
    child_gender = st.selectbox("Çocuğun Cinsiyeti", ["Kız", "Erkek", "Belirtmek istemiyorum"])

    if st.button("Çocuğu Ekle"):
        data = {
            "parent_id": st.session_state.user_id,
            "name": child_name,
            "age": child_age,
            "gender": child_gender
        }

        response = requests.post(f"{API_URL}/children", json=data)

        if response.status_code == 200:
            st.success("Çocuk başarıyla eklendi.")
            st.json(response.json())
        else:
            try:
                st.error(response.json())
            except Exception:
                st.error(response.text)

    st.divider()
    st.subheader("Çocuklarım")

    children_response = requests.get(
        f"{API_URL}/children",
        params={"parent_id": st.session_state.user_id}
    )

    if children_response.status_code == 200:
        children = children_response.json()

        if len(children) == 0:
            st.info("Henüz kayıtlı çocuk yok.")
        else:
            children_df = pd.DataFrame(children)
            st.dataframe(children_df, use_container_width=True)

            child_options = {
                f"{child['name']} (ID: {child['id']})": child["id"]
                for child in children
            }

            selected_child_label = st.selectbox("Çocuk seç", list(child_options.keys()))
            selected_child_id = child_options[selected_child_label]

            st.divider()
            st.subheader("Çocuk Günlük Kaydı")

            child_mood = st.selectbox(
                "Duygu Durumu",
                ["mutlu", "üzgün", "kaygılı", "sakin", "öfkeli"],
                key="child_mood"
            )
            child_sleep_hours = st.number_input(
                "Uyku Saati",
                min_value=0,
                max_value=24,
                value=8,
                key="child_sleep_hours"
            )
            child_social_interaction = st.slider(
                "Sosyal Etkileşim",
                0,
                10,
                5,
                key="child_social_interaction"
            )
            child_note = st.text_area("Not", key="child_note")

            if st.button("Çocuk Günlük Kaydı Ekle"):
                data = {
                    "child_id": selected_child_id,
                    "mood": child_mood,
                    "sleep_hours": child_sleep_hours,
                    "social_interaction": child_social_interaction,
                    "note": child_note
                }

                response = requests.post(f"{API_URL}/child-daily-log", json=data)

                if response.status_code == 200:
                    st.success("Çocuk günlük kaydı eklendi.")
                    st.json(response.json())
                else:
                    try:
                        st.error(response.json())
                    except Exception:
                        st.error(response.text)

            st.divider()
            st.subheader("Çocuk Geçmişi")

            if st.button("Çocuk Günlük Geçmişini Göster"):
                logs_response = requests.get(
                    f"{API_URL}/child-daily-logs",
                    params={"child_id": selected_child_id}
                )

                if logs_response.status_code == 200:
                    logs = logs_response.json()

                    if len(logs) == 0:
                        st.info("Kayıt yok.")
                    else:
                        logs_df = pd.DataFrame(logs)
                        st.dataframe(logs_df, use_container_width=True)

                        if "sleep_hours" in logs_df.columns:
                            st.line_chart(logs_df["sleep_hours"])

                        if "social_interaction" in logs_df.columns:
                            st.line_chart(logs_df["social_interaction"])
                else:
                    st.error(logs_response.text)

            if st.button("Çocuk Uyarılarını Göster"):
                alert_response = requests.get(
                    f"{API_URL}/child-alerts",
                    params={"child_id": selected_child_id}
                )

                if alert_response.status_code == 200:
                    alert_result = alert_response.json()

                    for alert in alert_result["alerts"]:
                        if "belirgin bir takip uyarısı görünmüyor" in alert:
                            st.success(alert)
                        else:
                            st.warning(alert)
                else:
                    st.error(alert_response.text)

    else:
        st.error(children_response.text)

    card_end()


def page_doctor_panel():
    st.markdown("## Doktor Paneli")

    if st.session_state.role != "doctor":
        st.error("Bu alan sadece doktorlar içindir.")
        return

    card_start()

    st.success(f"Doktor olarak giriş yaptınız: {st.session_state.full_name}")

    doctor_panel_choice = st.radio(
        "Takip türü seç",
        ["Yetişkin Hasta Takibi", "Çocuk Hasta Takibi"],
        horizontal=True
    )

    if doctor_panel_choice == "Yetişkin Hasta Takibi":
        st.subheader("Yetişkin Hastayı Doktora Ekle")

        patient_id_to_add = st.number_input(
            "Eklemek istediğin yetişkin hasta ID",
            min_value=1,
            step=1,
            key="patient_id_to_add"
        )

        if st.button("Yetişkin Hastayı Ekle"):
            add_response = requests.post(
                f"{API_URL}/add-patient",
                params={
                    "doctor_id": st.session_state.user_id,
                    "patient_id": patient_id_to_add
                }
            )

            if add_response.status_code == 200:
                st.success("Yetişkin hasta başarıyla eklendi.")
                st.json(add_response.json())
            else:
                try:
                    st.error(add_response.json())
                except Exception:
                    st.error(add_response.text)

        st.divider()
        st.subheader("Yetişkin Hastalarım")

        patients_response = requests.get(
            f"{API_URL}/my-patients",
            params={"doctor_id": st.session_state.user_id}
        )

        if patients_response.status_code == 200:
            patients = patients_response.json()

            if len(patients) == 0:
                st.info("Henüz kayıtlı yetişkin hastanız yok.")
            else:
                patients_df = pd.DataFrame(patients)
                st.dataframe(patients_df, use_container_width=True)

                patient_id = st.number_input(
                    "Detayını görmek istediğin yetişkin hasta ID",
                    min_value=1,
                    step=1,
                    key="patient_detail_id"
                )

                if st.button("Yetişkin Hasta Detaylarını Getir"):
                    detail_response = requests.get(
                        f"{API_URL}/patient-details",
                        params={"patient_id": patient_id}
                    )

                    if detail_response.status_code == 200:
                        details = detail_response.json()

                        st.subheader("Tahmin Geçmişi")
                        predictions = details["predictions"]

                        if len(predictions) == 0:
                            st.info("Bu hastanın henüz tahmin kaydı yok.")
                        else:
                            prediction_df = pd.DataFrame(predictions)
                            st.dataframe(prediction_df, use_container_width=True)

                        st.divider()
                        st.subheader("Günlük Kayıtlar")
                        logs = details["daily_logs"]

                        if len(logs) == 0:
                            st.info("Bu hastanın henüz günlük kaydı yok.")
                        else:
                            logs_df = pd.DataFrame(logs)
                            st.dataframe(logs_df, use_container_width=True)

                            if "mood" in logs_df.columns:
                                st.subheader("Duygu Durumu Dağılımı")
                                st.bar_chart(logs_df["mood"].value_counts())

                            if "sleep_hours" in logs_df.columns:
                                st.subheader("Uyku Saati Grafiği")
                                st.line_chart(logs_df["sleep_hours"])

                            if "social_interaction" in logs_df.columns:
                                st.subheader("Sosyal Etkileşim Grafiği")
                                st.line_chart(logs_df["social_interaction"])
                    else:
                        st.error(detail_response.text)

                st.divider()
                st.subheader("Yetişkin Hasta İçin Doktor Notu Ekle")

                adult_note = st.text_area("Doktor Notu", key="adult_doctor_note")
                adult_recommendation = st.text_area("Öneri / Takip Planı", key="adult_recommendation")
                adult_next_visit = st.text_input(
                    "Sonraki Görüşme Tarihi",
                    placeholder="2026-05-10",
                    key="adult_next_visit"
                )

                if st.button("Yetişkin Hasta Notunu Kaydet"):
                    data = {
                        "doctor_id": st.session_state.user_id,
                        "patient_id": patient_id,
                        "child_id": None,
                        "note": adult_note,
                        "recommendation": adult_recommendation,
                        "next_visit_date": adult_next_visit
                    }

                    note_response = requests.post(f"{API_URL}/doctor-note", json=data)

                    if note_response.status_code == 200:
                        st.success("Doktor notu kaydedildi.")
                    else:
                        st.error(note_response.text)
        else:
            st.error(patients_response.text)

    else:
        st.subheader("Çocuk Hastayı Doktora Ekle")

        child_id_to_add = st.number_input(
            "Eklemek istediğin çocuk hasta ID",
            min_value=1,
            step=1,
            key="child_id_to_add"
        )

        if st.button("Çocuk Hastayı Ekle"):
            child_add_response = requests.post(
                f"{API_URL}/add-child-patient",
                params={
                    "doctor_id": st.session_state.user_id,
                    "child_id": child_id_to_add
                }
            )

            if child_add_response.status_code == 200:
                st.success("Çocuk hasta başarıyla eklendi.")
                st.json(child_add_response.json())
            else:
                try:
                    st.error(child_add_response.json())
                except Exception:
                    st.error(child_add_response.text)

        st.divider()
        st.subheader("Çocuk Hastalarım")

        child_patients_response = requests.get(
            f"{API_URL}/my-child-patients",
            params={"doctor_id": st.session_state.user_id}
        )

        if child_patients_response.status_code == 200:
            child_patients = child_patients_response.json()

            if len(child_patients) == 0:
                st.info("Henüz kayıtlı çocuk hastanız yok.")
            else:
                child_patients_df = pd.DataFrame(child_patients)
                st.dataframe(child_patients_df, use_container_width=True)

                selected_child_id = st.number_input(
                    "Detayını görmek istediğin çocuk hasta ID",
                    min_value=1,
                    step=1,
                    key="selected_child_patient_id"
                )

                if st.button("Çocuk Hasta Detaylarını Getir"):
                    child_detail_response = requests.get(
                        f"{API_URL}/child-patient-details",
                        params={"child_id": selected_child_id}
                    )

                    if child_detail_response.status_code == 200:
                        child_details = child_detail_response.json()

                        st.subheader("Çocuk Bilgileri")
                        st.json(child_details["child"])

                        st.subheader("Çocuk Günlük Kayıtları")
                        child_logs = child_details["daily_logs"]

                        if len(child_logs) == 0:
                            st.info("Bu çocuk hasta için henüz günlük kayıt yok.")
                        else:
                            child_logs_df = pd.DataFrame(child_logs)
                            st.dataframe(child_logs_df, use_container_width=True)

                            if "sleep_hours" in child_logs_df.columns:
                                st.line_chart(child_logs_df["sleep_hours"])

                            if "social_interaction" in child_logs_df.columns:
                                st.line_chart(child_logs_df["social_interaction"])

                        st.divider()
                        st.subheader("Çocuk Otizm Test Geçmişi")

                        child_test_response = requests.get(
                            f"{API_URL}/child-autism-tests",
                            params={"child_id": selected_child_id}
                        )

                        if child_test_response.status_code == 200:
                            child_tests = child_test_response.json()

                            if len(child_tests) == 0:
                                st.info("Bu çocuk hasta için henüz otizm test kaydı yok.")
                            else:
                                child_tests_df = pd.DataFrame(child_tests)
                                st.dataframe(child_tests_df, use_container_width=True)

                                for test in child_tests:
                                    st.write(f"**Risk Düzeyi:** {test.get('risk_level', '-')}")
                                    st.write(f"**Toplam Puan:** {test.get('total_score', '-')}/10")
                                    st.write(f"**Sonuç:** {test.get('result_text', '-')}")
                                    st.caption(f"Tarih: {test.get('created_at', '-')}")
                                    st.divider()
                        else:
                            st.error(child_test_response.text)
                    else:
                        st.error(child_detail_response.text)

                st.divider()
                st.subheader("Çocuk Hasta İçin Doktor Notu Ekle")

                child_note = st.text_area("Doktor Notu", key="child_doctor_note")
                child_recommendation = st.text_area("Öneri / Takip Planı", key="child_recommendation")
                child_next_visit = st.text_input(
                    "Sonraki Görüşme Tarihi",
                    placeholder="2026-05-10",
                    key="child_next_visit"
                )

                if st.button("Çocuk Hasta Notunu Kaydet"):
                    data = {
                        "doctor_id": st.session_state.user_id,
                        "patient_id": None,
                        "child_id": selected_child_id,
                        "note": child_note,
                        "recommendation": child_recommendation,
                        "next_visit_date": child_next_visit
                    }

                    note_response = requests.post(f"{API_URL}/doctor-note", json=data)

                    if note_response.status_code == 200:
                        st.success("Çocuk hasta için doktor notu kaydedildi.")
                    else:
                        st.error(note_response.text)
        else:
            st.error(child_patients_response.text)

    card_end()


def page_doctor_notes():
    st.markdown("## Doktor Notlarım")
    card_start()

    response = requests.get(
        f"{API_URL}/my-doctor-notes",
        params={"user_id": st.session_state.user_id}
    )

    if response.status_code != 200:
        st.error(response.text)
        card_end()
        return

    notes = response.json()

    if len(notes) == 0:
        st.info("Henüz doktor notu bulunmuyor.")
        card_end()
        return

    for note in notes:
        doctor_name = note.get("doctor_name", "Doktor")
        target_name = note.get("target_name", "Hasta")
        created_at = note.get("created_at", "-")
        next_visit_date = note.get("next_visit_date", "-")
        note_text = note.get("note", "-")
        recommendation = note.get("recommendation", "-")

        st.markdown(f"### {target_name}")
        st.write(f"**Doktor:** {doctor_name}")
        st.write(f"**Tarih:** {created_at}")
        st.write(f"**Doktor Notu:** {note_text}")
        st.write(f"**Öneri / Takip Planı:** {recommendation}")
        st.warning(f"Sonraki Görüşme Tarihi: {next_visit_date}")
        st.divider()

    card_end()


def render_message_request_panel():
    st.subheader("Mesajlaşma İstekleri")

    requests_response = requests.get(
        f"{API_URL}/message-requests",
        params={"user_id": st.session_state.user_id}
    )

    if requests_response.status_code != 200:
        st.error(requests_response.text)
        return

    requests_data = requests_response.json()

    if len(requests_data) == 0:
        st.info("Mesajlaşma isteği bulunmuyor.")
        return

    for req in requests_data:
        status = req.get("status", "-")
        sender_name = req.get("sender_name", "-")
        receiver_name = req.get("receiver_name", "-")
        request_id = req.get("id")

        st.write(f"**İstek:** {sender_name} → {receiver_name}")
        st.write(f"**Durum:** {status}")

        if st.session_state.role == "doctor" and req.get("receiver_id") == st.session_state.user_id and status == "pending":
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Kabul Et #{request_id}", key=f"accept_req_{request_id}"):
                    response = requests.post(
                        f"{API_URL}/respond-message-request",
                        params={
                            "request_id": request_id,
                            "status": "accepted",
                            "user_id": st.session_state.user_id,
                        }
                    )
                    if response.status_code == 200:
                        st.success("Mesajlaşma isteği kabul edildi.")
                        st.rerun()
                    else:
                        st.error(response.text)

            with col2:
                if st.button(f"Reddet #{request_id}", key=f"reject_req_{request_id}"):
                    response = requests.post(
                        f"{API_URL}/respond-message-request",
                        params={
                            "request_id": request_id,
                            "status": "rejected",
                            "user_id": st.session_state.user_id,
                        }
                    )
                    if response.status_code == 200:
                        st.warning("Mesajlaşma isteği reddedildi.")
                        st.rerun()
                    else:
                        st.error(response.text)

        st.divider()


def render_available_doctors_for_request():
    if st.session_state.role == "doctor":
        return

    st.subheader("Atanmış Doktorlar")

    response = requests.get(
        f"{API_URL}/available-doctors-for-message",
        params={"user_id": st.session_state.user_id}
    )

    if response.status_code != 200:
        st.info("Mesaj isteği gönderebileceğiniz doktor bulunamadı veya bu rol için desteklenmiyor.")
        return

    doctors = response.json()

    if len(doctors) == 0:
        st.info("Mesaj isteği gönderebileceğiniz atanmış doktor bulunmuyor. Önce doktorun sizi hasta listesine eklemesi gerekir.")
        return

    for doctor in doctors:
        doctor_id = doctor.get("user_id")
        status = doctor.get("request_status", "none")
        st.write(f"**{doctor.get('full_name', 'Doktor')}** - {doctor.get('email', '-')}")
        st.write(f"**Mesajlaşma durumu:** {status}")

        if status == "none":
            if st.button(f"Mesajlaşma İsteği Gönder #{doctor_id}", key=f"send_req_{doctor_id}"):
                req_response = requests.post(
                    f"{API_URL}/send-message-request",
                    json={
                        "sender_id": st.session_state.user_id,
                        "receiver_id": doctor_id,
                    }
                )
                if req_response.status_code == 200:
                    st.success("Mesajlaşma isteği doktora gönderildi.")
                    st.rerun()
                else:
                    st.error(req_response.text)
        elif status == "pending":
            st.info("Mesajlaşma isteğiniz doktor onayı bekliyor.")
        elif status == "accepted":
            st.success("Mesajlaşma onaylandı. Aşağıdaki sohbet alanından mesaj gönderebilirsiniz.")
        elif status == "rejected":
            st.warning("Mesajlaşma isteğiniz reddedildi.")

        st.divider()


def page_messaging():
    st.markdown("## Mesajlaşma")
    card_start()

    st.info("Bu alan doktor-hasta mesajlaşması içindir. Mesajlaşma için önce hasta mesaj isteği gönderir, doktor isteği kabul eder.")

    render_message_request_panel()
    render_available_doctors_for_request()

    st.subheader("Sohbetlerim")

    contacts_response = requests.get(
        f"{API_URL}/message-contacts",
        params={"user_id": st.session_state.user_id}
    )

    if contacts_response.status_code != 200:
        st.error(contacts_response.text)
        card_end()
        return

    contacts = contacts_response.json()

    if len(contacts) == 0:
        st.info("Henüz onaylanmış mesajlaşma kişisi yok.")
        card_end()
        return

    contact_options = {
        f"{contact.get('full_name', 'Kullanıcı')} ({contact.get('role', '-')}) - ID: {contact.get('user_id')}": contact.get("user_id")
        for contact in contacts
    }

    selected_label = st.selectbox("Sohbet kişisi seç", list(contact_options.keys()))
    selected_user_id = contact_options[selected_label]

    conversation_response = requests.get(
        f"{API_URL}/secure-conversation",
        params={
            "user1_id": st.session_state.user_id,
            "user2_id": selected_user_id,
        }
    )

    if conversation_response.status_code == 200:
        messages = conversation_response.json()

        if len(messages) == 0:
            st.info("Henüz mesaj yok. İlk mesajı gönderebilirsiniz.")
        else:
            for msg in messages:
                sender_name = msg.get("sender_name", "-")
                content = msg.get("content", "")
                created_at = msg.get("created_at", "-")

                if msg.get("sender_id") == st.session_state.user_id:
                    st.markdown(
                        f"""
                        <div class="user-msg">
                            <b>Sen</b> <small>{created_at}</small><br>{content}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="ai-msg">
                            <b>{sender_name}</b> <small>{created_at}</small><br>{content}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    else:
        st.error(conversation_response.text)

    with st.form("secure_message_form", clear_on_submit=True):
        content = st.text_area("Mesaj yaz", key="secure_message_content")
        submitted = st.form_submit_button("Mesajı Gönder")

        if submitted:
            send_response = requests.post(
                f"{API_URL}/secure-send-message",
                json={
                    "sender_id": st.session_state.user_id,
                    "receiver_id": selected_user_id,
                    "content": content,
                }
            )

            if send_response.status_code == 200:
                st.success("Mesaj gönderildi.")
                st.rerun()
            else:
                st.error(send_response.text)

    card_end()


def render_page():
    page = st.session_state.page

    if page == "Ana Sayfa":
        page_home()
    elif page == "Otizm Testi":
        page_autism_test()
    elif page == "Günlük Kayıt":
        page_daily_log()
    elif page == "Klinik Takip Formu":
        page_clinical_followup()
    elif page == "Geçmişim":
        page_history()
    elif page == "Doktor Notlarım":
        page_doctor_notes()
    elif page == "Mesajlaşma":
        page_messaging()
    elif page == "AI Öneri":
        page_ai_suggestion()
    elif page == "Gelişim Skoru":
        page_progress_score()
    elif page == "Chatbot":
        page_chatbot()
    elif page == "Bildirimlerim":
        page_notifications()
    elif page == "Parent Paneli":
        page_parent_panel()
    elif page == "Çocuk Otizm Testi":
        page_child_autism_test()
    elif page == "Doktor Paneli":
        page_doctor_panel()
    elif page == "Giriş Yap":
        page_login()
    elif page == "Kayıt Ol":
        page_register()
    else:
        page_home()


init_state()
brand_header()

if st.session_state.user_id is None:
    render_page()
else:
    main_col, deva_col = st.columns([3.2, 1.15], gap="large")

    with main_col:
        if st.session_state.page != "Ana Sayfa":
            if st.button("Ana Sayfaya Dön", key="back_home_top"):
                go_to("Ana Sayfa")

        render_page()

    with deva_col:
        render_deva_side()