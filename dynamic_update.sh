#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="${script_dir}"
control_file="${project_root}/config/commands/current.json"
pid_file="${project_root}/config/commands/geneassay-daemon.pid"

declare -a jq_args=()
declare -a jq_filters=()
update_count=0

add_update() {
    local jq_var="$1"
    local json_key="$2"
    local value="$3"

    jq_args+=(--arg "${jq_var}" "${value}")
    jq_filters+=(".${json_key} = \$${jq_var}")
    update_count=$((update_count + 1))
}

show_usage() {
    cat <<'EOF'
Usage: dynamic_update.sh [OPTIONS]

Update fields in config/commands/current.json for the running Geneassay daemon.

Options:
  --app-id=ID
  --line1=TEXT
  --details=TEXT
  --line2=TEXT
  --party-state=TEXT
  --party-min=NUMBER
  --party-max=NUMBER
  --large-image-url=URL
  --large-image-text=TEXT
  --small-image-url=URL
  --small-image-text=TEXT
  --button-one-url=URL
  --button-one-text=TEXT
  --button-two-url=URL
  --button-two-text=TEXT
  --timestamp-mode=MODE
  --custom-timestamp=TEXT
  --help

Notes:
  --line1 is an alias for --details.
  --line2 is an alias for --party-state.
  If no options are supplied, yad is used to prompt for line1 and line2.
EOF
}

if [[ ! -f "${pid_file}" ]]; then
    printf 'This requires the daemon to be running first, sorry.\n' >&2
    exit 1
fi

for arg in "$@"; do
    case "${arg}" in
        --help)
            show_usage
            exit 0
            ;;
        --app-id=*)
            add_update "app_id" "app_id" "${arg#--app-id=}"
            ;;
        --line1=*|--details=*)
            add_update "details" "details" "${arg#*=}"
            ;;
        --line2=*|--party-state=*)
            add_update "party_state" "party_state" "${arg#*=}"
            ;;
        --party-min=*)
            add_update "party_min" "party_min" "${arg#--party-min=}"
            ;;
        --party-max=*)
            add_update "party_max" "party_max" "${arg#--party-max=}"
            ;;
        --large-image-url=*)
            add_update "large_image_url" "large_image_url" "${arg#--large-image-url=}"
            ;;
        --large-image-text=*)
            add_update "large_image_text" "large_image_text" "${arg#--large-image-text=}"
            ;;
        --small-image-url=*)
            add_update "small_image_url" "small_image_url" "${arg#--small-image-url=}"
            ;;
        --small-image-text=*)
            add_update "small_image_text" "small_image_text" "${arg#--small-image-text=}"
            ;;
        --button-one-url=*)
            add_update "button_one_url" "button_one_url" "${arg#--button-one-url=}"
            ;;
        --button-one-text=*)
            add_update "button_one_text" "button_one_text" "${arg#--button-one-text=}"
            ;;
        --button-two-url=*)
            add_update "button_two_url" "button_two_url" "${arg#--button-two-url=}"
            ;;
        --button-two-text=*)
            add_update "button_two_text" "button_two_text" "${arg#--button-two-text=}"
            ;;
        --timestamp-mode=*)
            add_update "timestamp_mode" "timestamp_mode" "${arg#--timestamp-mode=}"
            ;;
        --custom-timestamp=*)
            add_update "custom_timestamp" "custom_timestamp" "${arg#--custom-timestamp=}"
            ;;
        *)
            printf 'Unknown argument: %s\n' "${arg}" >&2
            show_usage >&2
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

if (( update_count == 0 )); then
    if ! command -v yad >/dev/null 2>&1; then
        printf 'yad is required when no command line options are supplied.\n' >&2
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

    IFS='|' read -r yad_line1 yad_line2 <<< "${yad_output}"

    if [[ -n "${yad_line1}" ]]; then
        add_update "details" "details" "${yad_line1}"
    fi
    if [[ -n "${yad_line2}" ]]; then
        add_update "party_state" "party_state" "${yad_line2}"
    fi
fi

if (( update_count == 0 )); then
    printf 'No updates supplied.\n' >&2
    exit 1
fi

tmp_file="$(mktemp "${control_file}.XXXXXX")"
cleanup() {
    rm -f "${tmp_file}"
}
trap cleanup EXIT

jq_filter="${jq_filters[0]}"
for (( i = 1; i < ${#jq_filters[@]}; i++ )); do
    jq_filter+=" | ${jq_filters[$i]}"
done

jq "${jq_args[@]}" "${jq_filter}" "${control_file}" > "${tmp_file}"

mv "${tmp_file}" "${control_file}"
trap - EXIT

printf 'Updated %s\n' "${control_file}"
