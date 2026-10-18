"""Procedural placeholder "photos" for offline tests.

Used when image sources are unreachable. Each asset is drawn as SVG, rasterised,
then aged (grain, blur, vignette) so the cut-out stage works on a real
photo-like input: objects sit on a studio backdrop that rembg has to remove.
Every file is recorded with status `test_placeholder` and must be replaced by a
real photo before publishing anything.
"""

from __future__ import annotations

import io
import math
import random
from dataclasses import dataclass
from typing import Callable

import cairosvg
import numpy as np
from PIL import Image, ImageFilter

from .project import ProjectDir
from .schemas import AssetMeta

FONT = "Inter, Helvetica, Arial, sans-serif"
INK = "#121212"

GOLD_DEFS = """
<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff2b8"/><stop offset=".35" stop-color="#e3b44c"/>
  <stop offset=".62" stop-color="#9a6812"/><stop offset="1" stop-color="#f0cc6a"/>
</linearGradient>
<linearGradient id="goldh" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#8f5f10"/><stop offset=".4" stop-color="#f6d77a"/>
  <stop offset=".7" stop-color="#c58f2a"/><stop offset="1" stop-color="#7c500c"/>
</linearGradient>
<linearGradient id="chrome" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#5d6166"/><stop offset=".3" stop-color="#f4f6f8"/>
  <stop offset=".55" stop-color="#9aa0a6"/><stop offset=".8" stop-color="#e6e9ec"/>
  <stop offset="1" stop-color="#4b4f54"/>
</linearGradient>
"""


def backdrop(w: int, h: int, light: str = "#e9e4da", dark: str = "#b9b2a6") -> str:
    """Seamless studio paper sweep."""
    return f"""
<defs><radialGradient id="bd" cx=".5" cy=".42" r=".75">
  <stop offset="0" stop-color="{light}"/><stop offset="1" stop-color="{dark}"/></radialGradient>
<radialGradient id="floor" cx=".5" cy=".5" r=".5">
  <stop offset="0" stop-color="#000" stop-opacity=".35"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{w}" height="{h}" fill="url(#bd)"/>"""


def floor_shadow(cx: float, cy: float, rx: float, ry: float) -> str:
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#floor)"/>'


def svg(w: int, h: int, body: str, defs: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f"<defs>{GOLD_DEFS}{defs}</defs>{body}</svg>"
    )


# --- objects on a backdrop (to be cut out) ---------------------------------------


def trumpet() -> str:
    w, h = 1400, 900
    valves = ""
    for i, x in enumerate((560, 630, 700)):
        valves += f"""
<rect x="{x}" y="330" width="46" height="260" rx="8" fill="url(#goldh)"/>
<rect x="{x - 6}" y="318" width="58" height="26" rx="6" fill="#8a5b0e"/>
<rect x="{x - 6}" y="575" width="58" height="26" rx="6" fill="#8a5b0e"/>
<rect x="{x + 17}" y="268" width="12" height="52" fill="url(#goldh)"/>
<ellipse cx="{x + 23}" cy="262" rx="30" ry="11" fill="#f7f0de" stroke="#7a6a50" stroke-width="3"/>"""
    body = f"""{backdrop(w, h)}{floor_shadow(700, 760, 560, 40)}
<path d="M300 520 C 300 600, 340 640, 420 640 L 900 640" fill="none" stroke="#7a4f0c" stroke-width="40" stroke-linecap="round"/>
<path d="M300 520 C 300 600, 340 640, 420 640 L 900 640" fill="none" stroke="url(#gold)" stroke-width="30" stroke-linecap="round"/>
<path d="M760 640 C 860 640, 900 600, 900 560 L 900 500" fill="none" stroke="url(#gold)" stroke-width="30"/>
<rect x="160" y="436" width="760" height="34" rx="16" fill="url(#gold)"/>
<path d="M210 520 L 760 520" stroke="url(#gold)" stroke-width="30" stroke-linecap="round"/>
<path d="M210 520 C 150 520, 150 453, 210 453" fill="none" stroke="url(#gold)" stroke-width="30"/>
<path d="M90 446 L 160 438 L 160 470 L 90 462 Z" fill="url(#chrome)"/>
<ellipse cx="86" cy="454" rx="10" ry="22" fill="#c9cdd2"/>
<path d="M900 436 C 1040 430, 1140 360, 1260 250 L 1260 660 C 1140 550, 1040 476, 900 470 Z" fill="url(#gold)"/>
<ellipse cx="1260" cy="455" rx="34" ry="206" fill="url(#goldh)" stroke="#7a4f0c" stroke-width="4"/>
<ellipse cx="1262" cy="455" rx="20" ry="180" fill="#5a3a08" opacity=".55"/>
{valves}
<path d="M200 430 L 900 430" stroke="#fff6cf" stroke-width="4" opacity=".8"/>"""
    return svg(w, h, body)


