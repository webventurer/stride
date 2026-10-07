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

describe("card check", () => {
  it("runs in /linear:start after the simplification review and before the PR", () => {
    const start = read(".claude/commands/linear/start.md");

    ok(
      inOrder(start, [
        "### 10. Simplification review",
        "### 11. Card check",
        "reference/card-check.md",
        "### 17. Create PR",
        "## Card check",
      ]),
    );
  });

  it("runs in /linear:finish after every branch-changing step and before the merge", () => {
    const finish = read(".claude/commands/linear/finish.md");

    ok(
      finish.includes(
        "Never merge a branch whose current content has no passing card check against the card's current wording",
      ),
    );
    ok(
      inOrder(finish, [
        "### 5b.",
        "### 6. Confirm Vision outcome",
        "### 7. Check the change against its card",
        "reference/card-check.md",
        "### 8. Merge",
      ]),
    );
  });

  it("gives every promise one of four verdicts from a cold reviewer", () => {
    const brief = read(
      ".claude/commands/linear/reference/card-check-review.md",
    );

    for (const verdict of [
      "`kept`",
      "`kept-unproven`",
      "`broken`",
      "`unclear`",
    ]) {
      ok(brief.includes(verdict), verdict);
    }
    ok(brief.includes("never from the author's reasoning"));
    ok(
      brief.includes("An empty file means the card makes no checkable promise"),
    );
    ok(brief.includes("Do not suggest new wording for the card"));
  });

  it("never rewrites the card without the user's sign-off", () => {
    const check = read(".claude/commands/linear/reference/card-check.md");

    ok(check.includes("Never edit the card to make a verdict pass"));
    ok(
      check.includes(
        "A card change always stops for the user, in unattended mode too",
      ),
    );
    ok(check.includes("that the user signed off"));
    ok(check.includes("reference/card-check-review.md"));
    ok(check.includes("Stop after three rounds"));
  });

  it("confirms a pass with a second reviewer told to disprove it", () => {
    const check = read(".claude/commands/linear/reference/card-check.md");
    const brief = read(
      ".claude/commands/linear/reference/card-check-review.md",
    );
    const convention = read(
      "docs/conventions/check-the-card-at-the-start-and-the-end.md",
    );

    ok(
      check.includes(
        "Another reviewer found every promise on this card kept — try to disprove that",
      ),
    );
    ok(check.includes("without the first reviewer's verdicts"));
    ok(
      check.includes(
        "after a fix, the next round starts again with a first reviewer",
      ),
    );
    ok(check.includes("both reviewers find every promise **kept**"));
    ok(brief.includes("### When you are asked to disprove a pass"));
    ok(brief.includes("look for the input or situation that would break it"));
    ok(
      brief.includes(
        "Never mark a promise kept because the other reviewer did",
      ),
    );
    ok(convention.includes("no change passes on one reviewer's word"));
  });

  it("re-checks before merge when the branch content or the card changed", () => {
    const check = read(".claude/commands/linear/reference/card-check.md");

    ok(check.includes("Checked tree:"));
    ok(check.includes("Checked card:"));
    ok(check.includes("Record the tree from the passing round"));
    ok(check.includes("git rev-parse HEAD^{tree}"));
    ok(
      check.includes(
        "Different tree, different card, no `## Card check` section, or any verdict not Kept",
      ),
    );
  });

  it("explains both ends of the check in the conventions", () => {
    const page = "check-the-card-at-the-start-and-the-end.md";
    const convention = read(`docs/conventions/${page}`);

    ok(read("docs/conventions/index.md").includes(`(${page})`));
    ok(
      inOrder(convention, [
        "### At the start",
        "### At the end",
        "### Never quietly rewrite the card",
      ]),
    );
    for (const finding of [
      "Uncheckable",
      "Contradictory",
      "Missing",
      "Stale",
      "Mechanism",
    ]) {
      ok(convention.includes(`| **${finding}** |`), finding);
    }
    ok(convention.includes("| Finding | Meaning | A stop when |"));
    ok(convention.includes("before 6 October 2026"));
  });
});

describe("card start check", () => {
  it("runs in /linear:start after the Vision check and before any branch or code", () => {
    const start = read(".claude/commands/linear/start.md");

    ok(
      inOrder(start, [
        "### 2. Vision check",
        "### 3. Check the card",
        "reference/card-start-review.md",
        "### 6. Resolve the correct branch",
        "### 8. Plan, then implement",
      ]),
    );
  });

  it("starts a card with no findings without a prompt", () => {
    const start = read(".claude/commands/linear/start.md");

    ok(start.includes("continue to step 4 without a prompt"));
  });

  it("fixes its own findings and asks only about the card's purpose", () => {
    const start = read(".claude/commands/linear/start.md");
    const brief = read(
      ".claude/commands/linear/reference/card-start-review.md",
    );

    ok(
      start.includes(
        "**Notes only** — post them as one comment on the card and continue",
      ),
    );
    ok(
      start.includes(
        "**Stops** — fix them yourself before any branch exists, in both modes",
      ),
    );
    ok(start.includes("lists each change"));
    ok(
      start.includes(
        "Ask the user only when a fix would change what the card is for",
      ),
    );
    ok(brief.includes("you report, the orchestrator acts"));
  });

  it("checks the card once, not again on resuming in a worktree", () => {
    const start = read(".claude/commands/linear/start.md");

    ok(
      start.includes(
        "Skip this step when the current branch is already the card's branch",
      ),
    );
  });

  it("treats an older card's mechanism stop as a note", () => {
    const start = read(".claude/commands/linear/start.md");

    ok(start.includes("created in Linear before 2026-10-06"));
    ok(start.includes("treat a `mechanism` stop as a note"));
  });

  it("reports five kinds of finding, each with a level", () => {
    const brief = read(
      ".claude/commands/linear/reference/card-start-review.md",
    );

    for (const finding of [
      "`uncheckable`",
      "`contradictory`",
      "`missing`",
      "`stale`",
      "`mechanism`",
    ]) {
      ok(brief.includes(finding), finding);
    }
    ok(brief.includes('"level": "stop | note"'));
    ok(brief.includes("A note never stops the run"));
    ok(brief.includes("never from the conversation that planned it"));
    ok(brief.includes("list-by-parent <epic-UUID>"));
    ok(brief.includes("`evidence` and `proposed` are mandatory"));
  });
});

describe("reviewer diff base", () => {
  it("reads only what the branch changed since it left main", () => {
    for (const brief of ["card-check-review.md", "simplify-review.md"]) {
      const text = read(`.claude/commands/linear/reference/${brief}`);

      ok(text.includes("git diff $(git merge-base main HEAD)"), brief);
      ok(!text.includes("git diff main\n"), brief);
    }
  });
});
