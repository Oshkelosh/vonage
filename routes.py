"""Vonage addon routes."""

from __future__ import annotations

from typing import Any

from app.addons.notifications.shared_routes import build_notification_routers


def _parse_vonage_config_form(form: Any) -> tuple[dict[str, Any], bool]:
    return (
        {
            "api_key": form.get("api_key", ""),
            "api_secret": form.get("api_secret", ""),
            "from_number": form.get("from_number", ""),
        },
        form.get("is_enabled") == "on",
    )


admin_router, jinja_env = build_notification_routers(
    "vonage",
    template_name="vonage_config.html",
    page_title="Vonage Settings",
    secret_keys=("api_secret",),
    parse_config_form=_parse_vonage_config_form,
)