def saxophone() -> str:
    w, h = 1000, 1400
    keys = "".join(
        f'<circle cx="{442 + i * 4}" cy="{380 + i * 75}" r="{22 + i}" fill="#c99632" stroke="#6e480a" stroke-width="5"/>'
        f'<circle cx="{442 + i * 4}" cy="{380 + i * 75}" r="{12 + i}" fill="#f6e9c6"/>'
        for i in range(7)
    )
    body = f"""{backdrop(w, h)}{floor_shadow(560, 1250, 320, 34)}
<path d="M330 150 C 360 150, 420 190, 432 260" fill="none" stroke="url(#goldh)" stroke-width="24" stroke-linecap="round"/>
<path d="M300 140 L 340 150" stroke="#111" stroke-width="26" stroke-linecap="round"/>
<path d="M432 260 L 440 900" stroke="#7a4f0c" stroke-width="70" stroke-linecap="round"/>
<path d="M432 260 L 440 900" stroke="url(#goldh)" stroke-width="58" stroke-linecap="round"/>
<path d="M440 880 C 440 1120, 700 1130, 690 920" fill="none" stroke="#7a4f0c" stroke-width="112"/>
<path d="M440 880 C 440 1120, 700 1130, 690 920" fill="none" stroke="url(#goldh)" stroke-width="100"/>
<path d="M640 930 L 600 640 C 600 600, 820 600, 820 640 L 740 930 Z" fill="url(#goldh)"/>
<ellipse cx="710" cy="628" rx="112" ry="34" fill="url(#gold)" stroke="#7a4f0c" stroke-width="5"/>
<ellipse cx="710" cy="630" rx="88" ry="22" fill="#5a3a08" opacity=".7"/>
{keys}
<path d="M470 300 L 480 860" stroke="#fff3c8" stroke-width="6" opacity=".7"/>"""
    return svg(w, h, body)


def vinyl() -> str:
    w, h = 1200, 1200
    grooves = "".join(
        f'<circle cx="600" cy="600" r="{r}" fill="none" stroke="#2c2c2c" stroke-width="1.5" opacity=".9"/>'
        for r in range(190, 470, 7)
    )
    body = f"""{backdrop(w, h, "#ece6dc", "#c4bcae")}{floor_shadow(620, 1100, 430, 30)}
<circle cx="600" cy="600" r="480" fill="#0d0d0d"/>{grooves}
<path d="M600 600 L 300 160 A 480 480 0 0 1 520 125 Z" fill="#fff" opacity=".12"/>
<path d="M600 600 L 900 1040 A 480 480 0 0 1 680 1075 Z" fill="#fff" opacity=".10"/>
<circle cx="600" cy="600" r="170" fill="#1d3f8f"/>
<circle cx="600" cy="600" r="160" fill="none" stroke="#f6efdf" stroke-width="4"/>
<text x="600" y="560" font-family="{FONT}" font-weight="800" font-size="44" fill="#f6efdf" text-anchor="middle">TEST PRESSING</text>
<text x="600" y="690" font-family="{FONT}" font-weight="600" font-size="34" fill="#f6efdf" text-anchor="middle">33⅓ RPM · SIDE A</text>
<circle cx="600" cy="600" r="14" fill="#d9d2c5"/>"""
    return svg(w, h, body)


def microphone() -> str:
    w, h = 900, 1400
    ribs = "".join(
        f'<rect x="{318 + i * 22}" y="210" width="9" height="430" rx="4" fill="#3c4045" opacity=".55"/>' for i in range(12)
    )
    body = f"""{backdrop(w, h)}{floor_shadow(450, 1300, 230, 26)}
<rect x="430" y="760" width="40" height="500" fill="url(#chrome)"/>
<ellipse cx="450" cy="1270" rx="170" ry="34" fill="#2c2f33"/>
<ellipse cx="450" cy="1260" rx="160" ry="26" fill="url(#chrome)"/>
<path d="M250 430 L 250 720 Q 250 790 330 790 L 570 790 Q 650 790 650 720 L 650 430" fill="none" stroke="#2c2f33" stroke-width="30"/>
<rect x="290" y="160" width="320" height="560" rx="160" fill="url(#chrome)" stroke="#3a3d42" stroke-width="6"/>
{ribs}
<rect x="282" y="410" width="336" height="60" rx="10" fill="url(#chrome)" stroke="#3a3d42" stroke-width="4"/>
<circle cx="250" cy="440" r="26" fill="#2c2f33"/><circle cx="650" cy="440" r="26" fill="#2c2f33"/>"""
    return svg(w, h, body)


