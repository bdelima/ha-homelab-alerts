"""Config flow for Homelab Alerts.

One-time setup, no fields: this integration exists only to install its
bundled automation blueprint (see __init__.py). The actual configuration
-- which mobile_app device(s) get notified, and each severity's Android
channel name / Do Not Disturb bypass -- lives on the blueprint itself,
set when you create an automation from it, the same split
ha-portainer-dashboard uses between its config flow and its blueprint
inputs. Only one instance is needed.
"""
from __future__ import annotations

from typing import Any

from homeassistant import config_entries

from .const import DOMAIN


class HomelabAlertsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Homelab Alerts."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            # There's no supported way for a config flow to hand the
            # browser off to the automation editor on completion (same
            # conclusion ha-portainer-dashboard's config_flow.py reached,
            # and for the same reason: no query param on the automation
            # editor, and the my.home-assistant.io blueprint_import
            # redirect is for importing a blueprint from a URL, not
            # creating an automation from one already installed
            # locally). A one-time persistent notification with a direct
            # link is the closest available nudge. The link path is
            # /config/automation/dashboard -- singular "automation", the
            # real frontend route; an earlier version used the plural
            # form, which isn't a route and opened a blank page.
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "notification_id": "homelab_alerts_setup_next_step",
                    "title": "Homelab Alerts: one more step",
                    "message": (
                        "Setup is complete. To actually route alerts to "
                        "your phone, create an automation from the "
                        "bundled blueprint: "
                        "[Automations](/config/automation/dashboard) "
                        "-> **Add Automation** -> **Use Blueprint** -> "
                        '"Homelab Alerts".'
                    ),
                },
            )
            return self.async_create_entry(title="Homelab Alerts", data={})

        return self.async_show_form(step_id="user")
