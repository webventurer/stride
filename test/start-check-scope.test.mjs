import { ok } from "node:assert";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

function read(path) {
  return readFileSync(join(strideRoot, path), "utf8");
}

function inOrder(text, markers) {
  let at = -1;
  return markers.every((marker) => {
    at = text.indexOf(marker, at + 1);
    return at !== -1;
  });
}

function section(text, from, to) {
  return text.slice(text.indexOf(from), text.indexOf(to));
}

const start = read(".claude/commands/linear/start.md");
const reviewer = read(".claude/commands/linear/reference/card-start-review.md");
const startCheck = section(
  start,
  "### 3. Check the card",
  "### 4. Load project context",
);

describe("the start check after an earlier check", () => {
  it("asks stride what is left before any reviewer is spawned", () => {
    ok(
      inOrder(startCheck, [
        "git fetch origin main",
        "issue check-scope <issue-id>",
        "**Spawn three reviewers at once.**",
        "issue record-check <issue-id>",
      ]),
    );
  });

  it("records the wording as it read before the check, or as the check reworded it", () => {
    ok(
      inOrder(startCheck, [
        "> /tmp/<identifier>/checked.json",
        "**Spawn three reviewers at once.**",
        "into `checked.json`",
        "--checked @/tmp/<identifier>/checked.json",
      ]),
    );
  });

  it("carries a skipped check to the pull request's cost line", () => {
    ok(
      startCheck.includes(
        "save those words to `/tmp/<identifier>/start-cost.txt`",
      ),
    );
    ok(
      start.includes(
        "**Check cost line**: when step 3 skipped the start check",
      ),
    );
  });

  it("reads comments on sibling cards under any parent", () => {
    ok(
      reviewer.includes(
        "the other cards under the card's parent, whatever its title",
      ),
    );
  });

  it("spawns nobody and says why when nothing changed", () => {
    ok(startCheck.includes("Spawn no reviewer, post nothing"));
    ok(
      startCheck.includes(
        "card start check: nothing changed since <since>, skipped",
      ),
    );
  });

  it("has reviewers judge only what changed when something has", () => {
    ok(startCheck.includes("Check only what changed since `<record-time>`"));
    ok(reviewer.includes("## A check of changes only"));
    ok(reviewer.includes("Raise only a finding one of those changes causes"));
  });
});
