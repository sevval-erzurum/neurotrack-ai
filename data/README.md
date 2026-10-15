# Veri Setleri

## qchat_toddler_poland.csv — ÖNERİLEN (gerçek klinik tanı)

**252 çocuk (135 otizm / 117 tipik gelişim), 18–24 ay.**

- **İçerik:** Q-CHAT'in 25 maddesi (`qchat1recode`…`qchat25recode`, 0–4 puan; yüksek = atipik),
  demografi (yaş/ay, cinsiyet, prematürite, doğum ağırlığı, kardeş sayısı, kardeşte ASD öyküsü,
  anne eğitimi), toplam skor (`Sum_QCHAT`) ve hedef (`asd`: 1 = otizm, 0 = kontrol).
- **Etiket nasıl konmuş:** ADOS-2 + ADI-R + DSM-5 ölçütlerine göre klinik değerlendirme.
  Varşova'daki uzman tanı merkezlerinden toplanmış.
- **Kaynak:** Mendeley Data, DOI [10.17632/tmpkt2mfkg.2](https://data.mendeley.com/datasets/tmpkt2mfkg/2)
  (orijinal dosya SPSS `.sav`; burada CSV'ye çevrildi, `group` kolonu `asd` olarak 1/0 kodlandı).
- **İlgili çalışma:** Sollis, Wall & Washington (2025), *Compact subsets of autism screening items
  predict clinical diagnoses with a machine learning analysis of the QCHAT-10*, Scientific Reports.
  <https://www.nature.com/articles/s41598-025-26131-9>

**Neden bu veri kullanılıyor:** Etiket, anket skorunun türevi DEĞİL. En iyi eşik kuralı
etiketin yalnızca %76'sını açıklıyor — yani makine öğrenmesinin öğreneceği gerçek bir örüntü var.
Model eğitimi: `python -m app.ml.train_toddler`. Sonuçlar ve sınırlılıklar için `MODEL_CARD.md`.

---

## adult.csv / child.csv — DİKKAT: hedef sızıntısı var

UCI "Autism Screening" veri setleri (Thabtah 2017). Sırasıyla 704 ve 292 satır.

**Bu setlerde `Class/ASD` etiketi, A1–A10 maddelerinin toplamından deterministik olarak türetilmiştir:**

```
Class/ASD == (A1_Score + ... + A10_Score > 6)      -> %100.00 birebir (her iki sette de)
result kolonu == A1..A10 toplamı                    -> birebir
```

Sonuç olarak bu veriyle eğitilen model otizmi değil, bir toplama işlemini öğrenir:

| Yaklaşım | Doğruluk |
|---|---|
| Random Forest (704 satır, 5-kat CV) | 0.970 |
| Aynı model sadece 20 satırla eğitilmiş | 0.920 |
| Hiç ML yok, tek satır `toplam > 6` kuralı | **1.000** |

Yani ML, tek satırlık kuraldan daha kötü ve daha fazla veri bunu değiştirmez.
Bu, literatürde bilinen bir sorundur ("rule-derived labels"); bkz.
<https://londonic.uk/js/index.php/ljbeh/article/download/365/378/1153>

Bu setler **AQ-10 tarama aracı** olarak kullanılabilir (skor + eşik), ancak
"makine öğrenmesi tahmini" olarak sunulmamalıdır.

`adult_clean.csv`, `adult.csv`'nin sadeleştirilmiş halidir; aynı sızıntıyı taşır.
