# `.stride.json` settings

`.stride.json` stores the settings Stride uses for one repository. It lives in the repository root, but stays out of git because some settings control whether Stride may continue without asking you.

Stride creates or updates this file during Linear setup. A typical file looks like this:

```json
{
  "project": "Stride >>>",
  "api_key_env": "LINEAR_WEBVENTURER_API_KEY",
  "focus": "outcome",
  "unattended": false,
  "parallel-sessions": 3
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

Passing local checks, build and tests satisfy the merge validation gate in both modes. CI runs in the background; Stride does not wait for it before merging. Repository-enforced branch protection and required reviews still apply. No additional setting is needed.

Unattended mode does not mean “ignore errors.” Stride still stops for:

- failed builds, tests or required checks
- merge conflicts, unexpected changes or unsafe repository state
- missing issues, branches, pull requests or configuration
- choices that are unclear, destructive or need your judgement
- branch protection, required external review or security controls

### `parallel-sessions`

The most cards Stride runs at once.

```json
"parallel-sessions": 3
```

Use a whole number of 1 or more; `1` means one card at a time. A missing field is treated as `3`, and `/linear:setup` writes it. Any other value, such as `0`, `"three"` or `2.5`, is refused with a message naming the field.

### `screenshot-tool`

The tool this repository expects for screenshots and other visual checks. Optional.

```json
"screenshot-tool": "agentshot"
```

When it is set, `/parallel-sessions` puts the tool's name in every job's brief and tells the job to take its screenshots with it, run it under a time limit, and message the coordinator before using any other tool for a visual check. A missing field means the repository names no tool: briefs carry no screenshots rule and a job may use any tool. `/linear:setup` doesn't write this field. An empty value, or one that isn't text, is refused with a message naming the field.

## Keep the file out of git

Add `.stride.json` to `.gitignore`:

```text
.stride.json
```

The `unattended` setting gives Stride permission to continue through routine merge steps. That permission must come from your machine, not from files committed by the repository. If Stride finds a tracked `.stride.json` with `unattended` set to `true`, it stops and asks you to remove the file from version control.

## Change a setting

Edit `.stride.json` in the repository root. Use JSON strings for `project`, `api_key_env` and `focus`; use the JSON booleans `true` or `false` for `unattended` without quotation marks, a whole number for `parallel-sessions` and a JSON string for `screenshot-tool`.

Run `/linear:check` after changing Linear settings to confirm that the API key, project and board still match the workflow Stride expects.
