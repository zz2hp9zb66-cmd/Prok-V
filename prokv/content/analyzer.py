"""Text -> Storyboard: split text into scenes, pick a template, condense wording.

RuleBasedAnalyzer works offline with heuristics. It can be replaced by any other
ContentAnalyzer (for example an LLM-based one later) without touching rendering.

Optional hints in the input text give manual control:
    # Title            first heading becomes the video title / opening scene
    blank line or ---  scene boundary
    - item / 1. item   bullet list -> List scene
    **word**           highlight this word
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from prokv.config import VideoSpec
from prokv.content import text as tx
from prokv.models import Scene, SceneContent, Storyboard
from prokv.style import DEFAULT_STYLE, MotionConfig

KICKERS = {
    "ru": {"big_number": "В цифрах", "comparison": "Сравнение", "list": "Главное", "timeline": "Хронология",
           "quote": "Цитата", "diagram": "Как это работает", "split": "Определение", "conclusion": "Итог",
           "statement": ""},
    "en": {"big_number": "By the numbers", "comparison": "Compare", "list": "Key points",
           "timeline": "Timeline", "quote": "Quote", "diagram": "How it works", "split": "Definition",
           "conclusion": "Takeaway", "statement": ""},
}
CONTRAST_LABELS = {"ru": ("Не", "А"), "en": ("Not", "But")}

_BULLET = re.compile(r"^\s*(?:[-•*·—–]|\d{1,2}[.)])\s+(.+)$")
_HEADING = re.compile(r"^\s*#{1,3}\s+(.+)$")
_EMPHASIS = re.compile(r"\*\*(.+?)\*\*|__(.+?)__")
_QUOTE = re.compile(r"[«“\"„](?P<q>[^«»“”\"„]{12,})[»”\"]")
_ATTRIBUTION = re.compile(
    r"^[\s,.]*[—–-]?\s*(?:говорит|сказал[аи]?|пишет|писал[аи]?|отмечает|says|said|writes|wrote)?\s*(?P<a>.+)$",
    re.IGNORECASE)
_CONCLUSION = re.compile(r"(?i)^\s*(итог\w*|вывод\w*|главное|в итоге|в конце концов|резюм\w*|"
                         r"in short|in summary|bottom line|takeaway|to sum up|conclusion)\b[\s:,—-]*")
_STEP_MARKERS = re.compile(
    r"(?i)(?:^|,\s*|;\s*|\s)(?:а\s+)?(?:сначала|во-первых|затем|потом|после этого|далее|в конце|наконец|"
    r"first(?:ly)?|then|next|after that|finally)\b[\s,]*|\s*(?:→|->|=>)\s*")
_CAUSE = re.compile(r"(?i)\s*(?:приводит к|ведёт к|ведет к|поэтому|из-за этого|в результате|leads to|"
                    r"results in|therefore)\s+")
_TIME_BEFORE = re.compile(r"(?i)^\s*(раньше|прежде|когда-то|тогда|в прошлом|before|previously|in the past)\b[\s,]*")
_TIME_NOW = re.compile(r"(?i)^\s*(сегодня|сейчас|теперь|в наши дни|now|today|these days)\b[\s,]*")
_NOT_BUT = re.compile(r"(?i)^(?P<subj>.*?)\bне\s+(?P<a>[^,]+?),\s*а\s+(?P<b>.+)$|"
                      r"^(?P<subj_en>.*?)\bnot\s+(?P<a_en>[^,]+?),\s*but\s+(?P<b_en>.+)$")
_VERSUS = re.compile(r"(?i)\s+(?:vs\.?|versus|против)\s+")
_DEFINITION = re.compile(r"^(?P<term>[^,.:;]{2,40}?)\s+[—–-]\s+(?:это\s+)?(?P<definition>.{8,})$|"
                         r"^(?P<term_en>[^,.:;]{2,40}?)\s+(?:is|are)\s+(?P<definition_en>(?:a|an|the)\s.{8,})$")


@dataclass
class Idea:
    """A chunk of source text that becomes one scene."""

    sentences: list[str] = field(default_factory=list)
    bullets: list[str] = field(default_factory=list)
    heading: str = ""
    highlights: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join(self.sentences)


class ContentAnalyzer(ABC):
    @abstractmethod
    def analyze(self, text: str, spec: VideoSpec = VideoSpec()) -> Storyboard:
        ...


class RuleBasedAnalyzer(ContentAnalyzer):
    def __init__(self, motion: MotionConfig = DEFAULT_STYLE.motion, max_scenes: int = 12) -> None:
        self.motion = motion
        self.max_scenes = max_scenes

    # -- public ------------------------------------------------------------

    def analyze(self, text: str, spec: VideoSpec = VideoSpec()) -> Storyboard:
        text = tx.normalize(text)
        if not text:
            raise ValueError("The text is empty")
        self.lang = tx.detect_language(text)
        title, ideas = self._ideas(text)
        if not ideas and not title:
            raise ValueError("No usable text found")

        scenes: list[Scene] = []
        opening = self._opening(title, ideas)
        if opening:
            scenes.append(opening)
        for i, idea in enumerate(ideas):
            scene = self._scene(idea, is_last=i == len(ideas) - 1, previous=scenes[-1].kind if scenes else "")
            if scene:
                scenes.append(scene)
        scenes = self._limit(scenes)
        for scene in scenes:
            scene.duration_s = self._duration(scene)
        if not title:
            first = next((i.sentences[0] for i in ideas if i.sentences), "")
            title = tx.condense(first, 6).rstrip("…") if first else ""
        return Storyboard(title=tx.clean_end(title), language=self.lang, scenes=scenes, spec=spec)

    # -- splitting ---------------------------------------------------------

    def _ideas(self, text: str) -> tuple[str, list[Idea]]:
        title = ""
        ideas: list[Idea] = []
        blocks = re.split(r"\n\s*(?:---+\s*)?\n|\n---+\n", text)
        for block in blocks:
            lines = [l.strip() for l in block.strip().splitlines() if l.strip() and not re.fullmatch(r"-{3,}", l.strip())]
            if not lines:
                continue
            idea = Idea()
            prose: list[str] = []
            for line in lines:
                heading = _HEADING.match(line)
                bullet = _BULLET.match(line)
                if heading:
                    if not title and not ideas and not prose:
                        title = self._extract_emphasis(heading.group(1), idea)
                    else:
                        idea.heading = self._extract_emphasis(heading.group(1), idea)
                elif bullet and not _QUOTE.match(line):
                    idea.bullets.append(self._extract_emphasis(bullet.group(1), idea))
                else:
                    prose.append(self._extract_emphasis(line, idea))
            sentences = tx.split_sentences(" ".join(prose))
            if idea.bullets or len(sentences) <= 2:
                idea.sentences = sentences
                ideas.append(idea)
            else:
                ideas.extend(self._chunk(sentences, idea))
        return title, [i for i in ideas if i.sentences or i.bullets]

    def _chunk(self, sentences: list[str], template: Idea) -> list[Idea]:
        """Split a long paragraph: dated sentences stay together, others go in pairs."""
        groups: list[list[str]] = []
        for sentence in sentences:
            dated = bool(tx.years(sentence))
            if groups and dated and all(tx.years(s) for s in groups[-1]):
                groups[-1].append(sentence)
            elif groups and not dated and len(groups[-1]) == 1 and not self._special(groups[-1][0]) \
                    and not self._special(sentence):
                groups[-1].append(sentence)
            else:
                groups.append([sentence])
        result = []
        for n, group in enumerate(groups):
            result.append(Idea(group, heading=template.heading if n == 0 else "",
                               highlights=list(template.highlights)))
        return result

    @staticmethod
    def _special(sentence: str) -> bool:
        """Sentences with their own structure become their own scene instead of being paired."""
        clean = tx.clean_end(sentence)
        return bool(
            tx.years(sentence) or tx.key_number(sentence) or _QUOTE.search(sentence)
            or _CONCLUSION.match(sentence) or len(_STEP_MARKERS.findall(sentence)) >= 2
            or _NOT_BUT.match(clean) or _VERSUS.search(clean) or _DEFINITION.match(clean)
            or _TIME_BEFORE.match(sentence)
        )

    @staticmethod
    def _extract_emphasis(line: str, idea: Idea) -> str:
        for m in _EMPHASIS.finditer(line):
            idea.highlights.append(m.group(1) or m.group(2))
        return _EMPHASIS.sub(lambda m: m.group(1) or m.group(2), line)

    # -- scene building ----------------------------------------------------

    def _opening(self, title: str, ideas: list[Idea]) -> Scene | None:
        if title:
            body = ""
            first = ideas[0] if ideas else None
            if first and not first.bullets and len(first.sentences) == 2 and self._plain(first.sentences[0]):
                body = tx.condense(first.sentences.pop(0), 14)
            content = SceneContent(headline=tx.condense(title, 8), body=body,
                                   highlights=self._highlights(title, []))
            return Scene("statement", 0, content, title)
        return None

    def _plain(self, sentence: str) -> bool:
        return not (tx.key_number(sentence) or tx.years(sentence) or _QUOTE.search(sentence))

    def _scene(self, idea: Idea, is_last: bool, previous: str) -> Scene | None:
        builders = [
            self._bullet_list_scene, self._quote_scene, self._conclusion_scene, self._timeline_scene,
            self._diagram_scene, self._comparison_scene, self._split_scene, self._number_scene,
            self._inline_list_scene,
        ]
        for build in builders:
            scene = build(idea, is_last)
            if scene:
                break
        else:
            # An unmarked last paragraph with no special structure is the takeaway.
            scene = self._conclusion(idea, None) if is_last else self._statement_scene(idea, is_last)
        if scene and scene.kind == "statement" and previous == "statement" and idea.text:
            scene = self._split_from_statement(idea) or scene
        if scene and scene.kind == previous:
            scene.variant = "alt"  # same template twice in a row: use its alternative layout
        if scene:
            scene.source = idea.text or "\n".join(idea.bullets)
            scene.content.kicker = scene.content.kicker or KICKERS[self.lang][scene.kind]
        return scene

    def _kicker(self, idea: Idea, default: str = "") -> str:
        return tx.condense(idea.heading, 4) if idea.heading else default

    def _highlights(self, text: str, manual: list[str]) -> list[str]:
        chosen = [h for h in manual if h.lower() in text.lower()]
        return chosen or tx.keywords(text, 1)

    def _bullet_list_scene(self, idea: Idea, is_last: bool) -> Scene | None:
        if len(idea.bullets) < 2:
            return None
        return self._list(idea, idea.bullets, " ".join(idea.sentences))

    def _inline_list_scene(self, idea: Idea, is_last: bool) -> Scene | None:
        """"Heading: a, b, c and d" with at least three short parts."""
        m = re.match(r"^(?P<head>[^:]{3,80}):\s*(?P<rest>.+)$", idea.text)
        if not m:
            return None
        parts = [p for p in re.split(r",\s*|;\s*|\s+(?:и|and)\s+", tx.clean_end(m.group("rest"))) if p]
        if len(parts) < 3 or any(tx.word_count(p) > 6 for p in parts):
            return None
        return self._list(idea, parts, m.group("head"))

    def _list(self, idea: Idea, items: list[str], headline: str) -> Scene:
        items = [tx.condense(i, 6) for i in items[:5]]
        head = tx.condense(headline.rstrip(":"), 7) if headline else ""
        return Scene("list", 0, SceneContent(kicker=self._kicker(idea), headline=head, items=items,
                                             highlights=self._highlights(head, idea.highlights)))

    def _quote_scene(self, idea: Idea, is_last: bool) -> Scene | None:
        m = _QUOTE.search(idea.text)
        if not m or tx.word_count(m.group("q")) < 3:
            return None
        quote = tx.clean_end(m.group("q")).rstrip(",")
        author = ""
        tail = idea.text[m.end():]
        a = _ATTRIBUTION.match(tail.split(".")[0]) if tail.strip(" .") else None
        if a and a.group("a").strip(" .,"):
            author = tx.condense(a.group("a"), 6)
        return Scene("quote", 0, SceneContent(quote=quote, author=author))

    def _conclusion_scene(self, idea: Idea, is_last: bool) -> Scene | None:
        """Explicitly marked takeaways ("Итог: ...", "In short, ...")."""
        marked = _CONCLUSION.match(idea.text)
        return self._conclusion(idea, marked) if marked else None

    def _conclusion(self, idea: Idea, marked: re.Match | None) -> Scene | None:
        if not idea.sentences:
            return None
        first = _CONCLUSION.sub("", idea.sentences[0]) if marked else idea.sentences[0]
        headline = tx.condense(first, 12)
        body = tx.condense(idea.sentences[1], 12) if len(idea.sentences) > 1 else ""
        kicker = tx.capitalize(marked.group(1)) if marked else ""
        return Scene("conclusion", 0, SceneContent(kicker=kicker, headline=headline, body=body,
                                                   highlights=self._highlights(headline, idea.highlights)))

    def _timeline_scene(self, idea: Idea, is_last: bool) -> Scene | None:
        dated = [s for s in idea.sentences if tx.years(s)]
        if len({tx.years(s)[0] for s in dated}) < 2:
            return None
        headline = self._kicker(idea)
        pairs = []
        for sentence in dated[:5]:
            year = tx.years(sentence)[0]
            m = re.match(r"^(?P<head>[^:]{3,60}):\s*(?P<rest>.+)$", sentence)
            if m and not tx.years(m.group("head")):
                headline = headline or tx.condense(m.group("head"), 6)
                sentence = m.group("rest")
            pairs.append([year, tx.condense(tx.remove_first_year(sentence), 9)])
        return Scene("timeline", 0, SceneContent(headline=headline, pairs=pairs))

    def _diagram_scene(self, idea: Idea, is_last: bool) -> Scene | None:
        text = idea.text
        head = ""
        m = re.match(r"^(?P<head>[^:]{3,60}):\s*(?P<rest>.+)$", text)
        if m:
            head, text = m.group("head"), m.group("rest")
        markers = len(_STEP_MARKERS.findall(text))
        if markers >= 2:
            steps = _STEP_MARKERS.split(tx.clean_end(text))
        elif _CAUSE.search(text):
            steps = _CAUSE.split(tx.clean_end(text))
        else:
            return None
        steps = [tx.condense(s, 7) for s in steps if s and tx.word_count(s) >= 1][:4]
        if len(steps) < 2:
            return None
        return Scene("diagram", 0, SceneContent(kicker=self._kicker(idea), headline=tx.condense(head, 6) if head else "",
                                                items=steps))

    def _comparison_scene(self, idea: Idea, is_last: bool) -> Scene | None:
        s = idea.sentences
        if len(s) >= 2 and _TIME_BEFORE.match(s[0]) and _TIME_NOW.match(s[1]):
            labels = [tx.capitalize(_TIME_BEFORE.match(s[0]).group(1)), tx.capitalize(_TIME_NOW.match(s[1]).group(1))]
            sides = [_TIME_BEFORE.sub("", s[0]), _TIME_NOW.sub("", s[1])]
            return self._comparison(idea, labels, sides, "")
        for sentence in s:
            m = _NOT_BUT.match(tx.clean_end(sentence))
            if m:
                subj = m.group("subj") if m.group("subj") is not None else m.group("subj_en")
                a = m.group("a") or m.group("a_en")
                b = m.group("b") or m.group("b_en")
                return self._comparison(idea, list(CONTRAST_LABELS[self.lang]), [a, b], subj)
            parts = _VERSUS.split(tx.clean_end(sentence))
            if len(parts) == 2:
                return self._comparison(idea, ["A", "B"], parts, "")
        return None

    def _comparison(self, idea: Idea, labels: list[str], sides: list[str], headline: str) -> Scene:
        sides = [tx.condense(x, 7) for x in sides]
        headline = tx.condense(headline, 6) if tx.word_count(headline) >= 2 else self._kicker(idea)
        return Scene("comparison", 0, SceneContent(headline=headline, pairs=[[labels[0], sides[0]], [labels[1], sides[1]]],
                                                   highlights=self._highlights(sides[1], idea.highlights)))

    def _split_scene(self, idea: Idea, is_last: bool) -> Scene | None:
        m = _DEFINITION.match(tx.clean_end(idea.sentences[0])) if idea.sentences else None
        if not m:
            return None
        term = m.group("term") or m.group("term_en")
        definition = m.group("definition") or m.group("definition_en")
        if tx.word_count(term) > 4:
            return None
        return Scene("split", 0, SceneContent(kicker=self._kicker(idea), headline=tx.capitalize(term.strip()),
                                              body=tx.condense(definition, 14),
                                              highlights=self._highlights(definition, idea.highlights)))

    def _number_scene(self, idea: Idea, is_last: bool) -> Scene | None:
        sentence = next((s for s in idea.sentences if tx.key_number(s)), None)
        if not sentence:
            return None
        num = tx.key_number(sentence)
        year = next(iter(tx.years(sentence)), "")
        # The clause holding the number (and what follows) explains it; a lead-in
        # clause before it ("According to research, ...") becomes the secondary line.
        lead_end = sentence.rfind(",", 0, num.start)
        lead = sentence[:lead_end] if lead_end > 0 else ""
        rest = tx.remove_span(sentence, num.start, num.end)[max(lead_end + 1, 0):] if lead else \
            tx.remove_span(sentence, num.start, num.end)
        if year:
            rest, lead = tx.remove_first_year(rest), tx.remove_first_year(lead)
        if lead and tx.word_count(lead) >= 2:
            label, body = tx.condense(rest, 9), tx.condense(lead, 8)
        else:
            clauses = re.split(r",\s*|\s+(?:и|and)\s+(?=\w+\w\s)", tx.clean_end(rest), maxsplit=1)
            label = tx.condense(clauses[0], 10)
            body = tx.condense(clauses[1], 8) if len(clauses) > 1 and tx.word_count(clauses[1]) >= 2 else ""
        if not body and len(idea.sentences) > 1:
            other = next(s for s in idea.sentences if s is not sentence)
            body = tx.condense(other, 10)
        kicker = self._kicker(idea, f"{KICKERS[self.lang]['big_number']} · {year}" if year else "")
        return Scene("big_number", 0, SceneContent(kicker=kicker, number=num.display, headline=label, body=body,
                                                   highlights=[]))

    def _statement_scene(self, idea: Idea, is_last: bool) -> Scene | None:
        if not idea.sentences:
            return None
        headline = tx.condense(idea.sentences[0], 10)
        body = tx.condense(idea.sentences[1], 14) if len(idea.sentences) > 1 else ""
        return Scene("statement", 0, SceneContent(kicker=self._kicker(idea), headline=headline, body=body,
                                                  highlights=self._highlights(headline, idea.highlights)))

    def _split_from_statement(self, idea: Idea) -> Scene | None:
        """Avoid two identical screens in a row: show the key word big, the thought below."""
        key = tx.keywords(idea.sentences[0], 1)
        if not key:
            return None
        return Scene("split", 0, SceneContent(kicker=self._kicker(idea), headline=tx.capitalize(key[0]),
                                              body=tx.condense(idea.sentences[0], 14),
                                              highlights=[]))

    # -- limits and timing ---------------------------------------------------

    def _limit(self, scenes: list[Scene]) -> list[Scene]:
        """Keep at most max_scenes: drop plain statements from the middle first."""
        while len(scenes) > self.max_scenes:
            middle = [i for i, s in enumerate(scenes[1:-1], 1) if s.kind in ("statement", "split")]
            scenes.pop(middle[-1] if middle else len(scenes) - 2)
        return scenes

    def _duration(self, scene: Scene) -> float:
        c = scene.content
        on_screen = " ".join([c.kicker, c.headline, c.body, c.number, c.quote, c.author, *c.items,
                              *(" ".join(p) for p in c.pairs)])
        m = self.motion
        extra = len(c.items) + len(c.pairs)
        seconds = m.scene_base_s + tx.word_count(on_screen) * m.read_s_per_word + extra * m.per_item_s
        return round(min(max(seconds, m.scene_min_s), m.scene_max_s) / m.speed, 2)
