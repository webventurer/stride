# Quick: ship a small change, then file the card

Ship a small, well-scoped change and file the Linear card *after* it merges — so a copy tweak or padding fix doesn't pay the up-front card-drafting tax. The card lands directly in **Done**, pointing at the merged PR.

Two ways in:

- **Describe it** — `/linear:quick "tighten the hero heading spacing"`: branch, implement, review, ship.
- **Already did it** — make the change first, then run `/linear:quick`: it picks up your existing diff and files the card to match what you just created.

Either way: review on the PR → **you say a ship phrase** → Vision trace → merge → file the Done card (or hold it to bundle with later changes). The PR opens at review time, so the change is viewable on GitHub before anything merges — only the merge waits for the ship phrase.

<mark>**Not a replacement for `/linear:plan-work`.**</mark> This is for changes whose shape is obvious and whose diff fits in one terminal scroll — copy/wording, design tweaks, doc polish, single-file refactors, config tweaks, dead-code removal. Anything that crosses files non-trivially, touches a shared contract or public API, needs a migration, or carries scope/risk uncertainty still earns the card-first discipline of `/linear:plan-work`.

> **Not `/loop`.** `/loop` is scheduled re-invocation of a command; `/linear:quick` is a one-shot ship-then-file flow. Same first four letters, unrelated.

## Good candidates for the fast loop

The fast-loop fits work where the shape is already obvious from the description and the diff fits comfortably in one terminal scroll. Examples:

- **Design tweaks** — typography, spacing, colour swap, padding adjustment, icon switch
- **Copy and wording** — typo fix, sentence rewrite, heading rename, button-label change
- **Documentation polish** — broken link, formatting consistency, sentence break, list normalisation
- **Single-file refactors** — extract a variable, rename a function within one file, inline a one-off helper
- **Config tweaks** — adjust a threshold, update a default, change a constant
- **Dead code removal** — orphaned imports, unused functions, dead branches the diff makes obvious
- **Comment / docstring additions** — when the *what* is obvious from the code but the *why* isn't

**When not to reach for `/linear:quick`:** the change crosses files in non-trivial ways, touches a public API or shared contract, requires migration, evolves the Vision, or carries any uncertainty about scope or risk. Those still earn the card-first discipline of `/linear:plan-work`.

## The ship gate

The merge fires **only** when you say an explicit ship phrase: **`ship`, `ship it`, `quick`, `jfdi`, `go`**. <mark>**The agent never decides on its own that the change is ready to merge.**</mark> No phrase, no merge — "looks done to me" and silent timeouts are not triggers.

## Rules

- Never work directly on `main` — existing uncommitted changes on `main` move to a branch first
- Never merge without one of the ship phrases above
- The PR opens at **review** time (step 5); only the **merge** waits for the ship phrase
- Use `--merge` (not `--squash`) to preserve atomic commits
- Keep scope to one change — if the diff grows past a one-scroll review, stop and suggest `/linear:plan-work`
- <mark>**Don't shortcut the Vision trace.** A drift is surfaced for your decision — exactly as `/linear:finish` does — *before* the merge, while the catch is still actionable.</mark>
- The card is filed once, directly in **Done** — or deferred to bundle with later changes

---

## Steps

### 1. Vision check

Read `VISION.md` from the repo root. If missing, stop and suggest `/vision` (same hard gate as the other commands). If present, load the full Success criteria — step 6 traces the change against them.

### 2. Find the change

Run `git status -sb` and `git log main..HEAD --oneline`. Two paths:

- **Retrospective** (you made the change first): the working tree has uncommitted changes, or the current branch already has commits ahead of `main`. Use them. If the changes are uncommitted **on `main`**, create `quick/<slug>` and commit them with `/commit` first (never ship from `main`). If they're already on a feature branch, stay on it.
- **Describe-then-build** (clean tree, description given): create the branch and implement in step 3.

```bash
git checkout main && git checkout -b quick/<slug>
```

Derive `<slug>` from the description, or from the diff in the retrospective path.

### 3. Implement *(describe-then-build path only — skip if the change already exists)*

Make the change iteratively with the user, with the same discipline as `/linear:start` step 7:

- [YAGNI gate](../../stride/docs/principles/design-decisions.md#the-test) — drop anything that closes doors or adds unused complexity
- **Footprint audit** — each new helper/test earns its place (used 2+ times, adds semantic value, or encapsulates non-trivial config)
- Follow the project's coding standards

If the change starts crossing files non-trivially or the diff outgrows one terminal scroll, **stop** and tell the user this is `/linear:plan-work` territory now.

### 4. Validate

Run the project's build and tests. Fix failures and re-run until clean. Never ship with a failing build.

### 5. Review — open the PR, then gate

Show the full diff and the commit log in the terminal:

```bash
git diff main...HEAD
git log main..HEAD --oneline
```

Then push the branch and open the PR **without merging**, so the change is reviewable on GitHub or pulled into an editor — not terminal-only *(auth per [reference/workflow.md](reference/workflow.md))*:

Write the PR body to a file with the editor — never an inline heredoc, since bodies often carry backticks, `$`, or `<placeholders>` that trip shell quoting ([why](reference/workflow.md#how-skills-talk-to-linear)):

```markdown
## Summary
<1–2 bullets: what changed and why>
```

Then push and open the PR with `--body-file`:

```bash
git push -u origin quick/<slug>
gh pr create --title "<imperative summary>" --body-file <body-file>
```

If a PR already exists for the branch (a resumed run), push to it instead of opening a second one.

**Then open the PR in diffity — the visual diff is the review surface.** Follow the launch procedure in [reference/diffity-review.md](reference/diffity-review.md).

Then surface the URL with the gate prompt: **"PR: \<url\> — ship it? (say `ship` / `ship it` / `quick` / `jfdi` / `go`, or tell me what to change.)"**

If the user requests changes, make them, re-validate (step 4), push to the same PR (`git push`, or `--force-with-lease` after a squash), and show the updated diff. Repeat until they say a ship phrase. <mark>**Opening the PR is reversible; the merge is not. Until a ship phrase, do nothing irreversible — above all, no merge.**</mark>

### 6. On the ship phrase — trace Vision, then merge

Only once the user says a ship phrase. **First run the Vision trace check — the same judgement `/linear:finish` makes, not a rubber stamp.** With the diff and commit subjects in hand, read them against the `VISION.md` Success criteria and pick the best-fit criterion:

- **Match** — the change clearly serves one criterion. Surface a single line and continue to the merge:

  ```
  Trace verified against "<criterion>" — shipping.
  ```

- **Drift / no clear fit** — surface it in plain English and let the user decide *before* the merge:

  ```
  This change ships: <one-line description of the diff>
  Closest Vision criterion: "<best-fit>"
  But the fit is thin because <why>.

  Ship anyway against that criterion, pick a better one, or add a
  new criterion to VISION.md first? (ship / <criterion> / add)
  ```

  - **ship / pick** → continue to the merge; the chosen criterion becomes the card's *Why this matters*.
  - **add** → pause. Tell the user: *"Add the criterion to `VISION.md`, `/commit` it on this branch (the push updates the open PR), then say a ship phrase again."* Don't merge. (The merge is still ahead, so the catch rides on the same branch and the same open PR — no follow-up PR needed.)

The merge hasn't happened yet, so a drift is fully actionable here. The PR is already open from step 5 — once the trace is settled, merge it:

```bash
gh pr merge <number> --merge --subject "Merge branch 'quick/<slug>'" --body ""
```

`--merge` keeps the atomic commits. Capture the merged PR URL.

### 7. File the card now, or hold it to bundle

Ask:

```
File the card now, or delay to bundle with more changes? (file / delay)
```

- **delay** — hold this PR's URL, summary, and confirmed Vision criterion in the session's **pending bundle**, and skip filing. Tell the user it'll fold into the next `file`. The change is already shipped; only the card is deferred. (The bundle lives in this working session — a later `/linear:quick` that files picks it up.)
- **file** — create one card in **Done** covering this change *and every PR held in the pending bundle*, then attach each PR *(auth per [reference/workflow.md](reference/workflow.md))*. Write the card description to a file first and pass it with `--description @<file>` — multi-line bodies go through a file, never an inline string ([why](reference/workflow.md#how-skills-talk-to-linear)):

  ```bash
  uv run .claude/tools/linear_cli.py issue create \
    -t <TEAM> --project "<project>" --state Done \
    --title "<imperative summary of the change(s)>" \
    --description @<card-file>
  uv run .claude/tools/linear_cli.py issue attach <new-id> --url <merged-PR-URL>
  # ...repeat issue attach for each PR in the bundle
  ```

  Resolve the project from `.stride.json` and the team key from `uv run .claude/tools/linear_cli.py team list`. The PR links make the Linear ↔ git ↔ PR trail whole even though the branch carried no issue ID. Clear the pending bundle once filed.

### 8. Clean up

```bash
git checkout main && git pull --ff-only
git branch -d quick/<slug>
git push origin --delete quick/<slug>
```

If GitHub auto-deleted the remote branch on merge, skip that silently.

### 9. Summary

Display:

- The change (one line) and the merged PR URL
- Card: filed in **Done** — `<identifier>` with the PR(s) attached — *or* `held (bundle of N pending)`
- Build: passed
- Branch: deleted
- Vision: the criterion the change serves (from step 6)

---

## Error handling

- `VISION.md` missing → stop, suggest `/vision`
- Uncommitted changes on `main` → branch + `/commit` before shipping (never ship from `main`)
- Build/tests fail → fix before shipping; never merge red
- No ship phrase given → never merge; keep iterating. The PR opened at step 5 stays open (reversible) — if the user abandons the flow, the open PR and pushed branch are theirs to close or resume; quick doesn't auto-close them
- Vision drift, user picks **add** → stop, don't merge; resume after the criterion is committed
- Change outgrew a one-scroll diff → stop, suggest `/linear:plan-work`
- `uv run .claude/tools/linear_cli.py issue create` / `attach` fails after merge → surface it; the PR is already merged, so re-running the file step (with the bundle intact) recovers the card