def clock() -> str:
    w, h = 1100, 1100
    ticks = ""
    for i in range(60):
        a = math.radians(i * 6)
        r1, r2 = (360, 400) if i % 5 == 0 else (385, 400)
        sw = 10 if i % 5 == 0 else 3
        ticks += (
            f'<line x1="{550 + r1 * math.sin(a):.1f}" y1="{550 - r1 * math.cos(a):.1f}" '
            f'x2="{550 + r2 * math.sin(a):.1f}" y2="{550 - r2 * math.cos(a):.1f}" stroke="{INK}" stroke-width="{sw}"/>'
        )
    nums = "".join(
        f'<text x="{550 + 300 * math.sin(math.radians(n * 30)):.1f}" y="{550 - 300 * math.cos(math.radians(n * 30)) + 26:.1f}" '
        f'font-family="{FONT}" font-weight="700" font-size="74" text-anchor="middle" fill="{INK}">{n}</text>'
        for n in range(1, 13)
    )
    body = f"""{backdrop(w, h)}
<circle cx="560" cy="566" r="470" fill="#000" opacity=".25"/>
<circle cx="550" cy="550" r="470" fill="#2b2b2b"/><circle cx="550" cy="550" r="440" fill="#f4efe2"/>
{ticks}{nums}
<line x1="550" y1="550" x2="550" y2="250" stroke="{INK}" stroke-width="16" stroke-linecap="round"/>
<line x1="550" y1="550" x2="760" y2="550" stroke="{INK}" stroke-width="24" stroke-linecap="round"/>
<line x1="550" y1="600" x2="550" y2="180" stroke="#c0392b" stroke-width="5"/>
<circle cx="550" cy="550" r="24" fill="{INK}"/>"""
    return svg(w, h, body)


def tape_recorder() -> str:
    w, h = 1400, 1100

    def reel(cx: int) -> str:
        holes = "".join(
            f'<circle cx="{cx + 95 * math.cos(math.radians(a)):.1f}" cy="{380 + 95 * math.sin(math.radians(a)):.1f}" r="52" fill="#d8d1c3"/>'
            for a in (-90, 30, 150)
        )
        return (
            f'<circle cx="{cx}" cy="380" r="230" fill="#4a2f1c"/>'
            f'<circle cx="{cx}" cy="380" r="236" fill="none" stroke="url(#chrome)" stroke-width="14"/>'
            f'<circle cx="{cx}" cy="380" r="170" fill="url(#chrome)"/>{holes}'
            f'<circle cx="{cx}" cy="380" r="30" fill="#2b2b2b"/>'
        )

    knobs = "".join(
        f'<circle cx="{x}" cy="880" r="42" fill="#1b1b1b"/><circle cx="{x}" cy="880" r="30" fill="url(#chrome)"/>'
        for x in (340, 470, 930, 1060)
    )
    body = f"""{backdrop(w, h)}{floor_shadow(700, 1050, 600, 34)}
<rect x="110" y="120" width="1180" height="900" rx="40" fill="#6b6155"/>
<rect x="130" y="140" width="1140" height="860" rx="30" fill="#cfc6b4"/>
<rect x="130" y="700" width="1140" height="300" rx="30" fill="#3e3a35"/>
{reel(420)}{reel(980)}
<path d="M420 610 L 640 650 L 760 650 L 980 610" fill="none" stroke="#4a2f1c" stroke-width="6"/>
<rect x="610" y="625" width="180" height="50" rx="8" fill="url(#chrome)"/>
<rect x="610" y="760" width="180" height="120" rx="10" fill="#f2e6c4" stroke="#1b1b1b" stroke-width="6"/>
<path d="M630 860 A 70 70 0 0 1 770 860" fill="none" stroke="#1b1b1b" stroke-width="3"/>
<line x1="700" y1="870" x2="745" y2="790" stroke="#c0392b" stroke-width="5"/>
{knobs}"""
    return svg(w, h, body)


