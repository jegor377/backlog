import yaml
import os
from datetime import datetime


def get_project_entries(session, project):
  filtered_entries = filter(
    lambda entry: entry.get("project", None) == project, 
    session.get("entries", []) or []
  )
  return list(filtered_entries)


def generate_summary(entries):
  goals = []
  accomplished_goals = []
  for entry in entries:
    goal = entry.get('goal', None) or None
    context = entry.get('context', "") or ""
    if context != "":
      context = f" ({context.strip()})"
    if goal:
      goals.append(goal + context)
      if entry.get('state', None) == 'done':
        accomplished_goals.append(goal)
  goals = set(goals)
  accomplished_goals = set(accomplished_goals)
  unsolved_problems = (entries[-1].get('problems', []) or [])
  print("# Nad czym pracowałem")
  if goals:
    print('\n'.join([f'- {goal}' for goal in goals]))
  else:
    print("Brak celów.")
  print("")
  print("# Co udało mi się zrobić")
  if accomplished_goals:
    print('\n'.join([f'- {goal}' for goal in accomplished_goals]))
  else:
    print("Nic nie udało się zrobić.")
  print("")
  print("# Co mnie blokuje")
  if unsolved_problems:
    print('\n'.join([f'- {problem.replace("\n", " ")}' for problem in unsolved_problems]))
  else:
    print("Nic mnie nie blokuje.")


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
  entries_in_project = get_project_entries(session, project)
  if not entries_in_project:
    print(f"No entries for project {project} in today's session.")
    exit(1)
  generate_summary(entries_in_project)
