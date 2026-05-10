#!/bin/bash
if [ ! -d "sessions" ]; then
  echo "Directory 'sessions' does not exist."
  exit 1
fi
current_date=${CURRENT_DATE:-$(date -u +"%Y-%m-%d")}
session_file="sessions/${current_date}.yaml"
current_time=${CURRENT_TIME:-$(date -u +"%Y-%m-%dT%H:%M:%SZ")}
if [ ! -f "$session_file" ]; then
  echo "Today's session file '$session_file' does not exist."
  exit 1
fi
last_entry_start=$(yq '.entries[-1].start' "$session_file")
time_diff=$(($(date -d "$current_time" +%s) - $(date -d "$last_entry_start" +%s)))
spent_hours=$(echo "scale=0; $time_diff / 3600" | bc)
remaining_seconds=$(echo "$time_diff % 3600" | bc)
spent_minutes=$(echo "scale=0; $remaining_seconds / 60" | bc)
spent_seconds=$(echo "$remaining_seconds % 60" | bc)
# For the end time
CUR_TIME="$current_time" \
yq eval '.entries[-1].end = env(CUR_TIME)' -i "$session_file"
# For the spent duration
entry_duration="${spent_hours}h ${spent_minutes}m ${spent_seconds}s"
DUR="$entry_duration" \
yq eval '.entries[-1].spent = env(DUR)' -i "$session_file"
echo "Session entry for '$current_date' finished. Duration: $entry_duration."