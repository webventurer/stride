# Recover: team-scoped → workspace-scoped type labels

> **What this is**: the recovery runbook for an older install whose type labels (`Epic`, `Issue`/`Story`, `Bug`) were created at **team scope** before stride moved them to **workspace scope**. Symptom: `provision-labels` fails with `duplicate label name`, because Linear won't let a workspace label coexist with a same-named team label.
>
> **Why it can't just update**: `IssueLabelUpdateInput` has no `teamId` field — a label's team scope is pinned at creation. Promoting team→workspace is always delete-and-recreate, never an update. (The label's `name` *is* updatable, though — that's what the populated path below exploits.)

The CLI doesn't expose delete / rename / team-scoped-list, so the steps below drop to the Linear API directly. Run each GraphQL operation through `linear.py`'s helper, authenticated with the affected workspace's key:

```bash
LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run python -c '
import sys; sys.path.insert(0, ".claude/tools")
from linear import graphql_data
print(graphql_data("""<QUERY OR MUTATION>""", {}))'
```

<mark>**Always run the tagged-issue check (step 2) before deleting anything.** Deleting a label untags every issue that uses it. The fast path is only safe when the count is zero.</mark>

## 1. Find the team-scoped duplicates

`list_labels` returns every label including team-scoped ones (the `label list` CLI command filters to workspace-only, so it can't see these):

```bash
LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run python -c '
import sys; sys.path.insert(0, ".claude/tools")
from linear import list_labels, bearer_token
team = [l for l in list_labels(bearer_token()) if l.get("team")]
for l in team: print(l["id"], "|", l["name"], "|", l["color"])'
```

Each row is a team-scoped label blocking its workspace twin. Note the legacy rename: stride's old **`Issue`** label is today's **`Story`** (shared colour `#4cb782`) — treat a team-scoped `Issue` as the `Story` you're migrating to.

## 2. Check the tagged-issue count (the safety gate)

For each label id from step 1, count the issues tagged with it:

```graphql
query { issues(filter: { labels: { some: { id: { eq: "<LABEL-ID>" } } } }, first: 50) { nodes { id identifier } } }
```

- **Empty `nodes`** → 0 tagged. Take the **fast path** (step 3).
- **Any nodes** → the label is in use. Take the **rename-aside path** (step 4) so no issue loses its label.

## 3. Fast path — 0 tagged issues

Delete each 0-tagged team-scoped label, then let `provision-labels` recreate it at workspace scope:

```graphql
mutation { issueLabelDelete(id: "<LABEL-ID>") { success } }
```

```bash
LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run .claude/tools/linear_cli.py provision-labels
```

Skip to step 5 to verify.

## 4. Rename-aside path — label has tagged issues

Deleting now would untag real work, so move the issues first. The trick: `name` is updatable even though `teamId` isn't, so the old label can step aside while its workspace replacement is built. For each in-use label:

1. **Rename the team label aside** so the workspace name frees up:

   ```graphql
   mutation { issueLabelUpdate(id: "<TEAM-LABEL-ID>", input: { name: "Epic (migrating)" }) { success } }
   ```

2. **Create the workspace label** (or run `provision-labels` once after renaming all of them aside):

   ```bash
   LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run .claude/tools/linear_cli.py provision-labels
   ```

3. **Retag every issue** from step 2's list — add the new workspace label, remove the renamed one:

   ```graphql
   mutation { issueAddLabel(id: "<ISSUE-ID>", labelId: "<WORKSPACE-LABEL-ID>") { success } }
   mutation { issueRemoveLabel(id: "<ISSUE-ID>", labelId: "<TEAM-LABEL-ID>") { success } }
   ```

4. **Delete the now-orphaned team label** (it has 0 tagged issues again):

   ```graphql
   mutation { issueLabelDelete(id: "<TEAM-LABEL-ID>") { success } }
   ```

The window where an issue carries neither label never opens — it gains the workspace label before losing the team one.

## 5. Verify

`label-drift` returns `[]` when the workspace carries every declared type label, and step 1 should now list no team-scoped type labels:

```bash
LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run .claude/tools/linear_cli.py label-drift
```

A `[]` means the workspace holds workspace-scoped `Bug`/`Epic`/`Story` and the migration is done.
