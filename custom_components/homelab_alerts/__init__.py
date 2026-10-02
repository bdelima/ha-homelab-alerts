"""Homelab Alerts.

On setup this integration installs its bundled automation blueprint into
HA's config dir (blueprints/automation/homelab_alerts/) -- that's its
entire job. No entities, no native services: everything the blueprint
needs (which mobile_app device(s) to notify, and the Android notification
channel + Do Not Disturb bypass for each of the three severities) is a
blueprint `!input`, set when you create an automation from it, not state
this integration needs to hold itself.

Kept as a real config-entry integration -- rather than nothing at all --
only so the blueprint gets (re-)installed automatically on every HA
start/reload, without a manual file copy into the config dir. Same
mechanism bdelima/ha-portainer-dashboard's portainer_maintenance
integration already uses (see its __init__.py); this is a smaller case of
exactly that pattern, since there's no webapp panel, no native services,
and no tracking sensors to also set up here.

The alerts themselves originate from homelab-ops (bdelima/homelab-ops):
mqtt-alert.sh publishes a small JSON payload --
{"host","unit","severity","message"} -- to homelab/alerts/<unit> for any
oneshot systemd unit on drakebay/ojochal/naples whose OnFailure= points at
homelab-alert@<unit>.service, plus a handful of scripts
(run-backup.sh/smart-check.sh/mount-healthcheck.sh) that publish directly
when their own internal state has more than one severity in a single run.
See that repo's Backup System Design doc for the full design discussion;
this integration and its blueprint are the HA-side half of that redesign.
"""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

BUNDLED_BLUEPRINTS_DIR = Path(__file__).parent / "bundled_blueprints"

BLUEPRINT_FILES = [
    (
        "automation/homelab_alerts.yaml",
        f"blueprints/automation/{DOMAIN}/homelab_alerts.yaml",
    ),
]


def _install_blueprints(hass: HomeAssistant) -> None:
    for src_rel, dest_rel in BLUEPRINT_FILES:
        src = BUNDLED_BLUEPRINTS_DIR / src_rel
        dest = Path(hass.config.path(dest_rel))
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dest)
        _LOGGER.debug("Installed blueprint %s -> %s", src, dest)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Homelab Alerts from a config entry."""
    await hass.async_add_executor_job(_install_blueprints, hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Homelab Alerts config entry.

    Nothing to tear down -- there are no entities or services, and the
    installed blueprint file is deliberately left in place (same as
    ha-portainer-dashboard: removing the integration doesn't retroactively
    break an automation you already built from its blueprint).
    """
    return True
