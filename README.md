
# <img src=https://raw.githubusercontent.com/uriel1998/geneassay/master/panic.png style="height:1em;"/> Geneassay : Discord Rich Presence

---

### ⭐ [NEW] Added option to load and save your settings to the `config/` directory at the project root.

A lightweight Discord custom Rich Presence manager that runs on Linux.  Has both a GUI built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) and [pypresence](https://github.com/qwertyquerty/pypresence), heavily inspired by [maximax42](https://github.com/maximmax42)'s amazing [Discord-CustomRP](https://github.com/maximmax42/Discord-CustomRP).
Also has a daemon mode that allows for dynamic and scripted updating.

This project is a fork of [dinogomez/genzai](https://github.com/dinogomez/genzai).

<p align="left"><img src="https://raw.githubusercontent.com/uriel1998/geneassay/master/panic.png"></p>

 
# Run Geneassay from source

Clone the repository and cd into it.

```bash
$ git clone git@github.com:uriel1998/geneassay.git
$ cd geneassay
```

Run the app directly with Python.  It will create a venv and download needed requirements automatically.

```bash
python3 geneassay/geneassay.py
```

Geneassay reads saved configurations from `<project root>/config` and saves new configuration JSON files there.

## Run Geneassay as a daemon

The daemon entrypoint is:

```bash
python3 geneassay/geneassay-daemon.py
```

It watches `<project root>/config/commands/current.json`, applies that config when it changes, and exits if that control file is deleted.

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

Daemon runtime artifacts live under `config/commands/`:

- `current.json`: active watched control file
- `geneassay-daemon.pid`: daemon PID file
- `geneassay-daemon.log`: daemon stdout/stderr log

Delete `config/commands/current.json` to make the daemon exit.

## GUI command line arguments

`geneassay.py` currently does not define or parse any application-specific command line arguments or flags.

You can run it as:

```bash
python3 geneassay/geneassay.py
```

On first launch, the script will:

1. Check whether it is already running inside a virtual environment.
2. Create `.venv` if needed.
3. Re-launch itself with the virtual environment's Python interpreter.
4. Install everything from `requirements.txt`.
5. Continue running with any command line arguments you originally passed in.

At the moment, this argument preservation only means the bootstrap step will not discard extra arguments. The application itself does not currently consume them.

Your system Python needs the standard `venv` module available for this to work.
  

## License

This project is licensed under the [MIT License](https://github.com/uriel1998/geneassay/blob/main/LICENSE)