def drum_kit() -> str:
    w, h = 1500, 1200
    body = f"""{backdrop(w, h)}{floor_shadow(750, 1110, 620, 46)}
<line x1="250" y1="1080" x2="300" y2="380" stroke="url(#chrome)" stroke-width="14"/>
<line x1="1260" y1="1080" x2="1200" y2="300" stroke="url(#chrome)" stroke-width="14"/>
<ellipse cx="300" cy="380" rx="200" ry="34" fill="url(#goldh)" stroke="#7a4f0c" stroke-width="4"/>
<ellipse cx="1200" cy="300" rx="230" ry="40" fill="url(#goldh)" stroke="#7a4f0c" stroke-width="4"/>
<rect x="250" y="700" width="230" height="170" rx="12" fill="#f2f0ea" stroke="#1b1b1b" stroke-width="6"/>
<ellipse cx="365" cy="700" rx="115" ry="26" fill="#ece7dc" stroke="#555" stroke-width="5"/>
<line x1="365" y1="870" x2="365" y2="1080" stroke="url(#chrome)" stroke-width="12"/>
<rect x="560" y="430" width="180" height="150" rx="10" fill="#7b1d1d"/>
<ellipse cx="650" cy="430" rx="90" ry="22" fill="#ece7dc"/>
<rect x="770" y="420" width="200" height="160" rx="10" fill="#7b1d1d"/>
<ellipse cx="870" cy="420" rx="100" ry="24" fill="#ece7dc"/>
<circle cx="760" cy="820" r="270" fill="#7b1d1d"/>
<circle cx="760" cy="820" r="250" fill="#f2efe6"/>
<circle cx="760" cy="820" r="250" fill="none" stroke="url(#chrome)" stroke-width="18"/>
<circle cx="760" cy="820" r="130" fill="none" stroke="#1d3f8f" stroke-width="10"/>
<text x="760" y="842" font-family="{FONT}" font-weight="800" font-size="64" text-anchor="middle" fill="#1d3f8f">TEST</text>
<rect x="1030" y="720" width="220" height="300" rx="12" fill="#7b1d1d"/>
<ellipse cx="1140" cy="720" rx="110" ry="26" fill="#ece7dc"/>"""
    return svg(w, h, body)


def ocean_liner() -> str:
    w, h = 1600, 900
    windows = "".join(f'<circle cx="{x}" cy="560" r="7" fill="#f2e7c9"/>' for x in range(320, 1300, 34))
    deck_windows = "".join(f'<rect x="{x}" y="452" width="16" height="16" fill="#3a3a3a"/>' for x in range(420, 1180, 30))
    funnels = "".join(
        f'<path d="M{x} 420 L {x + 20} 230 L {x + 110} 230 L {x + 110} 420 Z" fill="#c4442c"/>'
        f'<path d="M{x + 18} 255 L {x + 22} 230 L {x + 110} 230 L {x + 110} 255 Z" fill="#111"/>'
        for x in (520, 700, 880)
    )
    body = f"""{backdrop(w, h)}
<path d="M520 200 C 480 120, 380 110, 300 60 C 420 70, 520 120, 560 190 Z" fill="#555" opacity=".35"/>
{funnels}
<rect x="380" y="420" width="840" height="70" fill="#f1ede4" stroke="#222" stroke-width="3"/>
{deck_windows}
<path d="M160 500 L 1440 500 L 1360 680 L 260 680 Z" fill="#141414"/>
<path d="M232 640 L 1378 640 L 1360 680 L 260 680 Z" fill="#8c1f1f"/>
{windows}
<line x1="220" y1="500" x2="300" y2="300" stroke="#222" stroke-width="5"/>
<line x1="1380" y1="500" x2="1300" y2="300" stroke="#222" stroke-width="5"/>
<path d="M300 300 L 1300 300" stroke="#222" stroke-width="2"/>"""
    return svg(w, h, body)


# --- people: backlit silhouettes on a studio backdrop -------------------------------


def _limb(points: list[tuple[float, float]], width: float, color: str = INK) -> str:
    d = "M" + " L ".join(f"{x} {y}" for x, y in points)
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'


