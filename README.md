# NeuroTrack AI

**NeuroTrack AI**, otizm spektrum bozukluğu için yapay zekâ destekli ön değerlendirme, günlük takip, klinik izleme ve doktor-hasta iletişimi sunan web ve mobil tabanlı bir takip platformudur.

Bu sistem kesin tanı koymak amacıyla değil; kullanıcı, ebeveyn ve uzmanlara karar destek sağlamak amacıyla geliştirilmiştir.

---

## Proje Amacı

Bu projenin amacı, yetişkin ve çocuk kullanıcılar için otizm spektrum bozukluğu belirtilerini dijital ortamda takip edebilen, makine öğrenmesi destekli ön değerlendirme yapabilen ve doktor-hasta/ebeveyn iletişimini kolaylaştıran bütünleşik bir platform geliştirmektir.

Platformda yetişkin kullanıcılar kendi testlerini ve günlük kayıtlarını oluşturabilirken, ebeveynler çocukları adına günlük takip ve çocuk otizm ön değerlendirme testi yapabilmektedir. Doktor kullanıcıları ise kendilerine atanmış yetişkin ve çocuk hastaları takip edebilmekte, test geçmişlerini inceleyebilmekte ve doktor notu ekleyebilmektedir.

---

## Temel Özellikler

- Yetişkin kullanıcılar için makine öğrenmesi tabanlı otizm ön değerlendirme
- Çocuk kullanıcılar için makine öğrenmesi tabanlı otizm ön değerlendirme
- Ebeveyn çocuk takip paneli
- Günlük duygu durumu ve davranış takibi
- Klinik takip formları
- Doktor hasta takip paneli
- Çocuk ve yetişkin hasta geçmişi görüntüleme
- Doktor notları ve takip önerileri
- Bildirim sistemi
- Doktor-hasta mesajlaşma sistemi
- Deva AI chatbot destek modülü
- Web arayüzü
- Mobil uygulama desteği

---

## Kullanılan Teknolojiler

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Scikit-learn
- Joblib
- Pandas
- Uvicorn

### Web Arayüzü

- Streamlit
- Requests
- Pandas

### Mobil Uygulama

- React Native
- Expo
- JavaScript / TypeScript
- Expo Go

---

## Proje Yapısı

```text
autism-tracking-ai/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── model/
│   │   ├── adult_model.pkl
│   │   ├── child_model.pkl
│   │   └── train_child_model.py
│   └── utils/
│       ├── predict.py
│       └── predict_child.py
│
├── data/
│   └── child.csv
│
├── web_app.py              # Web arayüzü giriş noktası (router)
├── web/
│   ├── ui/
│   │   ├── theme.py        # Tasarım sistemi: renk/tipografi token'ları, global CSS
│   │   ├── components.py   # Kart, istatistik kutusu, rozet, sohbet balonu
│   │   ├── shell.py        # Sidebar navigasyon ve uygulama kabuğu
│   │   └── state.py        # Oturum durumu ve yönlendirme
│   ├── services/
│   │   └── api.py          # Backend API istemcisi
│   └── views/              # Sayfalar (auth, home, adult, parent, doctor, comms, deva)
│
├── .streamlit/
│   └── config.toml         # Streamlit tema ayarları
│
├── frontend.py             # Eski tek dosyalık arayüz (web_app.py ile değiştirildi)
│
├── App.js
├── app.json
├── package.json
├── package-lock.json
│
├── navigation/
├── screens/
├── services/
├── components/
├── constants/
├── assets/
│
└── README.md
```

---

## Backend Kurulumu ve Çalıştırma

Öncelikle proje klasörüne girilir:

```bash
cd autism-tracking-ai
```

Python sanal ortamı oluşturulur:

```bash
python3 -m venv venv
```

Sanal ortam aktif edilir:

```bash
source venv/bin/activate
```

Gerekli Python paketleri kurulur:

```bash
pip install -r requirements.txt
```

> Python 3.11 veya üzeri gereklidir.

Backend başlatılır:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

Backend çalıştıktan sonra API dokümantasyonu şu adresten görüntülenebilir:

```text
http://127.0.0.1:8003/docs
```

---

## Web Arayüzünü Çalıştırma

Backend çalışırken yeni bir terminal açılır ve proje klasörüne girilir:

```bash
cd autism-tracking-ai
```

Sanal ortam aktif edilir:

```bash
source venv/bin/activate
```

Streamlit web arayüzü başlatılır:

