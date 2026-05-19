import yaml
import os
from datetime import datetime
import re


class IndentDumper(yaml.SafeDumper):
  def increase_indent(self, flow=False, indentless=False):
    return super().increase_indent(flow, False)

# datetime -> ISO string without quotes
def datetime_representer(dumper, data):
  value = data.strftime('%Y-%m-%dT%H:%M:%SZ')
  return dumper.represent_scalar(
    'tag:yaml.org,2002:str',
    value,
    style=''
  )

# None -> empty value
def none_representer(dumper, data):
  return dumper.represent_scalar(
    'tag:yaml.org,2002:null',
    ''
  )

# strings -> never quote unless necessary
def str_representer(dumper, data):
  return dumper.represent_scalar(
    'tag:yaml.org,2002:str',
    data,
    style=''
  )

IndentDumper.add_representer(datetime, datetime_representer)
IndentDumper.add_representer(type(None), none_representer)
IndentDumper.add_representer(str, str_representer)


def generate_summary(session, project):
  goals = []
  accomplished_goals = []
  unfinished_goals = []
  unsolved_problems = []
  found = 0
  for entry in session.get('entries', []):
    if entry.get("project", None) != project:
      continue
    found += 1
    goal = entry.get('goal', None) or None
    if entry.get('summary_generated', False) == True:
      print(f"Skipping. Summary was already generated for goal: {goal}")
      continue
    context = entry.get('context', "") or ""
    if entry.get('state', 'in_progress') == 'done':
      entry['summary_generated'] = True
    if context != "":
      context = f" ({context.strip()})"
    if goal:
      new_goal = goal + context
      if new_goal not in goals:
        goals.append(new_goal)
      if entry.get('state', None) == 'done' and goal not in accomplished_goals:
        accomplished_goals.append(goal)
      elif goal not in unfinished_goals:
        unfinished_goals.append(goal)
      if entry.get('state', 'in_progress') == 'in_progress':
        unsolved_problems = entry.get('problems', []) or []
  if found == 0:
    print(f"No entries for project {project} in today's session.")
    exit(1)
  print("# Nad czym pracowałem")
  if goals:
    print('\n'.join([f'- {goal}' for goal in goals]))
  else:
    print("Brak celów.")
  print("")
  if accomplished_goals:
    print("# Co udało mi się zrobić")
    print('\n'.join([f'- {goal}' for goal in accomplished_goals]))
    print("")
  if unfinished_goals:
    print("# Co trzeba dokończyć")
    print('\n'.join([f'- {goal}' for goal in unfinished_goals]))
    print("")
  if unsolved_problems:
    print("# Co mnie blokuje")
    print('\n'.join([f'- {problem.replace("\n", " ")}' for problem in unsolved_problems]))


if __name__ == "__main__":
  project = os.getenv("PROJECT", None)
  if project is None:
    print("Please, set the PROJECT environment variable first!")
    exit(1)
  if not os.path.exists("sessions"):
    print("Sessions directory does not exist.")
    exit(1)
  current_date = datetime.now().strftime("%Y-%m-%d")
  summary_file = f"sessions/{current_date}.yaml"
  if not os.path.exists(summary_file):
    print(f"Today's session file {summary_file} doesn't exist.")
    exit(1)
  with open(summary_file, "r") as f:
    session = yaml.safe_load(f)
  generate_summary(session, project)
  with open(summary_file, "w", encoding='utf-8') as f:
    yaml.dump(
      session,
      f,
      Dumper=IndentDumper,
      sort_keys=False,
      default_flow_style=False,
      allow_unicode=True
    )
  # remove quotes around ISO timestamps
  with open(summary_file, "r+", encoding="utf-8") as f:
    content = f.read()
    content = re.sub(
      r"'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)'",
      r"\1",
      content
    )
    f.seek(0)
    f.write(content)
    f.truncate()