def man_in_hat(lean: float = 0, coat: str = "#1a1a1a") -> str:
    """Half-length portrait of a man in a fedora and overcoat."""
    w, h = 1000, 1300
    c = 500 + lean
    body = f"""{backdrop(w, h, "#efe9de", "#a9a091")}
<path d="M{c - 380} 1300 C {c - 370} 980, {c - 300} 860, {c - 120} 820 L {c + 120} 820 C {c + 300} 860, {c + 370} 980, {c + 380} 1300 Z" fill="{coat}"/>
<path d="M{c - 120} 820 L {c} 1080 L {c + 120} 820 Z" fill="#e8e3d8"/>
<path d="M{c - 26} 860 L {c + 26} 860 L {c + 40} 1060 L {c} 1110 L {c - 40} 1060 Z" fill="#3a3a3a"/>
<path d="M{c - 120} 820 L {c - 30} 1130 L {c - 200} 900 Z" fill="#2c2c2c"/>
<path d="M{c + 120} 820 L {c + 30} 1130 L {c + 200} 900 Z" fill="#2c2c2c"/>
<rect x="{c - 70}" y="700" width="140" height="150" rx="40" fill="#5d5a55"/>
<ellipse cx="{c}" cy="560" rx="150" ry="190" fill="#6c6862"/>
<ellipse cx="{c - 150}" cy="580" rx="26" ry="48" fill="#5d5a55"/>
<ellipse cx="{c + 150}" cy="580" rx="26" ry="48" fill="#5d5a55"/>
<path d="M{c - 70} 520 L {c - 130} 640 Q {c} 760 {c + 130} 640 L {c + 70} 520 Z" fill="#7a766f" opacity=".5"/>
<ellipse cx="{c}" cy="420" rx="290" ry="58" fill="#141414"/>
<path d="M{c - 170} 420 C {c - 170} 250, {c - 120} 210, {c} 230 C {c + 120} 210, {c + 170} 250, {c + 170} 420 Z" fill="#191919"/>
<path d="M{c - 172} 392 L {c + 172} 392 L {c + 170} 420 L {c - 170} 420 Z" fill="#4a4a4a"/>
<path d="M{c - 40} 240 Q {c} 290 {c + 40} 240" fill="none" stroke="#333" stroke-width="10"/>"""
    return svg(w, h, body)


def _figure(head: tuple[float, float], hip: tuple[float, float], legs: list[list[tuple[float, float]]]) -> str:
    """Torso, head and legs of a standing figure; arms and instrument are drawn by the caller."""
    hx, hy = head
    px, py = hip
    torso = (
        f'<path d="M{hx - 85} {hy + 140} C {hx - 110} {hy + 300}, {px - 95} {py - 160}, {px - 90} {py} '
        f'L {px + 90} {py} C {px + 95} {py - 160}, {hx + 110} {hy + 300}, {hx + 85} {hy + 140} '
        f'Q {hx} {hy + 105} {hx - 85} {hy + 140} Z" fill="{INK}"/>'
    )
    neck = f'<rect x="{hx - 30}" y="{hy + 50}" width="60" height="90" fill="{INK}"/>'
    head_ = f'<ellipse cx="{hx}" cy="{hy}" rx="70" ry="82" fill="{INK}"/>'
    hat = (
        f'<ellipse cx="{hx}" cy="{hy - 52}" rx="112" ry="20" fill="{INK}"/>'
        f'<rect x="{hx - 68}" y="{hy - 120}" width="136" height="70" rx="16" fill="{INK}"/>'
    )
    legs_ = "".join(_limb(leg, 78) for leg in legs)
    shoes = "".join(
        f'<ellipse cx="{leg[-1][0] + 26}" cy="{leg[-1][1] + 18}" rx="62" ry="24" fill="{INK}"/>' for leg in legs
    )
    return torso + neck + head_ + hat + legs_ + shoes


def trumpeter() -> str:
    w, h = 1000, 1500
    fig = _figure((460, 300), (470, 860), [[(430, 850), (410, 1130), (390, 1400)], [(510, 850), (580, 1120), (620, 1400)]])
    body = f"""{backdrop(w, h, "#efe9de", "#a9a091")}{floor_shadow(500, 1440, 280, 30)}
{fig}
{_limb([(420, 470), (520, 640), (640, 470)], 58)}
{_limb([(520, 470), (650, 560), (700, 420)], 58)}
<path d="M520 300 L 760 205 L 772 232 L 532 328 Z" fill="{INK}"/>
<path d="M740 216 C 810 190, 860 130, 900 60 L 945 170 C 880 190, 830 225, 765 258 Z" fill="{INK}"/>
<rect x="640" y="230" width="70" height="80" rx="10" fill="{INK}" transform="rotate(-22 675 270)"/>"""
    return svg(w, h, body)


