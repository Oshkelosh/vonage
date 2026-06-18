"""Minimal unit tests for the vonage addon."""

from app.addons.notifications.vonage.addon import VonageAddon


def test_addon_identity():
    assert VonageAddon.addon_id == "vonage"
    assert VonageAddon.addon_category == "notification"
