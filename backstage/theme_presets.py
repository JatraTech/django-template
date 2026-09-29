from __future__ import annotations

from typing import TypedDict


class ThemePresetValues(TypedDict):
    border_radius: str
    sidebar_density: str


THEME_PRESETS: dict[str, ThemePresetValues] = {
    "default": {
        "border_radius": "6px",
        "sidebar_density": "comfortable",
    },
    "minimal": {
        "border_radius": "10px",
        "sidebar_density": "comfortable",
    },
    "compact": {
        "border_radius": "6px",
        "sidebar_density": "compact",
    },
}

DEFAULT_THEME_PRESET = "minimal"

FONT_FAMILIES: dict[str, str] = {
    "inter": '"Inter", system-ui, sans-serif',
    "system": 'system-ui, -apple-system, "Segoe UI", sans-serif',
    "serif": 'Georgia, "Times New Roman", serif',
    "mono": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
    "rounded": 'ui-rounded, "SF Pro Rounded", system-ui, sans-serif',
}

SIDEBAR_WIDTHS: dict[str, str] = {
    "comfortable": "280px",
    "compact": "240px",
}
