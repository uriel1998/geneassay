
# <img src=https://raw.githubusercontent.com/uriel1998/geneassay/master/panic.png style="height:1em;"/> Geneassay : Discord Rich Presence

A lightweight Discord custom Rich Presence manager that runs on Linux.  Has both a GUI built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) and [pypresence](https://github.com/qwertyquerty/pypresence), heavily inspired by [maximax42](https://github.com/maximmax42)'s amazing [Discord-CustomRP](https://github.com/maximmax42/Discord-CustomRP).
Also has a daemon mode that allows for dynamic and scripted updating.

This project is a fork of the original upstream repository at [github.com/dinogomez/genzai](https://github.com/dinogomez/genzai).  Because it's so different, and because I kept misreading the original name, I renamed it.

Geneassay can load and save settings in the `config/` directory at the project root.

## Table Of Contents

- [Run Geneassay From Source As A GUI](#run-geneassay-from-source-as-a-gui)
- [Config File Reference](#config-file-reference)
- [Run Geneassay As A Daemon](#run-geneassay-as-a-daemon)
- [License](#license)

<p align="left"><img src="https://raw.githubusercontent.com/uriel1998/geneassay/master/panic.png"></p>

 
## Run Geneassay From Source As A GUI

Clone the repository and cd into it.

```bash
$ git clone git@github.com:uriel1998/geneassay.git
$ cd geneassay
```

Make a new Discord application, here in the [Discord Developer Portal](https://discord.com/developers/applications).

Click New Application on the top right.

Create your application name, this will be your title in your Discord Presence.

Run the app directly with Python.  On first launch, the script will:

1. Check whether it is already running inside a virtual environment.
2. Create `.venv` if needed.
3. Re-launch itself with the virtual environment's Python interpreter.
4. Install everything from `requirements.txt`.

```bash
python3 geneassay/geneassay.py
```

Copy the Application ID from Discord and paste it in the App ID field in Geneassay.

Click Connect

Fill out the fields you want.

Click Update

Enjoy your new Discord Rich Presence!

Geneassay reads saved configurations from `<project root>/config` and saves new configuration JSON files there.

## Config File Reference

Saved configs and daemon control files are JSON objects. The example file is:

```text
config/config.json.example
```

Common keys:

- `app_id`: Discord application ID. Required for both the GUI and daemon.
- `details`: Main Rich Presence text line.
- `party_state`: Secondary Rich Presence text line.
- `party_min`: Current party size. Must be used together with `party_max` and `party_state`.
- `party_max`: Maximum party size. Must be used together with `party_min` and `party_state`.
- `large_image_url`: URL for the large image asset.
- `large_image_text`: Hover text for the large image. Required if `large_image_url` is set.
- `small_image_url`: URL for the small image asset.
- `small_image_text`: Hover text for the small image. Required if `small_image_url` is set.
- `button_one_url`: URL for the first button.
- `button_one_text`: Label for the first button. Required if `button_one_url` is set.
- `button_two_url`: URL for the second button.
- `button_two_text`: Label for the second button. Required if `button_two_url` is set.

Daemon-supported timestamp keys:

- `timestamp_mode`: One of `start time`, `none`, `local time`, or `custom timestamp`.
- `custom_timestamp`: Required when `timestamp_mode` is `custom timestamp`. Format: `Month DD, YYYY HH:MM:SS AM/PM`.

Notes:

- The GUI currently saves the common keys above. It does not currently write `timestamp_mode` or `custom_timestamp` into saved JSON.
- The daemon can consume both the common keys and the timestamp keys.
- Image and button URLs must be valid URLs.
- If a remote image update fails, the daemon retries once with the default panic image fallback.


## Run Geneassay As A Daemon

**NOTE: You will need to have pre-configured configurations for this to work. Save them with the GUI or edit them by hand.**


The daemon entrypoint is:

```bash
python3 geneassay/geneassay-daemon.py
```

It watches `<project root>/config/commands/current.json`, applies that config when it changes, and exits if that control file is deleted. If you start the daemon directly, `config/commands/current.json` must already exist.  

Daemon-related shell helpers require:

- `fzf` for `run-geneassay-daemon.sh`
- `jq` for `geneassay/dynamic_update.sh`
- `yad` for `geneassay/dynamic_update.sh` when you omit both `--line1` and `--line2`

The included helper script lets you choose a saved config with `fzf`, stage it into the control path, and start the daemon if it is not already running:

```bash
./run-geneassay-daemon.sh
```

The helper script:

1. Lets you pick one of the `config/config_*.json` files with `fzf`, or choose `exit`.
2. Copies the selected config into `config/commands/current.json`.
3. Starts `geneassay-daemon.py` only if it is not already running.
4. Leaves an already-running daemon alone, so it can notice the updated control file on its own.

Choosing `exit` deletes `config/commands/current.json`, which makes the daemon stop itself.

To update the active daemon control file in place without switching configs, use:

```bash
geneassay/dynamic_update.sh [--line1=TEXT] [--line2=TEXT]
```

`dynamic_update.sh` updates `config/commands/current.json` with `jq`:

- `--line1=TEXT` sets `details`
- `--line2=TEXT` sets `party_state`
- passing both updates both fields in one write
- passing neither opens a `yad` form and applies whichever non-empty values you entered

`dynamic_update.sh` expects `config/commands/current.json` to already exist, typically because you started the daemon with `./run-geneassay-daemon.sh` first.

Daemon runtime artifacts live under `config/commands/`:

- `current.json`: active watched control file
- `geneassay-daemon.pid`: daemon PID file
- `geneassay-daemon.log`: daemon stdout/stderr log

Delete `config/commands/current.json` to make the daemon exit.
 

## License

This project is licensed under the [MIT License](https://github.com/uriel1998/geneassay/blob/main/LICENSE)
