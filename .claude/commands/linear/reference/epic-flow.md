# Epic-sized path

> The recipe `/linear:plan-work` follows once size-sensing (its step 5) has decided the work is epic-sized. The decision — story by default, epic when triggers fire — stays in `plan-work.md`; this file holds the execution mechanics so the decision step stays scannable. Step numbers below refer to `/linear:plan-work`'s steps.

---

**Epic-sized path** (`--epic` / "break into epic") — follow the parent-issue path:

1. Search for existing parent-issue epics in the project (`uv run .claude/tools/linear_cli.py search-by-project --project "<project>" --text "Epic: "`) and show any matches.
2. Ask: "Create a new epic, or link these stories to an existing one?"
3. If creating: run duplicate check (step 3), CRAFT if requested (step 4), then steps 7 onwards (research, test consideration, draft, approval, create) for the **parent issue** — skip step 5 on the recursion since size has already been decided. Use [EPIC-TEMPLATE.md](EPIC-TEMPLATE.md) instead of ISSUE-TEMPLATE.md and prefix the title with `Epic: `. Create the parent issue first via `uv run .claude/tools/linear_cli.py issue create -t <TEAM> --title "Epic: ..." --project "<project>" --state Backlog` and capture the returned identifier (e.g. `PG-NNN`).
4. Confirm the parent issue with the user before drafting sub-issues.
5. Ask: "What are the first 1–3 stories for this epic?" — each answer becomes a separate issue draft.
6. For each story: run duplicate check (step 3), CRAFT if requested (step 4), then steps 7 onwards. Create via `uv run .claude/tools/linear_cli.py issue create --project "<project>" --state Backlog ...` and then immediately set the parent via `uv run .claude/tools/linear_cli.py issue update <new-id> --parent <epic-id>`. `linear_cli.py issue create` doesn't take a `--parent` flag — the two-step pattern is canonical. Story drafts use ISSUE-TEMPLATE.md as normal — they're stories that happen to have a parent.
7. **Position the epic at the top of the project's Backlog, order the sub-issues beneath it in drafting order, then summarise.**

   `linear_cli.py issue update` doesn't take a `--sort-order` flag, so positions are set via `linear_cli.py` (`min-backlog-sort-order` to read, `set-sort-order` to write). Lower `sortOrder` = higher on the board; leave a gap of ~100 below the epic so future epics have room. The drafting-order rule respects the sequence the user chose by deciding which sub-issue to file first.

   Recipe: fetch the project's current minimum Backlog `sortOrder`, then call `issueUpdate` on the epic with `min − 100` and on each sub-issue with `epic + 1`, `+ 2`, … in drafting order:

   ```bash
   uv run .claude/tools/linear_cli.py min-backlog-sort-order <project-UUID>
   uv run .claude/tools/linear_cli.py set-sort-order <issue-UUID> --sort-order <N>
   ```

   If the API key isn't available, skip the ordering and append to the summary: *"Sub-issues created but couldn't be auto-ordered — set `LINEAR_<WORKSPACE>_API_KEY` to enable, or drag them into sequence on the board."*

   On success, the summary names the parent epic and the sub-issues in their new board order.

<mark>**Do not bundle all stories into one issue.** Each story is its own sub-issue with `parentId` set.</mark>

**Legacy milestone path**: if the user explicitly wants a date-bound milestone instead of a parent-issue epic (e.g. "ship by Q2", "before launch"), create it via `uv run .claude/tools/linear_cli.py create-milestone --project "<project-UUID>" --name "..." --target-date "..."` and link stories with `uv run .claude/tools/linear_cli.py issue create ... --project-milestone "<name>"`. This stays available for date/scope-bound tracking but is no longer the default — parent-issue epics carry the narrative; milestones are time markers.
