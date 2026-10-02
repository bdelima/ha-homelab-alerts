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
            # browser off to the automation editor on completion: the
            # frontend passes "create from this blueprint" to the editor
            # through in-memory state, not a URL or query param, so no link
            # can open that screen directly. The closest available nudge
            # is a one-time persistent notification linking to the
            # Blueprints page, where clicking the "Homelab Alerts" row
            # opens the editor already pre-filled with this blueprint.
            #
            # Route note: the frontend's config routes are singular
            # (/config/blueprint, /config/automation). An earlier version
            # of this link used the plural /config/automations/dashboard,
            # which isn't a route and opened a blank page.
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "notification_id": "homelab_alerts_setup_next_step",
                    "title": "Homelab Alerts: one more step",
                    "message": (
                        "Setup is complete. To actually route alerts to "
                        "your phone, create an automation from the "
                        "bundled blueprint: open "
                        "[Blueprints](/config/blueprint/dashboard) and "
                        'click **"Homelab Alerts"**.'
                    ),
                },
            )
            return self.async_create_entry(title="Homelab Alerts", data={})

        return self.async_show_form(step_id="user")
