"""
Аффилиатные ссылки на iHerb.
Замени IHERB_CODE на свой реферальный код из iherb.com/associates
"""

IHERB_CODE = "ТВОЙ_КОД"  # ← сюда вставь свой код, например "ABC1234"

# Маппинг: название добавки → поисковый запрос на iHerb
IHERB_SEARCH = {
    "Витамин D3":           "vitamin+d3",
    "Магний B6":            "magnesium+b6",
    "Омега-3":              "omega+3+fish+oil",
    "Цинк":                 "zinc+picolinate",
    "Витамин C":            "vitamin+c",
    "Коллаген морской":     "marine+collagen",
    "Мелатонин":            "melatonin",
    "Куркумин":             "curcumin+piperine",
    "Биотин":               "biotin",
    "Коэнзим Q10":          "coenzyme+q10",
    "Пробиотики":           "probiotics",
    "Железо хелат":         "iron+bisglycinate",
    "Фолиевая кислота":     "folate+methylfolate",
    "Витамин B12":          "methylcobalamin+b12",
    "Ашваганда":            "ashwagandha+ksm66",
    "Спирулина":            "spirulina",
    "NAC (N-ацетилцистеин)": "nac+n-acetyl+cysteine",
    "Глутатион":            "glutathione+liposomal",
    "Берберин":             "berberine",
    "L-теанин":             "l-theanine",
    "5-HTP":                "5-htp",
    "Глицин":               "glycine",
    "Карнитин":             "l-carnitine",
    "Креатин":              "creatine+monohydrate",
    "Витамин K2":           "vitamin+k2+mk7",
    "Витамин A":            "vitamin+a+retinol",
    "Витамин E":            "vitamin+e+tocopherol",
    "Селен":                "selenium+selenomethionine",
    "Йод":                  "iodine+potassium",
    "Хром":                 "chromium+picolinate",
    "Родиола розовая":      "rhodiola+rosea",
    "Женьшень":             "panax+ginseng",
    "Гинкго Билоба":        "ginkgo+biloba",
    "Лецитин":              "lecithin+phosphatidylcholine",
    "Альфа-липоевая кислота": "alpha+lipoic+acid",
}


def get_iherb_link(supplement_name: str) -> str | None:
    """Возвращает аффилиатную ссылку на iHerb или None если нет маппинга"""
    if IHERB_CODE == "ТВОЙ_КОД":
        return None  # код ещё не настроен

    query = IHERB_SEARCH.get(supplement_name)
    if not query:
        return None

    return f"https://www.iherb.com/search?kw={query}&rcode={IHERB_CODE}"
