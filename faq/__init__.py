"""FAQ package for screen-aware help UI and data."""

from .faq_component import get_current_screen_id, render_faq_button, render_faq_popup
from .faq_data import FAQ_DATA

__all__ = [
    "FAQ_DATA",
    "get_current_screen_id",
    "render_faq_button",
    "render_faq_popup",
]
