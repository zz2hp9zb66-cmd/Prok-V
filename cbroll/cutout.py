"""Background removal and paper-collage styling.

Originals are only read. Outputs:
  assets/masks/<id>.png     8-bit alpha from the segmentation model
  assets/cutouts/<id>.png   RGBA, cropped to the object
  assets/styled/<id>.png    RGBA with a torn white paper border (cut-outs)
                            or a toned print with a paper margin (photos)
"""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image

from .project import ProjectDir
from .schemas import AssetMeta

DEFAULT_MODELS = ["birefnet-general-lite"]
_sessions: dict = {}


def _session(model: str):
    from rembg import new_session  # heavy import, keep it lazy

    if model not in _sessions:
        _sessions[model] = new_session(model)
    return _sessions[model]


def remove_background(img: Image.Image, models: list[str] = DEFAULT_MODELS) -> np.ndarray:
    """8-bit alpha mask for the main subject; several models are merged (union)."""
    from rembg import remove

    masks = [np.asarray(remove(img.convert("RGB"), session=_session(m), only_mask=True)) for m in models]
    return np.maximum.reduce(masks)


def clean_mask(mask: np.ndarray) -> np.ndarray:
    """Drop specks and fill pin-holes; keep soft edges."""
    hard = (mask > 127).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(hard, 8)
    if n > 1:
        biggest = stats[1:, cv2.CC_STAT_AREA].max()
        keep = np.zeros_like(hard)
        for i in range(1, n):
            if stats[i, cv2.CC_STAT_AREA] >= biggest * 0.02:
                keep[labels == i] = 1
        hard = keep
    hard = cv2.morphologyEx(hard, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    soft = cv2.GaussianBlur(mask, (3, 3), 0)
    return np.where(hard > 0, np.maximum(soft, 128), soft * (cv2.dilate(hard, np.ones((3, 3))) > 0)).astype(np.uint8)


def _noise_field(h: int, w: int, rng: np.random.Generator, scale: int) -> np.ndarray:
    small = rng.random((max(2, h // scale), max(2, w // scale))).astype(np.float32)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_CUBIC)


def torn_border(alpha: np.ndarray, width: int, seed: int) -> np.ndarray:
    """Mask of a hand-cut paper margin around `alpha` with an irregular edge."""
    rng = np.random.default_rng(seed)
    h, w = alpha.shape
    inside = (alpha > 100).astype(np.uint8)
    dist = cv2.distanceTransform(1 - inside, cv2.DIST_L2, 5)
    wobble = 0.55 * _noise_field(h, w, rng, 60) + 0.3 * _noise_field(h, w, rng, 14) + 0.15 * _noise_field(h, w, rng, 3)
    limit = width * (0.55 + 0.9 * wobble)
    border = (dist <= limit).astype(np.float32)
    return cv2.GaussianBlur(border, (3, 3), 0)


def paper_rgb(h: int, w: int, seed: int, color=(248, 244, 234)) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = np.ones((h, w, 3), np.float32) * np.array(color, np.float32) / 255
    fibre = (_noise_field(h, w, rng, 4) - 0.5) * 0.05 + (_noise_field(h, w, rng, 40) - 0.5) * 0.04
    return np.clip(base + fibre[..., None], 0, 1)


def crop_to_alpha(rgba: np.ndarray, pad: int) -> np.ndarray:
    ys, xs = np.nonzero(rgba[..., 3] > 8)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, rgba.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, rgba.shape[1])
    return rgba[y0:y1, x0:x1]


def style_cutout(rgba: np.ndarray, seed: int, border_frac: float = 0.022) -> np.ndarray:
    """Object on a torn white paper margin, like a scissor-cut magazine clipping."""
    width = max(8, int(max(rgba.shape[:2]) * border_frac))
    pad = width * 2
    rgba = np.pad(rgba, ((pad, pad), (pad, pad), (0, 0)))
    h, w = rgba.shape[:2]
    alpha = rgba[..., 3].astype(np.float32) / 255
    border = np.maximum(torn_border(rgba[..., 3], width, seed), alpha)
    paper = paper_rgb(h, w, seed)
    rgb = rgba[..., :3].astype(np.float32) / 255
    out_rgb = rgb * alpha[..., None] + paper * (1 - alpha[..., None])
    out = np.dstack([out_rgb, border])
    return crop_to_alpha((out * 255).astype(np.uint8), 2)


DUOTONES = {
    "blue": ((14, 26, 58), (239, 230, 210)),
    "sepia": ((34, 24, 16), (240, 226, 196)),
    "ink": ((18, 18, 18), (238, 234, 224)),
}


def duotone(rgb: np.ndarray, tone: str) -> np.ndarray:
    dark, light = (np.array(c, np.float32) / 255 for c in DUOTONES[tone])
    g = rgb.astype(np.float32) / 255 @ np.array([0.3, 0.59, 0.11], np.float32)
    g = np.clip((g - 0.08) / 0.84, 0, 1) ** 1.1  # a bit more contrast, like a newspaper print
    return dark + (light - dark) * g[..., None]


def style_print(img: Image.Image, seed: int, tone: str | None, margin_frac: float = 0.035) -> np.ndarray:
    """A photographic print: optional duotone, paper margin with slightly uneven edges."""
    rgb = np.asarray(img.convert("RGB"))
    toned = duotone(rgb, tone) if tone else rgb.astype(np.float32) / 255
    h, w = toned.shape[:2]
    m = int(max(h, w) * margin_frac)
    H, W = h + 2 * m, w + 2 * m
    canvas = paper_rgb(H, W, seed)
    canvas[m : m + h, m : m + w] = toned
    rect = np.zeros((H, W), np.uint8)
    rect[m // 3 : H - m // 3, m // 3 : W - m // 3] = 255
    alpha = torn_border(rect, max(3, m // 4), seed)
    return (np.dstack([canvas, alpha]) * 255).astype(np.uint8)


def process(pd: ProjectDir, meta: AssetMeta) -> AssetMeta:
    """Cut out or print-style one asset according to its meta (`cut`, `tone`, `models`)."""
    seed = sum(map(ord, meta.id))
    img = Image.open(pd.abs(meta.original))
    if meta.cut:
        mask = clean_mask(remove_background(img, meta.models or DEFAULT_MODELS))
        Image.fromarray(mask).save(pd.abs(f"assets/masks/{meta.id}.png"))
        rgba = np.dstack([np.asarray(img.convert("RGB")), mask])
        rgba = crop_to_alpha(rgba, 4)
        cut_path = pd.abs(f"assets/cutouts/{meta.id}.png")
        Image.fromarray(rgba).save(cut_path)
        meta.cutout = pd.rel(cut_path)
        styled = style_cutout(rgba, seed)
    else:
        styled = style_print(img, seed, meta.tone)
    styled_path = pd.abs(f"assets/styled/{meta.id}.png")
    Image.fromarray(styled).save(styled_path, optimize=True)
    meta.styled = pd.rel(styled_path)
    pd.save_meta(meta)
    return meta
