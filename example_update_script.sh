#!/usr/bin/env bash
set -euo pipefail

# This is an example of how you can do dynamic updates.  This pulls a 
# data value from a cached file, parses it, 
# prepends an icon, and then updates the second line ONLY of 
# your current rich presence (if RPC is being handled by geneassay)

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_dir}" && pwd)"
dynamic_update_script="${project_root}/geneassay/dynamic_update.sh"

if [ ! -f "${project_root}/config/commands/geneassay-daemon.pid" ];then
	printf 'This requires the daemon to be running first, sorry.' >&2
	exit 1
fi


PressureScore=$(head -n 1 /home/steven/.cache/tanuki_weather/weather_cache/Phonepressure_pressure_score.txt)
PressureLevel=$(awk -v score="$PressureScore" 'BEGIN {
        if      (score < 0.50) level = 1
        else if (score < 1.00) level = 2
        else if (score < 1.50) level = 3
        else if (score < 2.00) level = 4
        else if (score < 2.50) level = 5
        else if (score < 3.00) level = 6
        else                   level = 7

        print level
    }'
)

case "$PressureLevel" in 
	1) icon="🟪";;
	2) icon="🟦";;
	3) icon="🟩";;
	4) icon="🟨";;
	5) icon="🟧";;
	6) icon="🟥";;
	7) icon="◻️";;
	*) icon="🟫";;
esac

out_text=$(printf "pressure: %s %s" "$icon" "$PressureScore")



"${dynamic_update_script}" --line2="${out_text}"
