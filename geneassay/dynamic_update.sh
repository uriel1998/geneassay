#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_dir}/.." && pwd)"
control_file="${project_root}/config/commands/current.json"

line1=""
line2=""

for arg in "$@"; do
    case "${arg}" in
        --line1=*)
            line1="${arg#--line1=}"
            ;;
        --line2=*)
            line2="${arg#--line2=}"
            ;;
        *)
            printf 'Unknown argument: %s\n' "${arg}" >&2
            printf 'Usage: %s [--line1=TEXT] [--line2=TEXT]\n' "$0" >&2
            exit 1
            ;;
    esac
done

if ! command -v jq >/dev/null 2>&1; then
    printf 'jq is required but was not found in PATH.\n' >&2
    exit 1
fi

if [[ ! -f "${control_file}" ]]; then
    printf 'Control file not found: %s\n' "${control_file}" >&2
    exit 1
fi

if [[ -z "${line1}" && -z "${line2}" ]]; then
    if ! command -v yad >/dev/null 2>&1; then
        printf 'yad is required when --line1 and --line2 are both omitted.\n' >&2
        exit 1
    fi

    yad_output="$(
        yad \
            --title="Geneassay Dynamic Update" \
            --form \
            --field="Line 1" \
            --field="Line 2" \
            --separator='|' \
            --button="OK":0 \
            --button="Cancel":1
    )" || exit 1

    IFS='|' read -r line1 line2 <<< "${yad_output}"
fi

if [[ -z "${line1}" && -z "${line2}" ]]; then
    printf 'No updates supplied.\n' >&2
    exit 1
fi

tmp_file="$(mktemp "${control_file}.XXXXXX")"
cleanup() {
    rm -f "${tmp_file}"
}
trap cleanup EXIT

if [[ -n "${line1}" && -n "${line2}" ]]; then
    jq \
        --arg details "${line1}" \
        --arg party_state "${line2}" \
        '.details = $details | .party_state = $party_state' \
        "${control_file}" > "${tmp_file}"
elif [[ -n "${line1}" ]]; then
    jq \
        --arg details "${line1}" \
        '.details = $details' \
        "${control_file}" > "${tmp_file}"
else
    jq \
        --arg party_state "${line2}" \
        '.party_state = $party_state' \
        "${control_file}" > "${tmp_file}"
fi

mv "${tmp_file}" "${control_file}"
trap - EXIT

printf 'Updated %s\n' "${control_file}"
