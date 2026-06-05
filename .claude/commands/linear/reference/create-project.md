# Create a Linear project

> **What this is**: the shared flow for creating a new Linear project and pinning the repo to it. Linked from [`/linear:setup`](../setup.md) (when a fresh repo has no `.linear_project`) and [`/linear:update-vision`](../update-vision.md) (when the repo isn't pinned yet). Keeping it in one place means both commands reference the same procedure instead of one reaching into the other.

When creating a new Linear project for a repo:

1. Ask for the project name (default: the repo directory name).
2. Resolve the Linear team:

   ```bash
   uv run .claude/tools/linear_cli.py team list
   ```

   - One team → use its `key` (e.g. `WB`).
   - Several → ask which to use.
   - None → stop; there's no team to create a project on.
3. Create the project, seeding the subtitle from `VISION.md`'s tagline — its opening blockquote, the `>` line under the H1 (the short `description` field; the full Vision goes into `content` next). Omit `--description` when there's no `VISION.md` or it has no opening blockquote:

   ```bash
   uv run .claude/tools/linear_cli.py project create \
     -t <TEAM-KEY> \
     --name "<project-name>" \
     --description "<tagline>"
   ```

   Capture the project `id` and URL from the JSON response. If the create fails (for example the user lacks permission to create projects on the team), surface the error and stop — don't retry silently, and don't write `.linear_project` for a project that wasn't created.
4. If `VISION.md` exists at the repo root, seed it into the project `content`:

   ```bash
   uv run .claude/tools/linear_cli.py update-project-content <project-id> --content @VISION.md
   ```

   `--content @VISION.md` reads the file directly — markdown newlines and special characters never touch the shell ([why](workflow.md#how-skills-talk-to-linear)).
5. Write `.linear_project` at the repo root — **both fields**, so `linear_cli.py` reads the bearer token from it without a per-call `LINEAR_API_KEY=` wrap:

   ```
   project = <project-name>
   api_key_env = LINEAR_<WORKSPACE>_API_KEY
   ```
6. If `.gitignore` doesn't already list `.linear_project`, append it.
