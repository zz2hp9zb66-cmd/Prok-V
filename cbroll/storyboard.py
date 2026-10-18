"""Storyboard for approval: one overview image plus a local HTML page."""

from __future__ import annotations

import html

from PIL import Image, ImageDraw, ImageFont

from .project import ProjectDir

STATUS_RU = {"draft": "на утверждении", "needs_changes": "нужны правки", "approved": "утверждено"}


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", "Arial Unicode.ttf", "Helvetica.ttc"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) > width and line:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line] if line else lines


def overview(pd: ProjectDir) -> str:
    scenes = pd.scenes()
    durations = {e.scene: e.duration_frames / pd.timeline().fps for e in pd.timeline().entries}
    tw, th, cap = 540, 960, 300
    sheet = Image.new("RGB", (tw * len(scenes) + 20 * (len(scenes) + 1), th + cap + 40), "#202020")
    draw = ImageDraw.Draw(sheet)
    f_title, f_body = _font(30, True), _font(22)
    for i, scene in enumerate(scenes):
        x = 20 + i * (tw + 20)
        still = Image.open(pd.abs(f"previews/scene_{scene.id}.png")).convert("RGB").resize((tw, th))
        sheet.paste(still, (x, 20))
        y = th + 36
        draw.text((x, y), f"Сцена {scene.id} · {durations[scene.id]:.1f} с", fill="#f0e6d0", font=f_title)
        draw.text((x, y + 40), f"{scene.template} · {STATUS_RU[scene.status]}", fill="#9c9585", font=f_body)
        y += 84
        for line in _wrap(draw, scene.text, f_body, tw)[:7]:
            draw.text((x, y), line, fill="#cfc7b6", font=f_body)
            y += 30
    path = pd.abs("previews/storyboard.png")
    sheet.save(path)
    return pd.rel(path)


def html_page(pd: ProjectDir) -> str:
    timeline = {e.scene: e for e in pd.timeline().entries}
    cards = []
    for scene in pd.scenes():
        rows = []
        for layer in scene.layers:
            if not layer.asset or layer.kind in ("texture",):
                continue
            meta_id = layer.asset.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            try:
                meta = pd.meta(meta_id)
                src = f'{html.escape(meta.title)} — <code>{meta.status}</code> ({html.escape(meta.license or "?")})'
            except FileNotFoundError:
                src = "—"
            rows.append(f"<li><b>{layer.id}</b>: {src}</li>")
        sec = timeline[scene.id].duration_frames / pd.timeline().fps
        cards.append(
            f"""<section><img src="scene_{scene.id}.png" alt="Сцена {scene.id}">
<div><h2>Сцена {scene.id} <small>{sec:.1f} с · шаблон {scene.template} · {STATUS_RU[scene.status]}</small></h2>
<p class="t">{html.escape(scene.text)}</p><ul>{''.join(rows)}</ul>
<p class="cmd">Утвердить: <code>cbroll approve {pd.root.name} {scene.id}</code> · правки — напишите в чат Claude Code</p></div></section>"""
        )
    page = f"""<!doctype html><html lang="ru"><meta charset="utf-8"><title>Раскадровка · {html.escape(pd.project().title)}</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;background:#1c1c1c;color:#eee;margin:0;padding:24px}}
section{{display:flex;gap:24px;margin:0 0 32px;align-items:flex-start}}img{{width:360px;border-radius:6px}}
small{{color:#aaa;font-weight:400}}.t{{font-size:19px;color:#f3e7cc}}code{{background:#333;padding:1px 5px;border-radius:4px}}
.cmd{{color:#aaa}}@media(max-width:700px){{section{{flex-direction:column}}img{{width:100%}}}}</style>
<h1>Раскадровка · {html.escape(pd.project().title)}</h1>{''.join(cards)}</html>"""
    path = pd.abs("previews/storyboard.html")
    path.write_text(page, encoding="utf-8")
    return pd.rel(path)
