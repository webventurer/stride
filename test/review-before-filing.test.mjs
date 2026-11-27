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

const plan = read(".claude/commands/linear/plan-work.md");
const reviewer = read(".claude/commands/linear/reference/card-start-review.md");
const review = section(
  plan,
  "### 12. Check the draft",
  "### 13. Show the draft",
);
const opening = section(
  plan,
  "### 13. Show the draft",
  "### 14. Create the issue",
);

describe("the review before a card is filed", () => {
  it("runs the start check's three lenses on the draft, without the brief", () => {
    ok(review.includes("reference/card-start-review.md"));
    ok(review.includes("The card is a draft not yet filed"));
    ok(review.includes("never the brief or the conversation"));
    ok(reviewer.includes("## A draft not yet filed"));
  });

  it("starts the three reviewers as Sonnet at medium effort", () => {
    const spawn = review
      .split("\n")
      .find((line) => line.includes("**Spawn three reviewers at once**"));

    ok(spawn.includes("model `sonnet`"), spawn);
    ok(spawn.includes("effort `medium`"), spawn);
    for (const lens of ["Promise by promise", "Try to break it", "Prove it"]) {
      ok(spawn.includes(lens), lens);
    }
  });

  it("fixes every stop, writes in edge cases and checks the brief before creating", () => {
    ok(
      inOrder(plan, [
        "**Already done**",
        "**Fix every stop**",
        "**Write in every edge case**",
        "**Check the draft against the brief:**",
        "### 14. Create the issue",
        "issue record-check <new-id>",
      ]),
    );
  });

  it("reviews the draft after the optional second-opinion loop", () => {
    ok(inOrder(plan, ["### 11. Cross-model", "### 12. Check the draft"]));
    ok(plan.includes("then continue to step 12, so the review reads it"));
  });

  it("files nothing without all three lenses, or with a stop still unfixed", () => {
    ok(review.includes("file nothing for that draft, in both modes"));
    ok(opening.includes("never filed,** on either path"));
    ok(
      opening.includes("with no such stop open, continue directly to step 14"),
    );
  });

  it("records no check for a cross-project card or a draft changed after review", () => {
    ok(
      plan.includes(
        "Post none for a cross-project card, or for a draft that changed after its review",
      ),
    );
  });
});
