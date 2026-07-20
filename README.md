<p align=center>
  <a href="https://github.com/dinogomez/geneassay/releases/latest"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/tag/dinogomez/geneassay?color=343638&label=latest&logo=github"></a>
  <a href="https://github.com/dinogomez/geneassay/releases/latest"><img alt="GitHub Releases" src="https://img.shields.io/github/downloads/dinogomez/geneassay/latest/total?color=343638&label=downloads&logo=github"></a>
  <a href="https://github.com/dinogomez/geneassay/releases/"><img alt="All GitHub Releases" src="https://img.shields.io/github/downloads/dinogomez/geneassay/total?color=343638&label=total%20downloads&logo=github"></a>
</p>

# <img src=https://github.com/dinogomez/geneassay/assets/41871666/0536940c-fa2d-4fda-9744-25edbc5ead14 style="height:1em;"/> Geneassay : Discord Rich Presence

---

### ⭐ [NEW] Added option to load and save your settings to the `config/` directory at the project root.

A lightweight Discord custom Rich Presence manager that runs on Linux and Windows, with macOS support coming soon. Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) and [pypresence](https://github.com/qwertyquerty/pypresence), heavily inspired by [maximax42](https://github.com/maximmax42)'s amazing [Discord-CustomRP](https://github.com/maximmax42/Discord-CustomRP).

<p align="center">
<img src="https://github.com/dinogomez/geneassay/assets/41871666/0d384431-5226-491f-baca-8a1c075b06ce">

# Download

### Latest [DOWNLOAD HERE](https://github.com/dinogomez/geneassay/releases/latest)

The latest official release of Geneassay is available for both Linux and Windows. Check the [Geneassay Latest Release](https://github.com/dinogomez/geneassay/releases/latest).

- [Download for Linux](https://github.com/dinogomez/geneassay/releases/download/1.0.1/geneassay_linux_1.0.1.zip)
- [Download for Windows](https://github.com/dinogomez/geneassay/releases/download/1.0.1/geneassay_windows_1.0.1.zip)

## How to use Geneassay?

### Linux and Windows

1. Extract the zip file.
2. Run `geneassay.exe` inside the `geneassay` folder.
3. Make a new Discord application, here in the [Discord Developer Portal](https://discord.com/developers/applications).
4. Click `New Application` on the top right.
5. Create your application name, this will be your `title` in your Discord Presence.
6. Copy the `Application ID` and paste it in the `App ID` field in Geneassay.
7. Click `Connect`
8. Fill out the fields you want.
9. Click `Save Config` if you want to persist the current settings to the `config/` directory in the project root.
10. Click `Update`
11. Enjoy your new Discord Rich Presence!

## Run Geneassay from source

Clone the repository and cd into it.

```bash
$ git clone git@github.com:dinogomez/geneassay.git
$ cd geneassay
```

Run the app directly with Python.

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

Daemon runtime artifacts live under `config/commands/`:

- `current.json`: active watched control file
- `geneassay-daemon.pid`: daemon PID file
- `geneassay-daemon.log`: daemon stdout/stderr log

Delete `config/commands/current.json` to make the daemon exit.

## Command line arguments

Geneassay currently does not define or parse any application-specific command line arguments or flags.

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

## Build Geneassay as an executable

I advice building the application with `auto-py-to-exe` or `pyinstaller` if you want a standalone executable.

With `auto-py-to-exe`.

1. Select `One Directory`
2. Select `Window Based`
3. Select `Add Folder` and add the `geneassay/assets` folder
4. Select `Add Folder` and add `customtkinter` package.

   > Use `pip show customtkinter` to find the location of the package.

5. Add the `PIL._tkinter_finder` hidden import
6. Select `Convert .py to .exe` and wait for the build to finish
7. Run the `geneassay.exe` file in the `output` folder
   <br>
   <br>

With `pyinstaller`, refer to this [documentation](https://customtkinter.tomschimansky.com/documentation/packaging) when building customtkinter apps.

```bash
pyinstaller --noconfirm --onedir --windowed --icon "<Geneassay Location>/Geneassay/assets/geneassay.ico" 
--add-data "<CustomTkinter Location>/customtkinter:customtkinter/" 
--add-data "<Geneassay Location>/Geneassay/assets:assets/" 
--hidden-import "PIL._tkinter_finder"  
"<Geneassay Location>/Geneassay/geneassay.py"
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](https://github.com/dinogomez/geneassay/blob/main/LICENSE)
