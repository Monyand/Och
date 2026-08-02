# Rules

- **Do not modify files or execute modifications immediately on a user request.** When a request is made, first explain your proposed approach, describe the changes you can make (or provide examples/alternatives), and wait for the user's explicit command/approval to proceed before modifying any files or running commands.
- **Git Commits On Demand:** Do NOT automatically execute git commits after code changes. Execute `git add` and `git commit` ONLY when the user explicitly requests to commit (e.g. "закоміть", "комміть"). When requested, execute the commit immediately with a relevant Ukrainian commit message.
- **Mandatory Changelog & Version Sync:** Whenever making any changes to an application, ALWAYS update `CHANGELOG.md` and bump the version badge in the application UI before creating the commit.
- **Store all Python scripts in subfolder.** All new Python scripts, helper scripts, and patch tools must be created inside the `python_scripts/` subfolder to keep the root directory clean.

