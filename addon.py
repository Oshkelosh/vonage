"""Vonage SMS notification integration."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field, SecretStr

from app.addons.notifications.base import NotificationAddon
from app.addons.log import info, warning
from app.addons.config_serialization import dump_addon_config


class VonageConfig(BaseModel):
    api_key: str = Field(default=..., description="Vonage API key")
    api_secret: SecretStr = Field(default=..., description="Vonage API secret")
    from_number: str = Field(default=..., description="Sender ID or phone number")

    @classmethod
    def config_model(cls):
        return cls


class VonageAddon(NotificationAddon):
    addon_id: str = "vonage"
    addon_name: str = "Vonage"
    addon_description: str = "Send SMS notifications via Vonage (Nexmo)."
    addon_category: str = "notification"
    version: str = "1.0.0"
    is_enabled: bool = False
    supported_channels: ClassVar[list[str]] = ["sms"]

    _config: Dict[str, Any] | None = None
    _api_key: str | None = None
    _api_secret: str | None = None
    _from_number: str | None = None

    @classmethod
    def config_schema(cls):
        return VonageConfig

    async def initialize(self, config: dict) -> None:
        validated = self.config_schema()(**config)
        self._config = dump_addon_config(validated)
        self._api_key = validated.api_key
        self._api_secret = validated.api_secret.get_secret_value()
        self._from_number = validated.from_number
        self.is_enabled = True
        info("Vonage", "Initialized (from={})", self._from_number)

    async def validate_config(self, config: dict) -> None:
        from app.core.exceptions import ValidationError

        validated = self.config_schema()(**config)
        api_secret = validated.api_secret.get_secret_value()
        if not api_secret:
            return
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                "https://rest.nexmo.com/account/get-balance",
                params={"api_key": validated.api_key, "api_secret": api_secret},
            )
        if resp.status_code == 401:
            raise ValidationError(message="Invalid API secret — check your credentials")
        if resp.status_code == 403:
            raise ValidationError(
                message="API secret is valid but missing required permissions: account:read"
            )
        if resp.status_code >= 400:
            data = resp.json() if resp.content else {}
            if isinstance(data, dict) and str(data.get("error-code", "")) in ("4", "3"):
                raise ValidationError(message="Invalid API secret — check your credentials")
            raise ValidationError(message="Vonage rejected the API credentials")

    async def shutdown(self) -> None:
        self._api_key = None
        self._api_secret = None
        self._from_number = None
        self.is_enabled = False

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> Dict[str, Any]:
        return self.channel_not_supported("email", to)

    async def send_sms(self, to: str, body: str) -> Dict[str, Any]:
        if not self._api_key or not self._api_secret or not self._from_number:
            return {"success": False, "message_id": "", "error": "Not configured", "to": to}

        payload = {
            "api_key": self._api_key,
            "api_secret": self._api_secret,
            "to": to,
            "from": self._from_number,
            "text": body,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://rest.nexmo.com/sms/json",
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                messages = data.get("messages", [])
                first = messages[0] if messages else {}
                status = first.get("status", "unknown")
                if status != "0":
                    error = first.get("error-text", f"Vonage status {status}")
                    warning("Vonage", "send_sms to={} error: {}", to, error)
                    return {"success": False, "message_id": "", "error": error, "to": to}
                return {
                    "success": True,
                    "message_id": first.get("message-id", ""),
                    "to": to,
                }
        except Exception as exc:
            warning("Vonage", "send_sms to={} error: {}", to, exc)
            return {"success": False, "message_id": "", "error": str(exc), "to": to}

    async def send_push(
        self,
        to: str,
        title: str,
        body: str,
        data: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return self.channel_not_supported("push", to)

    def get_routers(self) -> List[APIRouter]:
        return []

    def get_admin_routes(self) -> List[APIRouter]:
        from app.addons.notifications.vonage.routes import admin_router

        return [admin_router]

    def get_admin_templates(self) -> str:
        from pathlib import Path

        return str(Path(__file__).resolve().parent / "templates")

    def get_admin_static(self) -> str:
        from pathlib import Path

        return str(Path(__file__).resolve().parent / "static")