def sax_player() -> str:
    w, h = 1000, 1500
    fig = _figure((470, 290), (480, 860), [[(440, 850), (400, 1130), (380, 1400)], [(520, 850), (560, 1130), (590, 1400)]])
    body = f"""{backdrop(w, h, "#efe9de", "#a9a091")}{floor_shadow(500, 1440, 280, 30)}
{fig}
<path d="M540 330 C 600 360, 640 420, 650 470" fill="none" stroke="{INK}" stroke-width="22" stroke-linecap="round"/>
<path d="M650 470 L 700 900" stroke="{INK}" stroke-width="60" stroke-linecap="round"/>
<path d="M700 880 C 710 1010, 830 1010, 840 900 L 850 760" fill="none" stroke="{INK}" stroke-width="88"/>
<path d="M800 780 L 780 650 L 930 650 L 900 780 Z" fill="{INK}"/>
{_limb([(410, 470), (520, 650), (670, 620)], 58)}
{_limb([(530, 470), (600, 700), (700, 800)], 58)}"""
    return svg(w, h, body)


def drummer() -> str:
    w, h = 1200, 1300
    body = f"""{backdrop(w, h, "#efe9de", "#a9a091")}{floor_shadow(600, 1230, 420, 34)}
<circle cx="600" cy="260" r="92" fill="{INK}"/>
{_limb([(600, 340), (600, 560), (600, 760)], 220)}
{_limb([(520, 430), (380, 520), (300, 360)], 66)}
{_limb([(680, 430), (830, 540), (900, 420)], 66)}
{_limb([(300, 360), (200, 180)], 14)}{_limb([(900, 420), (1030, 260)], 14)}
<rect x="320" y="760" width="560" height="440" rx="24" fill="{INK}"/>
<ellipse cx="240" cy="640" rx="170" ry="26" fill="{INK}"/>
<line x1="240" y1="640" x2="250" y2="1220" stroke="{INK}" stroke-width="14"/>
<ellipse cx="980" cy="560" rx="180" ry="28" fill="{INK}"/>
<line x1="980" y1="560" x2="960" y2="1220" stroke="{INK}" stroke-width="14"/>"""
    return svg(w, h, body)


# --- full-frame "archive photos" (used as backgrounds, not cut out) -----------------


def skyline() -> str:
    w, h = 1200, 1600
    rnd = random.Random(7)
    far, near = "", ""
    x = 0
    while x < w:
        bw, bh = rnd.randint(50, 120), rnd.randint(250, 650)
        far += f'<rect x="{x}" y="{1150 - bh}" width="{bw}" height="{bh + 450}" fill="#8b8b88"/>'
        x += bw + rnd.randint(0, 10)
    x = -20
    while x < w:
        bw, bh = rnd.randint(90, 180), rnd.randint(220, 520)
        near += f'<rect x="{x}" y="{1250 - bh}" width="{bw}" height="{bh + 400}" fill="#3e3e3c"/>'
        for wy in range(1270 - bh, 1250, 34):
            for wx in range(x + 12, x + bw - 12, 26):
                if rnd.random() < 0.55:
                    near += f'<rect x="{wx}" y="{wy}" width="10" height="16" fill="#bdb8ab" opacity=".8"/>'
        x += bw + rnd.randint(4, 20)
    tower = (
        '<rect x="520" y="420" width="170" height="900" fill="#5a5a57"/>'
        '<rect x="550" y="300" width="110" height="140" fill="#5a5a57"/>'
        '<rect x="575" y="200" width="60" height="110" fill="#5a5a57"/>'
        '<path d="M595 200 L 605 40 L 615 200 Z" fill="#5a5a57"/>'
    )
    body = f"""<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#d9d6cd"/><stop offset=".7" stop-color="#f1eee6"/><stop offset="1" stop-color="#c9c6bd"/></linearGradient></defs>
<rect width="{w}" height="{h}" fill="url(#sky)"/>
{far}{tower}
<rect width="{w}" height="{h}" fill="#f1eee6" opacity=".25"/>
{near}
<rect y="1250" width="{w}" height="350" fill="#2a2a29"/>
<path d="M0 1300 L {w} 1290" stroke="#6b6b67" stroke-width="3"/>"""
    return svg(w, h, body)


