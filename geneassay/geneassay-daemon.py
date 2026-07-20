#!/usr/bin/env python3
# @1.0.0
# @name: Geneassay Daemon

import atexit
import json
import os
import signal
import subprocess
import sys
import time
import venv
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


def _in_virtualenv():
    return (
        sys.prefix != getattr(sys, "base_prefix", sys.prefix)
        or hasattr(sys, "real_prefix")
        or os.environ.get("VIRTUAL_ENV") is not None
    )


def _venv_python_path(venv_dir):
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _ensure_runtime_environment():
    project_root = Path(__file__).resolve().parent.parent
    requirements_path = project_root / "requirements.txt"
    venv_dir = project_root / ".venv"

    if not _in_virtualenv():
        if not venv_dir.exists():
            venv.create(venv_dir, with_pip=True)
        venv_python = _venv_python_path(venv_dir)
        os.execv(
            str(venv_python),
            [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]],
        )

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)],
        cwd=project_root,
    )


_ensure_runtime_environment()

from pypresence import Presence


PROJECT_ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = PROJECT_ROOT / "config" / "commands"
CONTROL_FILE = COMMANDS_DIR / "current.json"
PID_FILE = COMMANDS_DIR / "geneassay-daemon.pid"
PANIC_IMAGE_URL = "https://raw.githubusercontent.com/uriel1998/geneassay/master/panic.png"
POLL_INTERVAL_SECONDS = 1.0


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def format_error(error):
    if error is None:
        return "Unknown error."

    message = getattr(error, "message", None)
    if message:
        return message

    return str(error)


class DiscordRPC:
    def __init__(self):
        self.rpc = None

    def connect(self, app_id):
        try:
            self.rpc = Presence(app_id)
            self.rpc.connect()
            self.rpc.update(
                state="Launching Geneassay Daemon",
                details="Applying watched configuration.",
                start=int(time.time()),
            )
            return True, None
        except Exception as error:
            return False, error

    def disconnect(self):
        if not self.rpc:
            return

        try:
            self.rpc.close()
        except Exception:
            pass
        finally:
            self.rpc = None

    def update_presence(self, **kwargs):
        if not self.rpc:
            return False, "Discord RPC is not connected."

        payload = {key: value for key, value in kwargs.items() if value}

        try:
            print(f"Updating Discord presence: {payload}", flush=True)
            self.rpc.update(**payload)
            return True, None
        except Exception as error:
            return False, error


