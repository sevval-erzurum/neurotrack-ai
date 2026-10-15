"""Q-CHAT (Allison ve ark., 2008) maddeleri.

Veri setindeki `qchatNrecode` kolonları 0-4 arasıdır ve yüksek puan atipik
davranışı gösterir. Buradaki seçenek listeleri bu sıralamaya göre dizilmiştir:
options[k] seçilirse maddenin puanı k olur.

Türkçe ifadeler bu proje için çevrilmiştir; doğrulanmış bir Türkçe Q-CHAT
uyarlaması değildir.
"""

FREQ_TYPICAL = ["Her zaman", "Genellikle", "Bazen", "Nadiren", "Hiçbir zaman"]
FREQ_ATYPICAL = ["Hiçbir zaman", "Nadiren", "Bazen", "Genellikle", "Her zaman"]
EASE = ["Çok kolay", "Oldukça kolay", "Oldukça zor", "Çok zor", "İmkânsız"]
DURATION = ["Bir dakikadan az", "Birkaç dakika", "10 dakika kadar", "Yarım saatten fazla", "Saatlerce"]
WORDS = ["100'den fazla", "51–100", "10–50", "10'dan az", "Henüz konuşmuyor"]
FIRST_WORDS = ["Çok tipik", "Oldukça tipik", "Biraz alışılmadık", "Çok alışılmadık", "Henüz konuşmuyor"]

ITEMS: dict[int, tuple[str, list[str]]] = {
    1: ("Adıyla seslendiğinizde size bakar mı?", FREQ_TYPICAL),
    2: ("Çocuğunuzla göz teması kurmak sizin için ne kadar kolay?", EASE),
    3: ("Nesneleri sıraya dizer mi?", FREQ_ATYPICAL),
    4: ("Başkaları çocuğunuzun konuşmasını kolayca anlayabilir mi?", FREQ_TYPICAL),
    5: ("Bir şey istediğinde parmağıyla işaret eder mi?", FREQ_TYPICAL),
    6: ("İlgisini sizinle paylaşmak için bir şeyi işaret eder mi?", FREQ_TYPICAL),
    7: ("Dönen bir nesne ilgisini ne kadar süre tutar?", DURATION),
    8: ("Kaç kelime söyleyebiliyor?", WORDS),
    9: ("Mış gibi oyun oynar mı? (bebeğe bakmak, oyuncak telefonla konuşmak)", FREQ_TYPICAL),
    10: ("Sizin baktığınız yöne bakar mı?", FREQ_TYPICAL),
    11: ("Alışılmadık nesneleri koklar veya yalar mı?", FREQ_ATYPICAL),
    12: ("Bir şeyi kullanmanızı istediğinde elinizi tutup nesnenin üzerine koyar mı?", FREQ_ATYPICAL),
    13: ("Parmak uçlarında yürür mü?", FREQ_ATYPICAL),
    14: ("Rutini değiştiğinde veya eşyalar yerinde olmadığında uyum sağlaması ne kadar kolay?", EASE),
    15: ("Siz ya da aileden biri üzgün olduğunda teselli etmek ister mi?", FREQ_TYPICAL),
    16: ("Aynı şeyi tekrar tekrar yapar mı? (musluğu açıp kapamak, ışığı yakıp söndürmek)", FREQ_ATYPICAL),
    17: ("İlk kelimelerini nasıl tanımlarsınız?", FIRST_WORDS),
    18: ("Duyduklarını yankı gibi tekrarlar mı? (sözleriniz, şarkı veya film replikleri)", FREQ_ATYPICAL),
    19: ("Basit jestler kullanır mı? (el sallayarak hoşça kal demek)", FREQ_TYPICAL),
    20: ("Gözlerinin yakınında alışılmadık parmak hareketleri yapar mı?", FREQ_ATYPICAL),
    21: ("Tanımadığı bir durumla karşılaşınca tepkinizi görmek için yüzünüze bakar mı?", FREQ_TYPICAL),
    22: ("Yalnızca bir iki nesne ilgisini ne kadar süre tutar?", DURATION),
    23: ("Nesneleri tekrarlayıcı biçimde çevirip oynar mı? (ip parçası gibi)", FREQ_ATYPICAL),
    24: ("Seslere aşırı hassas görünür mü?", FREQ_ATYPICAL),
    25: ("Belirgin bir amaç olmadan boşluğa bakar mı?", FREQ_ATYPICAL),
}

# Yanıtlar ekranında kısa etiket olarak kullanılır.
SHORT_LABELS: dict[int, str] = {
    1: "Adına tepki", 2: "Göz teması", 3: "Nesneleri sıralama", 4: "Konuşmanın anlaşılırlığı",
    5: "İstek için işaret etme", 6: "İlgi paylaşmak için işaret etme", 7: "Dönen nesnelere ilgi",
    8: "Kelime sayısı", 9: "Mış gibi oyun", 10: "Bakış takibi", 11: "Koklama / yalama",
    12: "Eli araç olarak kullanma", 13: "Parmak ucunda yürüme", 14: "Değişime uyum",
    15: "Teselli etme", 16: "Tekrarlayıcı davranış", 17: "İlk kelimeler", 18: "Ekolali",
    19: "Jest kullanımı", 20: "Göz yakınında parmak hareketi", 21: "Sosyal referans",
    22: "Dar ilgi", 23: "Nesneleri çevirme", 24: "Ses hassasiyeti", 25: "Boşluğa bakma",
}


def column(item: int) -> str:
    return f"qchat{item}recode"
