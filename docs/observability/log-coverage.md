# Log Coverage

## Primary Source

Persistent systemd journal at `/var/log/journal` is the primary system log surface.

It is expected to cover:

- kernel events
- NVIDIA driver and GPU-related kernel messages
- system services
- authentication and sudo activity routed through journald
- container and service lifecycle events that reach the journal

Journal entries are enriched with normalized metadata for dashboards:

- `log_domain`: `kernel` or `service`
- `log_category`: `kernel`, `system-service`, `gpu-driver`, or `container-runtime`
- `vendor`: `linux`, `nvidia`, or `container`

## Direct File Tails

Direct file tails are reserved for Ubuntu maintenance and installation history:

- `/var/log/cloud-init.log`
- `/var/log/cloud-init-output.log`
- `/var/log/dpkg.log`
- `/var/log/apt/history.log`
- `/var/log/apt/term.log`
- `/var/log/installer/curtin-install.log`
- `/var/log/installer/installer-journal.txt`
- `/var/log/installer/subiquity-client-debug.log`
- `/var/log/installer/subiquity-client-info.log`
- `/var/log/installer/subiquity-server-debug.log`
- `/var/log/installer/subiquity-server-info.log`
- `/var/log/installer/oemlog/oem-iso-cfg.log`

## Why This Split Exists

- Journal ingestion is better for active Linux and GPU events.
- Journal ingestion also gives a stable place to split kernel and NVIDIA activity away from service and container activity without duplicating syslog-style files.
- File ingestion is better for installer and package-management logs that are already stored as text history.
- Disk and filesystem event views come from journal queries plus filesystem capacity metrics, not from separate rotating disk log files.
- Avoid tailing `syslog`, `kern.log`, and similar files in parallel with journald because that would create duplicate event streams.