def night_club() -> str:
    w, h = 1200, 1600
    rnd = random.Random(3)
    bokeh = "".join(
        f'<circle cx="{rnd.randint(0, w)}" cy="{rnd.randint(80, 700)}" r="{rnd.randint(10, 46)}" fill="#fff" opacity="{rnd.uniform(.08, .3):.2f}"/>'
        for _ in range(40)
    )
    heads = "".join(
        f'<ellipse cx="{x + rnd.randint(-20, 20)}" cy="{1330 + rnd.randint(-30, 30)}" rx="62" ry="78" fill="#050505"/>'
        f'<rect x="{x - 110}" y="{1390 + rnd.randint(-20, 20)}" width="220" height="400" rx="80" fill="#050505"/>'
        for x in range(60, w + 100, 190)
    )
    body = f"""<defs>
<radialGradient id="spot" cx=".5" cy="0" r="1"><stop offset="0" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<radialGradient id="pool" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#e9e3d3" stop-opacity=".7"/><stop offset="1" stop-color="#e9e3d3" stop-opacity="0"/></radialGradient></defs>
<rect width="{w}" height="{h}" fill="#141414"/>
{bokeh}
<path d="M520 0 L 680 0 L 1000 1150 L 200 1150 Z" fill="url(#spot)" opacity=".7"/>
<ellipse cx="600" cy="1120" rx="420" ry="90" fill="url(#pool)"/>
<rect x="0" y="1120" width="{w}" height="40" fill="#2a2520"/>
<circle cx="600" cy="760" r="58" fill="#0a0a0a"/>
<rect x="545" y="815" width="110" height="320" rx="40" fill="#0a0a0a"/>
<path d="M620 860 L 780 700 L 800 720 L 650 880 Z" fill="#0a0a0a"/>
<rect x="590" y="900" width="8" height="230" fill="#0a0a0a"/>
{heads}"""
    return svg(w, h, body)


def living_room() -> str:
    w, h = 1200, 1600
    stripes = "".join(f'<rect x="{x}" y="0" width="22" height="1100" fill="#9d978b" opacity=".35"/>' for x in range(0, w, 70))
    body = f"""<defs><linearGradient id="win" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#d7d2c6"/></linearGradient>
<radialGradient id="lamp" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fffbe9" stop-opacity=".9"/><stop offset="1" stop-color="#fffbe9" stop-opacity="0"/></radialGradient></defs>
<rect width="{w}" height="{h}" fill="#bcb5a7"/>{stripes}
<rect x="640" y="180" width="420" height="600" fill="url(#win)" stroke="#3b3631" stroke-width="22"/>
<line x1="850" y1="180" x2="850" y2="780" stroke="#3b3631" stroke-width="14"/>
<line x1="640" y1="480" x2="1060" y2="480" stroke="#3b3631" stroke-width="14"/>
<path d="M640 780 L 1060 780 L 1200 1600 L 400 1600 Z" fill="#fff" opacity=".12"/>
<rect y="1100" width="{w}" height="500" fill="#5b5146"/>
<rect x="80" y="560" width="420" height="560" rx="10" fill="#2a2420"/>
<rect x="80" y="760" width="420" height="40" fill="#f2efe6"/>
{"".join(f'<rect x="{x}" y="760" width="8" height="26" fill="#111"/>' for x in range(96, 490, 22))}
<circle cx="260" cy="350" r="120" fill="url(#lamp)"/>
<path d="M210 300 L 310 300 L 340 380 L 180 380 Z" fill="#e8e0c8"/>
<line x1="260" y1="380" x2="260" y2="560" stroke="#2a2420" stroke-width="10"/>
<line x1="760" y1="900" x2="760" y2="1400" stroke="#1e1e1e" stroke-width="12"/>
<ellipse cx="760" cy="1400" rx="90" ry="16" fill="#1e1e1e"/>
<rect x="725" y="820" width="70" height="110" rx="30" fill="#2b2b2b"/>
<path d="M880 1200 L 1160 1200 L 1160 1500 L 880 1500 Z" fill="#3a2c22"/>
<path d="M860 1150 L 1180 1150 L 1180 1260 L 860 1260 Z" fill="#4a3a2d"/>"""
    return svg(w, h, body)


def album_cover() -> str:
    """Generic typographic sleeve. Deliberately not a copy of any real cover."""
    w, h = 1200, 1200
    body = f"""<rect width="{w}" height="{h}" fill="#1d3f8f"/>
<rect x="0" y="0" width="{w}" height="560" fill="#141414"/>
<rect x="80" y="80" width="520" height="400" fill="#d9d4c8"/>
<circle cx="340" cy="250" r="70" fill="#141414"/><rect x="250" y="320" width="180" height="160" rx="50" fill="#141414"/>
<text x="1120" y="200" font-family="{FONT}" font-weight="800" font-size="120" fill="#e2572b" text-anchor="end">VOL.1</text>
<text x="80" y="760" font-family="{FONT}" font-weight="900" font-size="230" fill="#f6efdf" letter-spacing="-8">HARD</text>
<text x="80" y="990" font-family="{FONT}" font-weight="900" font-size="230" fill="#f6efdf" letter-spacing="-8">BOP</text>
<rect x="760" y="820" width="360" height="40" fill="#e2572b"/>
<text x="80" y="1120" font-family="{FONT}" font-weight="600" font-size="44" fill="#f6efdf">TEST RECORDS · SESSION No. 1 · 1957</text>"""
    return svg(w, h, body)


