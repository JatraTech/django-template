from __future__ import annotations

import copy
import re
from typing import Any

from backstage.settings import CONFIG_DEFAULTS
from backstage.theme_presets import (
    DEFAULT_THEME_PRESET,
    FONT_FAMILIES,
    SIDEBAR_WIDTHS,
    THEME_PRESETS,
)
from backstage.utils import convert_color, hex_to_rgb

_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{6})$")
_RGB_SPACE_RE = re.compile(r"^(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})$")

_PRIMARY_WEIGHTS = ("50", "100", "200", "300", "400", "500", "600", "700", "800", "900", "950")
_PRIMARY_LIGHTNESS = {
    "50": 0.96,
    "100": 0.92,
    "200": 0.84,
    "300": 0.72,
    "400": 0.58,
    "500": 0.46,
    "600": 0.38,
    "700": 0.32,
    "800": 0.26,
    "900": 0.20,
    "950": 0.14,
}


def normalize_hex(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Color value is required.")

    if cleaned.startswith("#"):
        cleaned = cleaned[1:]

    if _RGB_SPACE_RE.match(cleaned):
        r, g, b = (int(part) for part in cleaned.split())
        return f"#{r:02x}{g:02x}{b:02x}"

    if cleaned.startswith("rgb"):
        inner = cleaned[cleaned.find("(") + 1 : cleaned.find(")")]
        parts = [part.strip() for part in inner.split(",")]
        if len(parts) != 3:
            raise ValueError(f"Invalid rgb color: {value}")
        r, g, b = (int(part) for part in parts)
        return f"#{r:02x}{g:02x}{b:02x}"

    if _HEX_RE.match(cleaned):
        return f"#{cleaned.lower()}"

    raise ValueError(f"Invalid color format: {value}")


def rgb_to_space_separated(hex_color: str) -> str:
    r, g, b = hex_to_rgb(normalize_hex(hex_color).lstrip("#"))
    return f"{r} {g} {b}"


def _rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    r_norm, g_norm, b_norm = r / 255, g / 255, b / 255
    max_c = max(r_norm, g_norm, b_norm)
    min_c = min(r_norm, g_norm, b_norm)
    lightness = (max_c + min_c) / 2

    if max_c == min_c:
        return 0.0, 0.0, lightness

    delta = max_c - min_c
    saturation = delta / (2 - max_c - min_c) if lightness > 0.5 else delta / (max_c + min_c)

    if max_c == r_norm:
        hue = ((g_norm - b_norm) / delta) % 6
    elif max_c == g_norm:
        hue = ((b_norm - r_norm) / delta) + 2
    else:
        hue = ((r_norm - g_norm) / delta) + 4

    return hue * 60, saturation, lightness


def _hsl_to_rgb(hue: float, saturation: float, lightness: float) -> tuple[int, int, int]:
    if saturation == 0:
        value = round(lightness * 255)
        return value, value, value

    def _hue_to_rgb(p: float, q: float, t: float) -> float:
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    q = lightness * (1 + saturation) if lightness < 0.5 else lightness + saturation - lightness * saturation
    p = 2 * lightness - q
    hue_norm = (hue % 360) / 360
    r = _hue_to_rgb(p, q, hue_norm + 1 / 3)
    g = _hue_to_rgb(p, q, hue_norm)
    b = _hue_to_rgb(p, q, hue_norm - 1 / 3)
    return round(r * 255), round(g * 255), round(b * 255)


def derive_primary_scale(accent_hex: str) -> dict[str, str]:
    normalized = normalize_hex(accent_hex)
    r, g, b = hex_to_rgb(normalized.lstrip("#"))
    hue, saturation, _lightness = _rgb_to_hsl(r, g, b)
    saturation = min(1.0, max(0.35, saturation))

    scale: dict[str, str] = {}
    for weight in _PRIMARY_WEIGHTS:
        target_lightness = _PRIMARY_LIGHTNESS[weight]
        red, green, blue = _hsl_to_rgb(hue, saturation, target_lightness)
        scale[weight] = f"{red} {green} {blue}"

    scale["500"] = rgb_to_space_separated(normalized)
    return scale


def merge_color_palettes(*palettes: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    merged: dict[str, dict[str, str]] = copy.deepcopy(CONFIG_DEFAULTS["COLORS"])

    for palette in palettes:
        if not isinstance(palette, dict):
            continue
        for name, weights in palette.items():
            if not isinstance(weights, dict):
                continue
            merged.setdefault(name, {})
            merged[name].update(weights)

    return merged


def resolve_accent_hex(settings_obj: Any | None) -> str:
    from backstage.accent_palettes import get_accent_palette, resolve_palette_key

    palette = get_accent_palette(resolve_palette_key(settings_obj))
    return palette["preview_hex"]


def resolve_accent_dark_hex(settings_obj: Any | None, accent_hex: str) -> str:
    from backstage.accent_palettes import get_accent_palette, resolve_palette_key

    palette = get_accent_palette(resolve_palette_key(settings_obj))
    dark_rgb = palette["dark_primary_600"]
    r, g, b = (int(part) for part in dark_rgb.split())
    return f"#{r:02x}{g:02x}{b:02x}"


def build_theme_tokens(settings_obj: Any | None = None) -> dict[str, Any]:
    theme_preset = DEFAULT_THEME_PRESET
    font_family = "inter"
    sidebar_density = "comfortable"
    custom_css = ""

    if settings_obj is not None:
        theme_preset = getattr(settings_obj, "theme_preset", None) or DEFAULT_THEME_PRESET
        font_family = getattr(settings_obj, "font_family", None) or "inter"
        sidebar_density = getattr(settings_obj, "sidebar_density", None) or "comfortable"
        custom_css = getattr(settings_obj, "custom_css", "") or ""

    from backstage.accent_palettes import (
        get_accent_palette,
        resolve_dark_primary_overrides,
        resolve_palette_key,
        resolve_palette_scale,
    )

    preset_values = THEME_PRESETS.get(theme_preset, THEME_PRESETS[DEFAULT_THEME_PRESET])
    palette_key = resolve_palette_key(settings_obj)
    palette = get_accent_palette(palette_key)
    accent_hex = palette["preview_hex"]
    accent_dark_hex = resolve_accent_dark_hex(settings_obj, accent_hex)
    primary_scale = resolve_palette_scale(settings_obj)
    dark_primary_overrides = resolve_dark_primary_overrides(settings_obj)

    border_radius = preset_values["border_radius"]

    return {
        "theme_preset": theme_preset,
        "font_family": font_family,
        "sidebar_density": sidebar_density,
        "border_radius": border_radius,
        "accent_hex": accent_hex,
        "accent_dark_hex": accent_dark_hex,
        "accent_palette": palette_key,
        "primary_scale": primary_scale,
        "dark_primary_overrides": dark_primary_overrides,
        "font_stack": FONT_FAMILIES.get(font_family, FONT_FAMILIES["inter"]),
        "sidebar_width": SIDEBAR_WIDTHS.get(sidebar_density, SIDEBAR_WIDTHS["comfortable"]),
        "custom_css": custom_css,
    }


def _semantic_token_lines(dark: bool = False) -> list[str]:
    if dark:
        return [
            "  --background: var(--color-base-950);",
            "  --foreground: var(--color-base-50);",
            "  --card: var(--color-base-900);",
            "  --card-foreground: var(--color-base-50);",
            "  --muted: var(--color-base-800);",
            "  --muted-foreground: var(--color-base-400);",
            "  --border: color-mix(in oklab, var(--color-base-700) 48%, transparent);",
            "  --border-subtle: var(--border);",
            "  --input: var(--border);",
            "  --input-background: var(--color-base-900);",
            "  --ring: color-mix(in oklab, var(--color-primary-500) 30%, transparent);",
            "  --elevation-card: 0 1px 3px 0 rgb(0 0 0 / 0.12), 0 1px 2px -1px rgb(0 0 0 / 0.08);",
            "  --primary-foreground: rgb(255 255 255);",
        ]
    return [
        "  --background: var(--color-base-100);",
        "  --foreground: var(--color-base-900);",
        "  --card: rgb(255 255 255);",
        "  --card-foreground: var(--color-base-900);",
        "  --muted: var(--color-base-200);",
        "  --muted-foreground: var(--color-base-500);",
        "  --border: color-mix(in oklab, var(--color-base-300) 80%, transparent);",
        "  --border-subtle: var(--border);",
        "  --input: var(--border);",
        "  --input-background: var(--background);",
        "  --ring: color-mix(in oklab, var(--color-primary-500) 25%, transparent);",
        "  --elevation-card: 0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06);",
        "  --primary-foreground: rgb(255 255 255);",
    ]


def build_theme_css(tokens: dict[str, Any]) -> str:
    lines = [
        ":root {",
        f"  --border-radius: {tokens['border_radius']};",
        f"  --radius: {tokens['border_radius']};",
        f"  --font-sans: {tokens['font_stack']};",
        f"  --sidebar-width-comfortable: {SIDEBAR_WIDTHS['comfortable']};",
        f"  --sidebar-width-compact: {SIDEBAR_WIDTHS['compact']};",
        f"  --backstage-sidebar-width: {tokens['sidebar_width']};",
    ]

    for palette_name in ("base", "font"):
        for weight, value in CONFIG_DEFAULTS["COLORS"].get(palette_name, {}).items():
            lines.append(f"  --color-{palette_name}-{weight}: {value};")

    for weight, value in tokens["primary_scale"].items():
        css_value = convert_color(value)
        lines.append(f"  --color-primary-{weight}: {css_value};")

    lines.extend(_semantic_token_lines())
    lines.append("}")
    lines.append("")
    lines.append(".dark {")
    lines.extend(_semantic_token_lines(dark=True))
    for weight, value in tokens.get("dark_primary_overrides", {}).items():
        css_value = convert_color(value)
        lines.append(f"  --color-primary-{weight}: {css_value};")
    lines.append("}")
    lines.append("")

    custom_css = (tokens.get("custom_css") or "").strip()
    if custom_css:
        lines.append("/* Custom admin CSS */")
        lines.append(custom_css)
        lines.append("")

    return "\n".join(lines)
