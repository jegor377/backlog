#!/bin/bash
read -p "Enter the project name: " project_name
if [ -z "$project_name" ]; then
  echo "Project name cannot be empty. Please try again."
  exit 1
fi
echo "Project name set to: $project_name"
if [ ! -f "projects.yaml" ]; then
  cat <<EOL > projects.yaml
version: '1'
projects:
  - $project_name
EOL
else
    project_exists=$(yq '.projects | any_c(. == "'$project_name'")' projects.yaml)
    if [ ! "$project_exists" == "true" ]; then
        yq eval ".projects += [\"$project_name\"]" -i projects.yaml
        echo "Project '$project_name' added to projects.yaml."
    else
        echo "Project '$project_name' already exists in projects.yaml. Skipping addition."
    fi
fi