# Model Kartı: Q-CHAT Küçük Çocuk Tarama Modeli

## Amaç

18–24 aylık çocuklarda, ebeveynin yanıtladığı 10 soruluk kısa bir Q-CHAT formundan
**uzman değerlendirmesine yönlendirme gerekip gerekmediğini** öneren bir tarama modeli.
Tanı aracı değildir.

## Veri

| | |
|---|---|
| Kaynak | Q-CHAT, Polonya kohortu, [Mendeley Data 10.17632/tmpkt2mfkg.2](https://data.mendeley.com/datasets/tmpkt2mfkg/2) |
| Örneklem | 252 çocuk (135 otizm, 117 tipik gelişim), 18–24 ay |
| Etiket | ADOS-2 + ADI-R + DSM-5 ile klinik tanı (anket skorundan türetilmemiş) |

Projedeki UCI `adult.csv` / `child.csv` setleri model eğitiminde **kullanılmaz**: bu setlerde
etiket, 10 maddenin toplamından deterministik olarak türetilmiştir (bkz. `data/README.md`).

## Yöntem

- **Nested cross-validation.** Dış döngü 5 kat × 5 tekrar. Her dış fold'un eğitim kısmında,
  iç 5 katlı CV ile hem hiperparametre araması hem de 25 maddeden 10'unun seçimi (RFE) yapılır.
  Test fold'u hiçbir seçim adımını görmez.
- **Aday modeller:** lojistik regresyon, SVM (RBF), Random Forest, XGBoost. Referans olarak
  25 maddeli lojistik regresyon ve hiç öğrenme içermeyen klasik toplam skor.
- **Model seçimi:** en yüksek ortalama AUC'nin bir standart hatası içindeki en basit model.
- **Çalışma noktası:** dış fold tahminleri üzerinde duyarlılık ≥ 0.90 sağlayan en yüksek eşik.
  Tarama bağlamında bir vakayı kaçırmak, gereksiz bir yönlendirmeden daha maliyetlidir.

## Sonuçlar (nested CV, 25 dış fold)

| Model | AUC | Brier |
|---|---|---|
| Klasik toplam skor (25 madde, ML yok) | 0.847 ± 0.051 | — |
| **Lojistik regresyon (10 madde) — seçilen** | **0.934 ± 0.040** | 0.117 |
| SVM (RBF) | 0.935 ± 0.040 | 0.104 |
| Random Forest | 0.932 ± 0.040 | 0.107 |
| XGBoost | 0.930 ± 0.038 | 0.111 |
| Lojistik regresyon (25 madde, referans) | 0.941 ± 0.035 | 0.117 |

- Dört aday model arasındaki fark gürültü düzeyindedir. Bu veri boyutunda daha karmaşık
  modeller ek bir kazanç sağlamıyor; lojistik regresyon aynı performansı tam açıklanabilir
  biçimde veriyor.
- Kısa form (10 madde), 25 maddeye göre yaklaşık 0.007 AUC kaybettiriyor.
- Seçilen eşik 0.44: duyarlılık 0.90, özgüllük 0.81 (dış fold tahminleri üzerinden).
- Güncel sayılar ve madde seçim kararlılığı: `app/model/toddler_model_meta.json`.

## Açıklanabilirlik

Her tahmin için maddelerin log-odds katkısı döndürülür (`app/ml/toddler.py`). Doğrusal
modelde bu değer `katsayı × standartlaştırılmış yanıt` olup, özellik bağımsızlığı
varsayımı altında tam SHAP değerine eşittir. Katkıların toplamı ile sabit terim, modelin
log-odds çıktısını birebir verir.

## Sınırlılıklar

- **Olasılıklar popülasyon riski değildir.** Örneklemde otizm oranı %54, genel
  popülasyonda ise yaklaşık %1–2'dir. Model çıktısı yalnızca eşiğe göre yönlendirme
  kararı için kullanılmalı, "otizm olasılığı" olarak sunulmamalıdır.
- Tek bir ülkeden 252 çocuk; dış doğrulama yapılmamıştır. Başka bir popülasyonda
  performansın düşmesi beklenmelidir.
- Eşik, raporlanan performansın hesaplandığı aynı tahminler üzerinde seçilmiştir; bu
  nedenle çalışma noktasındaki duyarlılık/özgüllük hafif iyimser olabilir.
- Uygulamadaki Türkçe soru metinleri bu proje için çevrilmiştir; doğrulanmış bir Türkçe
  Q-CHAT uyarlaması değildir.
