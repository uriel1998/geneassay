# Changelog

## [Unreleased]

### Added

- Added `geneassay/geneassay-daemon.py`, a watched-control-file daemon that applies presence updates from `config/commands/current.json` and exits when that control file is deleted.
- Added `run-geneassay-daemon.sh`, an `fzf`-driven helper that selects a saved config, can launch dynamic updates for a running daemon, stages configs into the daemon control path, and can request daemon exit by deleting the control file.
- Added `dynamic_update.sh`, a `jq`-based helper that updates the active daemon control file from `--line1`, `--line2`, or a `yad` prompt.

### Changed

- Geneassay now reads and writes saved GUI configs from the project-root `config/` directory.
- Discord presence updates, connection attempts, and config-save validation were moved off the GUI thread to avoid apparent hangs during RPC or remote asset failures.
- Presence updates now retry image failures once with the default panic image fallback.
- `dynamic_update.sh` now accepts a broader set of control-file switches, including app ID, party size, image fields, button fields, and daemon timestamp fields.
- Full config swaps through `run-geneassay-daemon.sh` now trigger daemon reconnects, while ordinary `dynamic_update.sh` edits do not.
- The daemon now exits automatically if the Discord-compatible IPC socket disappears after it has connected.

## [1.0.0] - 2024-06-08

### Added

- Initial release of Geneassay 🎉, a lightweight Discord custom Rich Presence manager.

- Core functionalities:
  - Connect to Discord RPC using a client ID.
  - Update presence with customizable details.

### Release

- Linux Build
