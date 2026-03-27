"""
Аффилиатные ссылки через Admitad → iHerb
Формат deeplink: BASE_URL&ulp=ENCODED_IHERB_URL
"""
from urllib.parse import quote

# Твоя базовая аффилиатная ссылка из Admitad
ADMITAD_BASE = "https://xnmik.com/g/ncvzabqdgm09f29e66e062343b7780/?erid=2bL9aMPo2e49hMef4pfzYmiQPz"

# Маппинг: название добавки → поисковый запрос на iHerb
IHERB_SEARCH = {
    "Витамин D3":               "vitamin+d3",
    "Магний B6":                "magnesium+b6",
    "Омега-3":                  "omega+3+fish+oil",
    "Цинк":                     "zinc+picolinate",
    "Витамин C":                "vitamin+c",
    "Коллаген морской":         "marine+collagen",
    "Мелатонин":                "melatonin",
    "Куркумин":                 "curcumin+piperine",
    "Биотин":                   "biotin",
    "Коэнзим Q10":              "coenzyme+q10",
    "Пробиотики":               "probiotics",
    "Железо хелат":             "iron+bisglycinate",
    "Фолиевая кислота":         "folate+methylfolate",
    "Витамин B12":              "methylcobalamin+b12",
    "Ашваганда":                "ashwagandha+ksm66",
    "Спирулина":                "spirulina",
    "NAC (N-ацетилцистеин)":    "nac+n-acetyl+cysteine",
    "Глутатион":                "glutathione+liposomal",
    "Берберин":                 "berberine",
    "L-теанин":                 "l-theanine",
    "5-HTP":                    "5-htp",
    "Глицин":                   "glycine",
    "Карнитин":                 "l-carnitine",
    "Креатин":                  "creatine+monohydrate",
    "Витамин K2":               "vitamin+k2+mk7",
    "Витамин A":                "vitamin+a+retinol",
    "Витамин E":                "vitamin+e+tocopherol",
    "Селен":                    "selenium+selenomethionine",
    "Йод":                      "iodine+potassium",
    "Хром":                     "chromium+picolinate",
    "Родиола розовая":          "rhodiola+rosea",
    "Женьшень":                 "panax+ginseng",
    "Гинкго Билоба":            "ginkgo+biloba",
    "Лецитин":                  "lecithin+phosphatidylcholine",
    "Альфа-липоевая кислота":   "alpha+lipoic+acid",
}


def get_iherb_link(supplement_name: str) -> str | None:
    """Возвращает аффилиатную deeplink-ссылку через Admitad или None"""
    query = IHERB_SEARCH.get(supplement_name)
    if not query:
        return None

    iherb_url = f"https://www.iherb.com/search?kw={query}"
    encoded_url = quote(iherb_url, safe="")
    return f"{ADMITAD_BASE}&ulp={encoded_url}"