class GeneassayDaemon:
    def __init__(self):
        self.rpc = DiscordRPC()
        self.running = True
        self.connected_app_id = None
        self.start_time = int(time.time())
        self.last_applied_signature = None

    def run(self):
        COMMANDS_DIR.mkdir(parents=True, exist_ok=True)
        self._claim_pid_file()
        self._register_signal_handlers()

        if not CONTROL_FILE.exists():
            print(f"Control file missing at startup: {CONTROL_FILE}", flush=True)
            return 1

        print(f"Watching control file: {CONTROL_FILE}", flush=True)

        while self.running:
            if not CONTROL_FILE.exists():
                print("Control file deleted. Exiting daemon.", flush=True)
                return 0

            signature = self._control_file_signature()
            if signature != self.last_applied_signature:
                self.last_applied_signature = signature
                try:
                    config = self._load_control_config()
                    self._apply_config(config)
                    print("Control file applied successfully.", flush=True)
                except Exception as error:
                    print(f"Failed to apply control file: {format_error(error)}", flush=True)

            time.sleep(POLL_INTERVAL_SECONDS)

        return 0

    def _claim_pid_file(self):
        if PID_FILE.exists():
            try:
                existing_pid = int(PID_FILE.read_text().strip())
            except ValueError:
                existing_pid = None

            if existing_pid and self._pid_is_running(existing_pid):
                raise RuntimeError(
                    f"Geneassay daemon is already running with PID {existing_pid}."
                )

            PID_FILE.unlink(missing_ok=True)

        PID_FILE.write_text(f"{os.getpid()}\n")
        atexit.register(self._cleanup_pid_file)

    def _cleanup_pid_file(self):
        try:
            if PID_FILE.exists():
                pid_text = PID_FILE.read_text().strip()
                if pid_text == str(os.getpid()):
                    PID_FILE.unlink()
        except OSError:
            pass

    def _register_signal_handlers(self):
        def handle_signal(signum, _frame):
            print(f"Received signal {signum}. Exiting daemon.", flush=True)
            self.running = False

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

    def _control_file_signature(self):
        stat = CONTROL_FILE.stat()
        return (stat.st_mtime_ns, stat.st_size)

    def _load_control_config(self):
        with CONTROL_FILE.open("r") as handle:
            return json.load(handle)

    def _apply_config(self, config):
        app_id = str(config.get("app_id", "")).strip()
        if not app_id:
            raise ValueError("Control config must include a non-empty app_id.")

        if self.connected_app_id != app_id:
            self.rpc.disconnect()
            success, error = self.rpc.connect(app_id)
            if not success:
                raise RuntimeError(f"Connection failed. {format_error(error)}")
            self.connected_app_id = app_id

        update_kwargs = self._build_update_kwargs(config)
        if not update_kwargs:
            print("No presence fields found in control config.", flush=True)
            return

        success, error = self.rpc.update_presence(**update_kwargs)
        if not success and self._has_presence_images(update_kwargs):
            fallback_kwargs = self._with_fallback_images(update_kwargs)
            success, error = self.rpc.update_presence(**fallback_kwargs)
            if success:
                print("Applied fallback panic image after remote asset failure.", flush=True)

        if not success:
            raise RuntimeError(f"Presence update failed. {format_error(error)}")

    def _build_update_kwargs(self, config):
        details = str(config.get("details", "")).strip()
        state = str(config.get("party_state", "")).strip()
        large_image = str(config.get("large_image_url", "")).strip()
        large_text = str(config.get("large_image_text", "")).strip()
        small_image = str(config.get("small_image_url", "")).strip()
        small_text = str(config.get("small_image_text", "")).strip()
        party_min = str(config.get("party_min", "")).strip()
        party_max = str(config.get("party_max", "")).strip()
        button_one_url = str(config.get("button_one_url", "")).strip()
        button_one_text = str(config.get("button_one_text", "")).strip()
        button_two_url = str(config.get("button_two_url", "")).strip()
        button_two_text = str(config.get("button_two_text", "")).strip()
        custom_timestamp = str(config.get("custom_timestamp", "")).strip()
        timestamp_mode = str(config.get("timestamp_mode", "")).strip().lower()

        if details and len(details) == 1:
            raise ValueError("Details needs 2 or more characters.")
        if state and len(state) == 1:
            raise ValueError("Party State needs 2 or more characters.")
        if large_text and len(large_text) == 1:
            raise ValueError("Large Image Text needs 2 or more characters.")
        if small_text and len(small_text) == 1:
            raise ValueError("Small Image Text needs 2 or more characters.")

        if large_image and not large_text:
            raise ValueError("Large Image URL requires Large Image Text.")
        if small_image and not small_text:
            raise ValueError("Small Image URL requires Small Image Text.")

        for field_name, url in {
            "Large Image Url": large_image,
            "Small Image Url": small_image,
            "Button One Url": button_one_url,
            "Button Two Url": button_two_url,
        }.items():
            if url and not is_valid_url(url):
                raise ValueError(f"Invalid {field_name}.")

        buttons = []
        if button_one_url:
            if not button_one_text:
                raise ValueError("Button 1 needs a label.")
            buttons.append({"label": button_one_text, "url": button_one_url})
        if button_two_url:
            if not button_two_text:
                raise ValueError("Button 2 needs a label.")
            buttons.append({"label": button_two_text, "url": button_two_url})

        update_kwargs = {}
        if details:
            update_kwargs["details"] = details
        if state:
            update_kwargs["state"] = state
        if large_image:
            update_kwargs["large_image"] = large_image
            update_kwargs["large_text"] = large_text
        if small_image:
            update_kwargs["small_image"] = small_image
            update_kwargs["small_text"] = small_text
        if buttons:
            update_kwargs["buttons"] = buttons
        if party_min or party_max:
            if not state:
                raise ValueError("Party number needs a state.")
            if not party_min or not party_max:
                raise ValueError("Party size requires both Min and Max.")
            party_values = [int(party_min), int(party_max)]
            if party_values[0] > party_values[1]:
                raise ValueError("Min must not exceed Max.")
            update_kwargs["party_size"] = party_values

        start_time = self._resolve_start_time(timestamp_mode, custom_timestamp)
        if start_time is not None:
            update_kwargs["start"] = start_time

        return update_kwargs

    def _resolve_start_time(self, timestamp_mode, custom_timestamp):
        if not timestamp_mode or timestamp_mode == "start time":
            return self.start_time
        if timestamp_mode == "none":
            return None
        if timestamp_mode == "local time":
            return int(time.time())
        if timestamp_mode == "custom timestamp":
            if not custom_timestamp:
                raise ValueError("Custom timestamp mode requires custom_timestamp.")
            dt = datetime.strptime(custom_timestamp, "%B %d, %Y %I:%M:%S %p")
            return int(time.mktime(dt.timetuple()))
        return self.start_time

    def _has_presence_images(self, update_kwargs):
        return bool(
            update_kwargs.get("large_image") or update_kwargs.get("small_image")
        )

    def _with_fallback_images(self, update_kwargs):
        fallback_kwargs = dict(update_kwargs)
        if fallback_kwargs.get("large_image"):
            fallback_kwargs["large_image"] = PANIC_IMAGE_URL
        if fallback_kwargs.get("small_image"):
            fallback_kwargs["small_image"] = PANIC_IMAGE_URL
        return fallback_kwargs

    def _pid_is_running(self, pid):
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True


def main():
    try:
        daemon = GeneassayDaemon()
        return daemon.run()
    except Exception as error:
        print(format_error(error), flush=True)
        return 1
    finally:
        daemon = locals().get("daemon")
        if daemon is not None:
            daemon.rpc.disconnect()


if __name__ == "__main__":
    sys.exit(main())
