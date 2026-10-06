# Homelab Alerts

A small Home Assistant custom integration that turns [homelab-ops](https://github.com/bdelima/homelab-ops)'s
MQTT alerting into phone pushes and Home Assistant persistent
notifications, routed by severity.

## What it does

homelab-ops publishes a small JSON payload to `homelab/alerts/<unit>` for
anything worth knowing about on drakebay/ojochal/naples: a backup that
didn't finish, a mount that's genuinely broken, a SMART attribute
trending up, a backup that completed cleanly. Each payload looks like:

```json
{"host": "naples", "unit": "mergerfs-balance", "severity": "warning", "message": "The mergerfs balance did not complete. Run ‘storage-tiering-status’ on naples for more information."}
```

`severity` is one of `info`, `warning`, or `critical` -- a flat,
shared vocabulary across every module, not a different set per module.
Each module decides its own severity for a given event; this integration
only decides what severity *sounds and looks like* on your phone.

This integration itself does almost nothing: on load, it installs a
bundled automation blueprint into your HA config. The blueprint is where
the actual behavior lives:

- Subscribes to `homelab/alerts/+` (every unit, no per-source wiring
  needed as new alert sources are added on the homelab-ops side).
- Resolves the payload's severity to one of three Android notification
  channels -- Info / Warning / Critical by default, fully renameable.
- Marks each severity so it reads at a glance: an emoji at the start of
  the title (info ℹ️, warning ⚠️, critical ❗) and, on the phone push, a
  matching Android status-bar icon and color (information / alert /
  alert-circle, in blue / amber / red). The persistent notification's
  title gets the same emoji. These are fixed in the blueprint, not
  inputs; the status-bar icon and color are Android-only.
- Each of those three channels has its own independent "Bypass Do Not
  Disturb" toggle (off by default). When on, that severity's pushes use
  Android's reserved `alarm_stream` channel instead -- the same mechanism
  a phone alarm clock uses, shared phone-wide, not exclusive to this
  integration.
- Each severity also has two on/off toggles: **Mobile Notification** (the
  phone push) and **Persistent Notification** (an entry in Home
  Assistant's own notification panel, the bell in the sidebar). Both are
  on by default. A persistent notification is created fresh for every
  alert and stays until you dismiss it, so an alert that repeats adds a
  new entry each time. With Mobile Notification off for a severity, that
  severity's channel and Bypass-Do-Not-Disturb settings are simply unused.
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
   optionally rename each severity's channel, turn on its
   Bypass-Do-Not-Disturb toggle, or turn its Mobile and Persistent
   notifications on or off. Save.
4. On the homelab-ops side, make sure your MQTT broker config
   (`mqtt.conf`) matches whatever broker this Home Assistant instance's
   own MQTT integration is using -- see homelab-ops's own docs for that
   half.

That's it. Any alert homelab-ops publishes now reaches your phone,
grouped by severity into whichever channel you configured, and shows up
in Home Assistant's notification panel, for each severity whose toggles
are on.

Upgrading from 1.0.x: the new toggles default to Mobile on (so phone
pushes behave exactly as before) and Persistent on (so you will start
seeing persistent notifications for every severity until you turn them
off). Existing automations pick up the new defaults without being
edited, once Home Assistant restarts and the integration re-installs the
updated blueprint.

## Design notes

See homelab-ops's
[module architecture doc, section 6 ("Alert wiring and severity")](https://github.com/bdelima/homelab-ops/blob/main/docs/module-architecture.md#6-alert-wiring-and-severity)
for the full reasoning behind the severity model (why three flat levels
instead of per-module sets), the JSON payload shape, and why some
scripts (`run-backup.sh`, `smart-check.sh`, `mount-healthcheck.sh`) call
`mqtt-alert.sh` directly rather than relying solely on the generic
`OnFailure=` wrapper.

This repo follows the same blueprint-bundling pattern as
[ha-portainer-dashboard](https://github.com/bdelima/ha-portainer-dashboard)'s
`portainer_maintenance` integration -- see that repo's `__init__.py` and
its blueprint's per-category channel/bypass-DND inputs for the
precedent this one builds on directly.