```bash
python -m streamlit run web_app.py --server.port 8501
```

Web arayüzü tarayıcıda şu adresten açılır:

```text
http://localhost:8501
```

---

## Mobil Uygulamayı Çalıştırma

Mobil uygulamayı çalıştırmak için Node.js kurulu olmalıdır.

Proje klasörüne girilir:

```bash
cd autism-tracking-ai
```

Gerekli paketler kurulur:

```bash
npm install
```

Expo uygulaması başlatılır:

```bash
npx expo start -c
```

Terminalde oluşan QR kod, telefondaki **Expo Go** uygulaması ile okutularak mobil uygulama çalıştırılabilir.

---

## Mobil API Bağlantı Ayarı

Mobil uygulamanın backend ile haberleşebilmesi için `services/api.js` dosyasındaki `API_URL` değeri güncellenmelidir.

Bilgisayarın yerel IP adresi öğrenilir:

```bash
ipconfig getifaddr en0
```

Daha sonra `services/api.js` dosyasında aşağıdaki alan düzenlenir:

```javascript
export const API_URL = "http://BILGISAYAR_IP_ADRESI:8003";
```

Örnek:

```javascript
export const API_URL = "http://192.168.1.13:8003";
```

Web arayüzü ise varsayılan olarak şu API adresini kullanmaktadır:

```text
http://127.0.0.1:8003
```

---

## Kullanıcı Rolleri

Sistemde üç farklı kullanıcı rolü bulunmaktadır.

### Yetişkin Kullanıcı

- Otizm ön değerlendirme testi yapabilir.
- Günlük duygu durumu kaydı oluşturabilir.
- Klinik takip formu doldurabilir.
- Doktor notlarını görüntüleyebilir.
- Doktor ile mesajlaşabilir.
- Bildirimlerini takip edebilir.

### Ebeveyn Kullanıcı

- Çocuk profili oluşturabilir.
- Çocuk için günlük takip kaydı girebilir.
- Çocuk otizm ön değerlendirme testi yapabilir.
- Çocuk test geçmişini görüntüleyebilir.
- Doktor notlarını görüntüleyebilir.
- Doktor ile mesajlaşabilir.

### Doktor Kullanıcı

- Yetişkin hastaları takip edebilir.
- Çocuk hastaları takip edebilir.
- Hasta günlük kayıtlarını ve test geçmişlerini görüntüleyebilir.
- Doktor notu ve takip önerisi ekleyebilir.
- Mesajlaşma isteklerini kabul veya reddedebilir.
- Hastalarla mesajlaşabilir.

---

## Makine Öğrenmesi Kullanımı

Projede yetişkin ve çocuk kullanıcılar için ayrı makine öğrenmesi modelleri kullanılmıştır.

Yetişkin kullanıcılar için otizm ön değerlendirme modeli, yetişkin ASD tarama verileri kullanılarak eğitilmiştir. Çocuk kullanıcılar için ise çocuklara yönelik ASD tarama veri seti kullanılarak ayrı bir model oluşturulmuştur.

Model girdileri genel olarak A1–A10 tarama skorları ve yaş bilgisinden oluşmaktadır. Model çıktısı, kullanıcıya düşük, orta veya yüksek risk düzeyinde destekleyici bir ön değerlendirme sunmaktadır.

---

## Backend API Modülleri

Projede kullanılan temel API modülleri şunlardır:

- Kullanıcı kayıt ve giriş işlemleri
- Yetişkin otizm tahmin işlemleri
- Çocuk otizm tahmin işlemleri
- Günlük kayıt işlemleri
- Klinik takip işlemleri
- Doktor-hasta eşleştirme işlemleri
- Doktor notu işlemleri
- Bildirim işlemleri
- Mesajlaşma işlemleri
- Deva AI chatbot işlemleri

API uç noktaları backend çalıştırıldıktan sonra aşağıdaki adresten incelenebilir:

```text
http://127.0.0.1:8003/docs
```

---

## Önemli Not

Bu uygulama kesin tanı koymaz. Sistem, makine öğrenmesi tabanlı ön değerlendirme ve takip desteği sunmak amacıyla geliştirilmiştir. Otizm spektrum bozukluğu tanısı yalnızca uzman hekimler ve ilgili klinik değerlendirme süreçleri sonucunda konulabilir.

---

## Geliştirici

**Şevval Erzurum**  
**İsmail Egin**
Bilgisayar Mühendisliği  
Bitirme Projesi