@dataclass
class Spec:
    id: str
    title: str
    draw: Callable[[], str]
    cutout: bool  # True = object on a backdrop to be removed
    tone: str = "color"  # "bw" for archive-looking prints
    duotone: str | None = None  # print tone for whole photos
    models: tuple[str, ...] = ()


SPECS: list[Spec] = [
    Spec("nyc_skyline", "Нью-Йорк, панорама (тест)", skyline, cutout=False, tone="bw", duotone="blue"),
    Spec("ocean_liner", "Трансатлантический лайнер (тест)", ocean_liner, cutout=True, tone="bw"),
    Spec("man_hat_a", "Мужчина в шляпе — «Альфред Лайон» (тест)", lambda: man_in_hat(-20), cutout=True, tone="bw"),
    Spec("man_hat_b", "Мужчина в шляпе — «Фрэнсис Вольф» (тест)", lambda: man_in_hat(25, "#262626"), cutout=True, tone="bw"),
    Spec("night_club", "Ночной клуб, сцена (тест)", night_club, cutout=False, tone="bw", duotone="ink"),
    Spec("trumpeter", "Трубач, силуэт (тест)", trumpeter, cutout=True, tone="bw"),
    Spec("wall_clock", "Настенные часы, 3:00 (тест)", clock, cutout=True),
    Spec("trumpet", "Труба (тест)", trumpet, cutout=True),
    Spec("living_room", "Гостиная-студия (тест)", living_room, cutout=False, tone="bw", duotone="sepia"),
    Spec("tape_recorder", "Катушечный магнитофон (тест)", tape_recorder, cutout=True,
         models=("birefnet-general-lite", "isnet-general-use")),
    Spec("ribbon_mic", "Ленточный микрофон (тест)", microphone, cutout=True),
    Spec("album_cover", "Типографская обложка (тест)", album_cover, cutout=False),
    Spec("vinyl", "Виниловая пластинка (тест)", vinyl, cutout=True),
    Spec("drum_kit", "Ударная установка (тест)", drum_kit, cutout=True),
    Spec("saxophone", "Саксофон (тест)", saxophone, cutout=True),
    Spec("drummer", "Барабанщик, силуэт (тест)", drummer, cutout=True, tone="bw"),
    Spec("sax_player", "Саксофонист, силуэт (тест)", sax_player, cutout=True, tone="bw"),
]


def age_photo(img: Image.Image, tone: str, seed: int) -> Image.Image:
    """Make a clean render look like a print: soften, grain, vignette."""
    rng = np.random.default_rng(seed)
    img = img.convert("RGB").filter(ImageFilter.GaussianBlur(1.1))
    a = np.asarray(img).astype(np.float32) / 255
    if tone == "bw":
        g = a @ np.array([0.3, 0.59, 0.11], dtype=np.float32)
        a = np.stack([g * 1.02, g * 0.99, g * 0.94], axis=-1)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / w) ** 2 + ((yy - h / 2) / h) ** 2)
    a *= (1 - 0.35 * np.clip(r - 0.25, 0, 1))[..., None]
    a += rng.normal(0, 0.035, (h, w, 1)).astype(np.float32)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def generate(pd: ProjectDir, only: list[str] | None = None) -> list[AssetMeta]:
    out = []
    for i, spec in enumerate(SPECS):
        if only and spec.id not in only:
            continue
        png = cairosvg.svg2png(bytestring=spec.draw().encode())
        img = age_photo(Image.open(io.BytesIO(png)), spec.tone, seed=i)
        path = pd.abs(f"assets/originals/{spec.id}.jpg")
        img.save(path, quality=92)
        meta = AssetMeta(
            id=spec.id,
            title=spec.title,
            query=spec.title,
            source="test_generator",
            author="cbroll procedural test asset",
            license="generated placeholder",
            status="test_placeholder",
            original=pd.rel(path),
            cut=spec.cutout,
            tone=spec.duotone,
            models=list(spec.models),
            width=img.width,
            height=img.height,
        )
        pd.save_meta(meta)
        out.append(meta)
    return out

