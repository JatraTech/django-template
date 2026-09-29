from __future__ import annotations

from typing import TypedDict

from backstage.theme_tokens import rgb_to_space_separated
from backstage.utils import hex_to_rgb

_PRIMARY_WEIGHTS = ("50", "100", "200", "300", "400", "500", "600", "700", "800", "900", "950")

DEFAULT_ACCENT_PALETTE = "red"


class AccentPaletteDefinition(TypedDict):
    label: str
    preview_hex: str
    light: dict[str, str]
    dark_primary_500: str
    dark_primary_600: str


def _hex_scale(values: dict[str, str]) -> dict[str, str]:
    return {weight: rgb_to_space_separated(hex_value) for weight, hex_value in values.items()}


def _palette(
    label: str,
    shades: dict[str, str],
    dark_500: str,
    dark_600: str,
) -> AccentPaletteDefinition:
    light = _hex_scale(shades)
    return {
        "label": label,
        "preview_hex": shades["500"],
        "light": light,
        "dark_primary_500": rgb_to_space_separated(dark_500),
        "dark_primary_600": rgb_to_space_separated(dark_600),
    }


# Tailwind CSS v4 default palette hex values
_PALETTE_SHADES: dict[str, dict[str, str]] = {
    "red": {
        "50": "#fef2f2",
        "100": "#fee2e2",
        "200": "#fecaca",
        "300": "#fca5a5",
        "400": "#f87171",
        "500": "#ef4444",
        "600": "#dc2626",
        "700": "#b91c1c",
        "800": "#991b1b",
        "900": "#7f1d1d",
        "950": "#450a0a",
    },
    "rose": {
        "50": "#fff1f2",
        "100": "#ffe4e6",
        "200": "#fecdd3",
        "300": "#fda4af",
        "400": "#fb7185",
        "500": "#f43f5e",
        "600": "#e11d48",
        "700": "#be123c",
        "800": "#9f1239",
        "900": "#881337",
        "950": "#4c0519",
    },
    "orange": {
        "50": "#fff7ed",
        "100": "#ffedd5",
        "200": "#fed7aa",
        "300": "#fdba74",
        "400": "#fb923c",
        "500": "#f97316",
        "600": "#ea580c",
        "700": "#c2410c",
        "800": "#9a3412",
        "900": "#7c2d12",
        "950": "#431407",
    },
    "amber": {
        "50": "#fffbeb",
        "100": "#fef3c7",
        "200": "#fde68a",
        "300": "#fcd34d",
        "400": "#fbbf24",
        "500": "#f59e0b",
        "600": "#d97706",
        "700": "#b45309",
        "800": "#92400e",
        "900": "#78350f",
        "950": "#451a03",
    },
    "emerald": {
        "50": "#ecfdf5",
        "100": "#d1fae5",
        "200": "#a7f3d0",
        "300": "#6ee7b7",
        "400": "#34d399",
        "500": "#10b981",
        "600": "#059669",
        "700": "#047857",
        "800": "#065f46",
        "900": "#064e3b",
        "950": "#022c22",
    },
    "teal": {
        "50": "#f0fdfa",
        "100": "#ccfbf1",
        "200": "#99f6e4",
        "300": "#5eead4",
        "400": "#2dd4bf",
        "500": "#14b8a6",
        "600": "#0d9488",
        "700": "#0f766e",
        "800": "#115e59",
        "900": "#134e4a",
        "950": "#042f2e",
    },
    "blue": {
        "50": "#eff6ff",
        "100": "#dbeafe",
        "200": "#bfdbfe",
        "300": "#93c5fd",
        "400": "#60a5fa",
        "500": "#3b82f6",
        "600": "#2563eb",
        "700": "#1d4ed8",
        "800": "#1e40af",
        "900": "#1e3a8a",
        "950": "#172554",
    },
    "indigo": {
        "50": "#eef2ff",
        "100": "#e0e7ff",
        "200": "#c7d2fe",
        "300": "#a5b4fc",
        "400": "#818cf8",
        "500": "#6366f1",
        "600": "#4f46e5",
        "700": "#4338ca",
        "800": "#3730a3",
        "900": "#312e81",
        "950": "#1e1b4b",
    },
    "violet": {
        "50": "#f5f3ff",
        "100": "#ede9fe",
        "200": "#ddd6fe",
        "300": "#c4b5fd",
        "400": "#a78bfa",
        "500": "#8b5cf6",
        "600": "#7c3aed",
        "700": "#6d28d9",
        "800": "#5b21b6",
        "900": "#4c1d95",
        "950": "#2e1065",
    },
    "slate": {
        "50": "#f8fafc",
        "100": "#f1f5f9",
        "200": "#e2e8f0",
        "300": "#cbd5e1",
        "400": "#94a3b8",
        "500": "#64748b",
        "600": "#475569",
        "700": "#334155",
        "800": "#1e293b",
        "900": "#0f172a",
        "950": "#020617",
    },
    "zinc": {
        "50": "#fafafa",
        "100": "#f4f4f5",
        "200": "#e4e4e7",
        "300": "#d4d4d8",
        "400": "#a1a1aa",
        "500": "#71717a",
        "600": "#52525b",
        "700": "#3f3f46",
        "800": "#27272a",
        "900": "#18181b",
        "950": "#09090b",
    },
}

