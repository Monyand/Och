# Rules

- **Do not modify files or execute modifications immediately on a user request.** When a request is made, first explain your proposed approach, describe the changes you can make (or provide examples/alternatives), and wait for the user's explicit command/approval to proceed before modifying any files or running commands.
- **Immediate Git Commits:** When the user explicitly requests to commit (e.g. "закоміть", "комміть"), execute `git add` and `git commit` immediately with a relevant Ukrainian commit message without asking for additional confirmation.
- **Store all Python scripts in subfolder.** All new Python scripts, helper scripts, and patch tools must be created inside the `python_scripts/` subfolder to keep the root directory clean.

