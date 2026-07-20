#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
config_dir="${project_root}/config"
commands_dir="${config_dir}/commands"
control_file="${commands_dir}/current.json"
pid_file="${commands_dir}/geneassay-daemon.pid"
log_file="${commands_dir}/geneassay-daemon.log"
daemon_script="${project_root}/geneassay/geneassay-daemon.py"

if ! command -v fzf >/dev/null 2>&1; then
    printf 'fzf is required but was not found in PATH.\n' >&2
    exit 1
fi

mkdir -p "${commands_dir}"

selected_config="$(
    {
        printf 'exit\n'
        find "${config_dir}" -maxdepth 1 -type f -name 'config_*.json' ! -name 'config.json.example' | sort
    } | fzf --prompt='Geneassay config> '
)"

if [[ -z "${selected_config}" ]]; then
    printf 'No config selected.\n' >&2
    exit 1
fi

if [[ "${selected_config}" == "exit" ]]; then
    rm -f "${control_file}"
    printf 'Deleted control file and requested daemon exit.\n'
    exit 0
fi

tmp_file="$(mktemp "${commands_dir}/current.json.XXXXXX")"
cp "${selected_config}" "${tmp_file}"
mv "${tmp_file}" "${control_file}"
printf 'Updated control file from %s\n' "$(basename "${selected_config}")"

if [[ -f "${pid_file}" ]]; then
    existing_pid="$(<"${pid_file}")"
    if [[ -n "${existing_pid}" ]] && kill -0 "${existing_pid}" 2>/dev/null; then
        printf 'Geneassay daemon already running with PID %s.\n' "${existing_pid}"
        exit 0
    fi
    rm -f "${pid_file}"
fi

nohup "${daemon_script}" >"${log_file}" 2>&1 &
sleep 1

if [[ -f "${pid_file}" ]]; then
    daemon_pid="$(<"${pid_file}")"
    if [[ -n "${daemon_pid}" ]] && kill -0 "${daemon_pid}" 2>/dev/null; then
        printf 'Started Geneassay daemon with PID %s.\n' "${daemon_pid}"
        exit 0
    fi
fi

printf 'Geneassay daemon did not start successfully. Check %s\n' "${log_file}" >&2
exit 1
