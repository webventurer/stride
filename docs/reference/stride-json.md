# `.stride.json` settings

`.stride.json` stores the settings Stride uses for one repository. It lives in the repository root, but stays out of git because some settings control whether Stride may continue without asking you.

Stride creates or updates this file during Linear setup. A typical file looks like this:

```json
{
  "project": "Stride >>>",
  "api_key_env": "LINEAR_WEBVENTURER_API_KEY",
  "focus": "outcome",
  "unattended": false
}
```

## Settings

### `project`

The exact name of the Linear project linked to this repository.

```json
"project": "Stride >>>"
```

Stride uses this name when it lists work, creates cards and syncs `VISION.md` to Linear.

### `api_key_env`

The name of the environment variable that holds your Linear API key.

```json
"api_key_env": "LINEAR_WEBVENTURER_API_KEY"
```

The API key itself belongs in `~/.env`, not in `.stride.json`. Keeping only the variable name here lets each repository select the right Linear workspace without storing a secret in the project.

### `focus`

Controls how much technical detail Stride includes in command summaries.

| Value | What Stride shows |
|:------|:------------------|
| `"outcome"` | What changed for the user or project and why it matters. Technical detail appears only when you need it to make a decision or understand a risk. |
| `"technical"` | The outcome plus implementation details, decisions and cleanup information. |

The default is `"outcome"`. A missing `focus` field is treated as `"outcome"`.

### `unattended`

Controls whether Stride pauses for routine review and approval prompts.

| Value | Behaviour |
|:------|:----------|
| `false` | Interactive mode. Stride keeps its normal review, approval and housekeeping prompts. |
| `true` | Unattended mode. After checks pass, Stride follows the command's documented next step without waiting for routine approval. |

The default is `false`. A missing `unattended` field is treated as `false`.

In unattended mode, Stride can:

- continue through passing delivery steps without waiting for a ship phrase
- merge after the command's build, test, repository and Vision checks pass
- complete routine cleanup and Linear updates without asking
- warn about a missing Vision outcome, add the closest durable Success criterion, commit it separately, check the fit again and continue

Unattended mode does not mean “ignore errors.” Stride still stops for:

- failed builds, tests or required checks
- merge conflicts, unexpected changes or unsafe repository state
- missing issues, branches, pull requests or configuration
- choices that are unclear, destructive or need your judgement
- branch protection, required external review or security controls

## Keep the file out of git

Add `.stride.json` to `.gitignore`:

```text
.stride.json
```

The `unattended` setting gives Stride permission to continue through routine merge steps. That permission must come from your machine, not from files committed by the repository. If Stride finds a tracked `.stride.json` with `unattended` set to `true`, it stops and asks you to remove the file from version control.

## Change a setting

Edit `.stride.json` in the repository root. Use JSON strings for `project`, `api_key_env` and `focus`; use the JSON booleans `true` or `false` for `unattended` without quotation marks.

Run `/linear:check` after changing Linear settings to confirm that the API key, project and board still match the workflow Stride expects.
