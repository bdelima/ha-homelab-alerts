# Homelab Alerts

A small Home Assistant custom integration that turns [homelab-ops](https://github.com/bdelima/homelab-ops)'s
MQTT alerting into phone pushes, routed to the right Android notification
channel by severity.

## What it does

homelab-ops publishes a small JSON payload to `homelab/alerts/<unit>` for
anything worth knowing about on drakebay/ojochal/naples: a backup that
didn't finish, a mount that's genuinely broken, a SMART attribute
trending up, a backup that completed cleanly. Each payload looks like:

```json
{"host": "naples", "unit": "mergerfs-balance", "severity": "warning", "message": "naples: mergerfs-balance.service failed -- run: storage-tiering-status.sh"}
```

`severity` is one of `info`, `warning`, or `critical` -- a flat,
shared vocabulary across every module, not a different set per module.
Each module decides its own severity for a given event; this integration
only decides what severity *sounds like* on your phone.

This integration itself does almost nothing: on load, it installs a
bundled automation blueprint into your HA config. The blueprint is where
the actual behavior lives:

- Subscribes to `homelab/alerts/+` (every unit, no per-source wiring
  needed as new alert sources are added on the homelab-ops side).
- Resolves the payload's severity to one of three Android notification
  channels -- Info / Warning / Critical by default, fully renameable.
- Each of those three channels has its own independent "Bypass Do Not
  Disturb" toggle (off by default). When on, that severity's pushes use
  Android's reserved `alarm_stream` channel instead -- the same mechanism
  a phone alarm clock uses, shared phone-wide, not exclusive to this
  integration.
- Once a channel exists on your phone, Android's own per-channel
  notification settings (sound, importance, lock-screen visibility, or
  turning a whole severity off) are yours to adjust at any time -- this
  blueprint only creates the channel and routes to it.

No iOS support -- `alarm_stream`/Do-Not-Disturb-bypass is an
Android-specific mechanism (the `channel` key in a mobile_app
notification's `data` block is simply ignored on iOS), and there are no
iOS devices in this household to build the equivalent for.

## Setup

1. Install via [HACS](https://hacs.xyz/): add this repository as a
   custom repository (**HACS -> Integrations -> ... -> Custom
   repositories**, `bdelima/ha-homelab-alerts`), then install "Homelab
   Alerts" like any other HACS integration.
2. **Settings -> Devices & Services -> Add Integration -> Homelab
   Alerts.** No fields to fill in -- this step just installs the bundled
   blueprint.
3. **Settings -> Automations & Scenes -> Add Automation -> Use Blueprint
   -> "Homelab Alerts".** Pick the mobile_app device(s) to notify, and
   optionally rename each severity's channel or turn on its
   Bypass-Do-Not-Disturb toggle. Save.
4. On the homelab-ops side, make sure your MQTT broker config
   (`mqtt.conf`) matches whatever broker this Home Assistant instance's
   own MQTT integration is using -- see homelab-ops's own docs for that
   half.

That's it. Any alert homelab-ops publishes now reaches your phone,
grouped by severity into whichever channel you configured.

## Design notes

See [homelab-ops](https://github.com/bdelima/homelab-ops)'s own
Backup System Design documentation for the full reasoning behind the
severity model (why three flat levels instead of per-module sets),
the JSON payload shape, and why some scripts (`run-backup.sh`,
`smart-check.sh`, `mount-healthcheck.sh`) call `mqtt-alert.sh` directly
rather than relying solely on the generic `OnFailure=` wrapper.

This repo follows the same blueprint-bundling pattern as
[ha-portainer-dashboard](https://github.com/bdelima/ha-portainer-dashboard)'s
`portainer_maintenance` integration -- see that repo's `__init__.py` and
its blueprint's per-category channel/bypass-DND inputs for the
precedent this one builds on directly.
