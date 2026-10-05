"""Language helpers: cleaning, sentence splitting, condensing, numbers, keywords.

Rule-based and offline (Russian and English). No AI or external services.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

STOPWORDS = set("""
и в во не что он на я с со как а то все она так его но да ты к у же вы за бы по только ее её мне было
вот от меня еще ещё нет о из ему теперь когда даже ну вдруг ли если уже или ни быть был него до вас нибудь
опять уж вам ведь там потом себя ничего ей может они тут где есть надо ней для мы тебя их чем была сам
чтоб без будто чего раз тоже себе под будет ж тогда кто этот того потому этого какой совсем ним здесь
этом один почти мой тем чтобы нее неё сейчас были куда зачем всех никогда можно при наконец два об другой
хоть после над больше тот через эти нас про всего них какая много разве три эту моя впрочем хорошо свою
этой перед иногда лучше чуть том нельзя такой им более всегда конечно всю между это эта эти его её их
который которая которое которые которых также свой своя своё свои очень просто именно ещё весь вся всё
почему зачем иначе снова стал стала стали стало становится каждый каждая любой другие свои весь целый
the a an and or but if then of to in on at by for with from as is are was were be been being it its this
that these those not no yes so than too very can will just into over about after before also more most
such only own same each other which who whom what when where why how all any both few some our their
""".split())

FILLERS = [
    "на самом деле", "по сути", "в общем-то", "в общем", "как известно", "конечно", "действительно",
    "буквально", "вообще", "кстати", "по большому счёту", "по большому счету", "в принципе",
    "на мой взгляд", "как правило", "по-настоящему", "при этом", "actually", "basically", "of course", "really",
    "literally", "in fact",
]
ABBREVIATIONS = {"г", "гг", "т", "е", "д", "п", "др", "вв", "в", "им", "ул", "стр", "тыс", "млн", "млрд",
                 "руб", "см", "напр", "mr", "mrs", "dr", "vs", "etc", "e", "g", "i", "st", "no"}

_SENTENCE_END = re.compile(r"([.!?…]+[»”\"')]*)\s+(?=[«“\"(]?[A-ZА-ЯЁ0-9—–-])")
_WORD = re.compile(r"[\w%’'‰₽$€⅓½¼¾+\-]+", re.UNICODE)


def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace(" ", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" ?-- ?", " — ", text)
    text = re.sub(r"(?<=\s)-(?=\s)", "—", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    """Split a paragraph into sentences, keeping abbreviations like "г." or "т.е." intact."""
    text = " ".join(text.split())
    sentences, start = [], 0
    for match in _SENTENCE_END.finditer(text):
        before = text[start:match.start()].split()
        last = before[-1].lower().strip(".«»\"'(") if before else ""
        if match.group(1) == "." and last.split(".")[-1] in ABBREVIATIONS:
            continue
        sentences.append(text[start:match.end(1)].strip())
        start = match.end()
    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def words(text: str) -> list[str]:
    return _WORD.findall(text)


def word_count(text: str) -> int:
    return len(words(text))


def strip_fillers(text: str) -> str:
    text = re.sub(r"\s*\([^)]*\)", "", text)
    for filler in FILLERS:
        text = re.sub(rf"(?i)(,\s*)?(?<!\w){re.escape(filler)}(?!\w)(\s*,)?", " ", text)
    text = re.sub(r"\s+,", ",", text)
    return re.sub(r"\s{2,}", " ", text).strip(" ,")


def clean_end(text: str) -> str:
    return text.strip().rstrip(".;:,").strip()


def capitalize(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def _clauses(text: str) -> list[str]:
    """Split at commas, semicolons, colons and dashes (but not "— это")."""
    parts = re.split(r"(?<=[,;:])\s+|\s+[—–]\s+(?!это\b)", text)
    return [p for p in parts if p.strip()]


def condense(text: str, max_words: int) -> str:
    """Shorten text to at most `max_words` words, cutting at clause boundaries.

    Fillers and parentheses are removed first. If the first clause alone is too
    long, the text is split at "и"/"and"; only as a last resort is it cut mid-clause
    (then an ellipsis marks the cut).
    """
    text = clean_end(strip_fillers(text))
    if word_count(text) <= max_words:
        return capitalize(text)
    for splitter in (_clauses, lambda t: re.split(r"\s+(?=(?:и|and|а также)\s)", t)):
        parts = splitter(text)
        result = ""
        for part in parts:
            candidate = f"{result} {part}".strip() if result else part
            if word_count(candidate) > max_words:
                break
            result = candidate
        if result and word_count(result) >= min(3, max_words):
            return capitalize(clean_end(result))
    tokens = text.split()[:max_words]
    while len(tokens) > 1 and tokens[-1].lower().strip(",.") in STOPWORDS:
        tokens.pop()
    return capitalize(clean_end(" ".join(tokens))) + "…"


# --- numbers ---------------------------------------------------------------

_UNIT = (r"%|‰|×|x\b|раз(?:а)?\b|млн\.?|млрд\.?|тыс\.?|миллион\w*|миллиард\w*|тысяч\w*|"
         r"k\b|m\b|bn\b|million\b|billion\b|thousand\b|₽|\$|€|руб\w*\.?|долл\w*|евро\b|"
         r"лет\b|год\w*|минут\w*|час\w*|дн\w*|недел\w*|месяц\w*|см\b|кг\b|км\b|об/мин|rpm\b|"
         r"percent\b|процент\w*|years?\b|minutes?\b|hours?\b|days?\b")
_NUMBER = re.compile(
    rf"(?P<cur>[$€₽])?\s?(?P<num>\d{{1,3}}(?:[  ]\d{{3}})+|\d+(?:[.,]\d+)?[⅓½¼¾]?)"
    rf"(?:\s?(?P<unit>{_UNIT}))?(?:\s(?P<unit2>долл\w*|рубл\w*|евро\b|dollars?\b))?",
    re.IGNORECASE,
)
_YEAR_PHRASE = re.compile(
    r"(?i)\b(?:(?:в|с|к|до|после|около|in|by|since|around)\s+)?(?:the\s+)?(?P<year>1[5-9]\d\d|20\d\d)"
    r"(?:-[хе]|['’]?s\b)?(?:\s*(?:году|года|год|годах|годы|гг?\.))?"
)
_SHORT_UNITS = {"миллион": "млн", "миллиард": "млрд", "тысяч": "тыс.", "процент": "%", "million": "M",
                "billion": "B", "thousand": "K", "percent": "%", "долл": "$", "dollar": "$",
                "рубл": "₽", "руб": "₽", "евро": "€"}
_GROWTH = re.compile(r"(?i)\b(вырос\w*|выросл\w*|увелич\w*|рост\w*|прибав\w*|grew|grow\w*|increas\w*|rose)\b")
_DECLINE = re.compile(r"(?i)\b(упал\w*|сниз\w*|сократ\w*|паден\w*|уменьш\w*|fell|fall\w*|declin\w*|drop\w*)\b")


@dataclass
class NumberMatch:
    display: str       # compact on-screen form, e.g. "+10%", "1,4 млрд $"
    value: float
    unit: str
    start: int
    end: int
    is_year: bool

    @property
    def is_percent(self) -> bool:
        return self.unit == "%"


def _short_unit(unit: str) -> str:
    low = unit.lower().rstrip(".")
    for prefix, short in _SHORT_UNITS.items():
        if low.startswith(prefix):
            return short
    return unit


def find_numbers(text: str) -> list[NumberMatch]:
    found = []
    for m in _NUMBER.finditer(text):
        raw = m.group("num")
        if m.start("num") > 0 and (text[m.start("num") - 1].isalpha() or text[m.start("num") - 1] in "-‑"):
            continue  # part of a word like "MP3"
        digits = raw.replace(" ", "").replace(" ", "").replace(",", ".").rstrip("⅓½¼¾")
        try:
            value = float(digits)
        except ValueError:
            continue
        units = [u for u in (m.group("unit"), m.group("unit2")) if u]
        cur = m.group("cur") or ""
        shorts = [_short_unit(u) for u in units]
        currency = cur or next((s for s in shorts if s in "$€₽"), "")
        scale = " ".join(s for s in shorts if s not in "$€₽")
        if scale.startswith(("год", "лет", "year")):
            scale = ""
        year_unit = all(u.lower().startswith(("год", "year")) for u in units)
        is_year = year_unit and not cur and raw.isdigit() and len(raw) == 4 and 1500 <= value <= 2099
        display = raw.replace(" ", " ")
        if scale == "%":
            display += "%"
        elif scale:
            display += f" {scale}"
        if currency:
            display = f"{display} {currency}" if currency in "₽€" or scale else f"{currency}{display}"
        unit = "%" if scale == "%" else (scale or currency)
        found.append(NumberMatch(display, value, unit, m.start(), m.end(), is_year))
    return found


def key_number(text: str) -> NumberMatch | None:
    """The most "headline-worthy" non-year number: percentages and money first."""
    candidates = [n for n in find_numbers(text) if not n.is_year]
    if not candidates:
        return None

    def score(n: NumberMatch) -> float:
        return (3 if n.is_percent else 0) + (2 if n.unit else 0) + min(n.value, 1e6) / 1e7

    best = max(candidates, key=score)
    if not best.unit and best.value < 10:
        return None  # a bare small number ("2 people") is not worth a scene
    window = text[max(0, best.start - 40):best.start]
    if best.is_percent and _GROWTH.search(window):
        best.display = "+" + best.display
    elif best.is_percent and _DECLINE.search(window):
        best.display = "−" + best.display
    return best


def years(text: str) -> list[str]:
    return [m.group("year") for m in _YEAR_PHRASE.finditer(text)]


def remove_first_year(text: str) -> str:
    return _YEAR_PHRASE.sub("", text, count=1).strip(" ,")


def remove_span(text: str, start: int, end: int) -> str:
    before = re.sub(r"(?i)\s*\b(на|до|в|by|to|of)\s*$", "", text[:start])
    return re.sub(r"\s{2,}", " ", (before + " " + text[end:]).strip())


# --- keywords --------------------------------------------------------------

# Likely verb forms (Russian present/past/infinitive, English -ed/-ing): rarely the key word.
_VERB_END = re.compile(r"(ть|ться|тся|ется|ются|ает|яет|ают|яют|ует|уют|чит|шит|дит|рит|ят|ут|ют|"
                       r"ала|али|ало|ила|или|ыла|ыли|ed|ing)$")


def keywords(text: str, count: int = 1) -> list[str]:
    """Most distinctive words: proper nouns and long content words, numbers excluded."""
    tokens = [w.strip("'’-") for w in words(text)]
    scored = []
    for i, token in enumerate(tokens):
        low = token.lower()
        if low in STOPWORDS or len(token) < 4 or any(c.isdigit() for c in token):
            continue
        score = len(token) + (6 if i > 0 and token[0].isupper() else 0) - (8 if _VERB_END.search(low) else 0)
        scored.append((score, -i, token))
    scored.sort(reverse=True)
    result = []
    for _, _, token in scored:
        if token.lower() not in (r.lower() for r in result):
            result.append(token)
        if len(result) == count:
            break
    return result


def detect_language(text: str) -> str:
    cyr = len(re.findall(r"[а-яё]", text, re.IGNORECASE))
    lat = len(re.findall(r"[a-z]", text, re.IGNORECASE))
    return "ru" if cyr >= lat else "en"
