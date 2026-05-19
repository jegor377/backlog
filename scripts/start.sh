#!/bin/bash
if [ ! -d "sessions" ]; then
  mkdir sessions
  echo "Directory 'sessions' created successfully."
fi
current_date=$(date -u +"%Y-%m-%d")
session_file="sessions/${current_date}.yaml"
current_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
if [ ! -f "$session_file" ]; then
  previous_file=$(ls -t -1 sessions | head -n 1)
  cat <<EOL > "$session_file"
version: '1'
date: $current_date
entries:
  - start: $current_time
    end:
    spent:
    project:
    task:
    goal:
    context:
    state: in_progress
    actions:
    problems:
    accoplishments:
next_steps:
EOL
  if [ ! -z "$previous_file" ]; then
    previous_file=sessions/$previous_file
    yq eval ".next_steps = load(\"$previous_file\").next_steps" "$session_file" -i
  fi
  echo "Session file '$session_file' created successfully."
else
  last_end_value=$(yq ".entries[-1].end" "$session_file")
  if [ "$last_end_value" == "" ]; then
    CURRENT_DATE="$current_date" \
    CURRENT_TIME="$current_time" \
    bash scripts/finish.sh
  fi

  CURRENT_TIME="$current_time" \
  yq eval '
  .entries += [{
    "start": env(CURRENT_TIME),
    "end": null,
    "spent": null,
    "project": null,
    "task": null,
    "goal": null,
    "context": null,
    "state": "in_progress",
    "actions": null,
    "problems": null,
    "accomplishments": null
  }]' -i "$session_file"
  sed -i 's/: null$/:/' "$session_file"
  echo "New entry added to session file '$session_file'."
fi