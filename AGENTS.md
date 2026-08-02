# Rules

- **Do not modify files or execute modifications immediately on a user request.** When a request is made, first explain your proposed approach, describe the changes you can make (or provide examples/alternatives), and wait for the user's explicit command/approval to proceed before modifying any files or running commands.
- **Git Commits On Demand:** Do NOT automatically execute git commits after code changes. Execute `git add` and `git commit` ONLY when the user explicitly requests to commit (e.g. "закоміть", "комміть"). When requested, execute the commit immediately with a relevant Ukrainian commit message.
- **Mandatory Changelog & Version Sync (1 Commit = 1 Version):** During an active working session, accumulate code changes without bumping the version badge on every micro-edit. Consolidate all session changes into `CHANGELOG.md` and bump the UI version badge ONCE right before executing the user's explicit commit command ("закоміть").
- **Store all Python scripts in subfolder.** All new Python scripts, helper scripts, and patch tools must be created inside the `python_scripts/` subfolder to keep the root directory clean.