_PALETTE_LABELS: dict[str, str] = {
    "red": "Red",
    "rose": "Rose",
    "orange": "Orange",
    "amber": "Amber",
    "emerald": "Emerald",
    "teal": "Teal",
    "blue": "Blue",
    "indigo": "Indigo",
    "violet": "Violet",
    "slate": "Slate",
    "zinc": "Zinc",
}


def _build_all_palettes() -> dict[str, AccentPaletteDefinition]:
    palettes: dict[str, AccentPaletteDefinition] = {}
    for key, shades in _PALETTE_SHADES.items():
        palettes[key] = _palette(
            label=_PALETTE_LABELS[key],
            shades=shades,
            dark_500=shades["400"],
            dark_600=shades["500"],
        )
    return palettes


ACCENT_PALETTES: dict[str, AccentPaletteDefinition] = _build_all_palettes()

ACCENT_PALETTE_CHOICES = [(key, ACCENT_PALETTES[key]["label"]) for key in ACCENT_PALETTES]


def get_accent_palette(key: str | None) -> AccentPaletteDefinition:
    palette_key = key if key in ACCENT_PALETTES else DEFAULT_ACCENT_PALETTE
    return ACCENT_PALETTES[palette_key]


def resolve_palette_key(settings_obj: object | None) -> str:
    if settings_obj is not None:
        palette = getattr(settings_obj, "accent_palette", None)
        if palette and palette in ACCENT_PALETTES:
            return palette
    return DEFAULT_ACCENT_PALETTE


def resolve_palette_scale(settings_obj: object | None) -> dict[str, str]:
    palette = get_accent_palette(resolve_palette_key(settings_obj))
    return dict(palette["light"])


def resolve_dark_primary_overrides(settings_obj: object | None) -> dict[str, str]:
    palette = get_accent_palette(resolve_palette_key(settings_obj))
    return {
        "500": palette["dark_primary_500"],
        "600": palette["dark_primary_600"],
    }


def nearest_palette_key(accent_hex: str) -> str:
    target = hex_to_rgb(accent_hex.lstrip("#"))
    best_key = DEFAULT_ACCENT_PALETTE
    best_distance = float("inf")
    for key, palette in ACCENT_PALETTES.items():
        preview = hex_to_rgb(palette["preview_hex"].lstrip("#"))
        distance = sum((a - b) ** 2 for a, b in zip(target, preview, strict=True))
        if distance < best_distance:
            best_distance = distance
            best_key = key
    return best_key
