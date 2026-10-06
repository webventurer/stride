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
  const positions = markers.map((marker) => text.indexOf(marker));
  return positions.every(
    (at, i) => at !== -1 && (i === 0 || at > positions[i - 1]),
  );
}

describe("card check", () => {
  it("runs in /linear:start after the simplification review and before the PR", () => {
    const start = read(".claude/commands/linear/start.md");

    ok(
      inOrder(start, [
        "### 9a. Simplification review",
        "### 9b. Card check",
        "reference/card-check.md",
        "### 15. Create PR",
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
        "### 6a. Confirm Vision outcome",
        "### 6b. Check the change against its card",
        "reference/card-check.md",
        "### 7. Merge",
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
  });
});
