"""AQ-10 yetişkin tarama ölçeği (Allison, Auyeung & Baron-Cohen, 2012).

Kural tabanlıdır, makine öğrenmesi içermez. UCI yetişkin veri setindeki etiket bu
kuralın kendisi olduğu için (bkz. data/README.md) ML burada bir şey katmaz.
Türkçe ifadeler bu proje için çevrilmiştir; doğrulanmış bir uyarlama değildir.
"""

from dataclasses import dataclass

# 0 = Kesinlikle katılıyorum, 1 = Biraz katılıyorum, 2 = Biraz katılmıyorum, 3 = Kesinlikle katılmıyorum
OPTIONS = ["Kesinlikle katılıyorum", "Biraz katılıyorum", "Biraz katılmıyorum", "Kesinlikle katılmıyorum"]

# (madde metni, katılım puan alır mı)
ITEMS: dict[int, tuple[str, bool]] = {
    1: ("Başkalarının fark etmediği küçük sesleri sık sık fark ederim.", True),
    2: ("Genellikle küçük ayrıntılardan çok bütün resme odaklanırım.", False),
    3: ("Aynı anda birden fazla işi yapmak bana kolay gelir.", False),
    4: ("Bir kesinti olduğunda yaptığım işe çok hızlı geri dönebilirim.", False),
    5: ("Biri benimle konuşurken satır aralarını okumak bana kolay gelir.", False),
    6: ("Beni dinleyen birinin sıkılmaya başladığını anlayabilirim.", False),
    7: ("Bir hikâye okurken karakterlerin niyetlerini anlamakta zorlanırım.", True),
    8: ("Bir şeylerin kategorileri hakkında bilgi toplamayı severim.", True),
    9: ("Birinin ne düşündüğünü veya hissettiğini yüzüne bakarak kolayca anlarım.", False),
    10: ("İnsanların niyetlerini anlamakta zorlanırım.", True),
}

REFERRAL_THRESHOLD = 6


@dataclass(frozen=True)
class AQ10Result:
    score: int
    refer: bool
    scored_items: list[int]


def score(answers: dict[int, int]) -> AQ10Result:
    missing = set(ITEMS) - set(answers)
    if missing:
        raise ValueError(f"Eksik madde yanıtları: {sorted(missing)}")
    if any(not 0 <= answers[i] <= 3 for i in ITEMS):
        raise ValueError("AQ-10 yanıtları 0-3 aralığında olmalıdır")

    scored = [i for i, (_, agree_scores) in ITEMS.items() if (answers[i] <= 1) == agree_scores]
    return AQ10Result(score=len(scored), refer=len(scored) >= REFERRAL_THRESHOLD, scored_items=scored)
