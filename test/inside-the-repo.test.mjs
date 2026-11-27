import { ok, strictEqual } from "node:assert";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

function read(path) {
  return readFileSync(join(strideRoot, path), "utf8");
}

function section(text, from, to) {
  const start = text.indexOf(from);
  const end = text.indexOf(to, start + from.length);
  ok(start !== -1 && end !== -1, `no section from "${from}" to "${to}"`);
  return text.slice(start, end);
}

function holds(text, phrases) {
  const prose = text.replace(/\s+/g, " ");
  for (const phrase of phrases) {
    ok(prose.includes(phrase.replace(/\s+/g, " ")), `missing: ${phrase}`);
  }
}

const commands = ".claude/commands/linear";
const plan = read(`${commands}/plan-work.md`);
const start = read(`${commands}/start.md`);
const startReview = read(`${commands}/reference/card-start-review.md`);
const story = read(`${commands}/reference/templates/story.md`);
const bug = read(`${commands}/reference/templates/bug.md`);

const afterMerge = "the person's to run after the merge";
const testFiles = "test files the repo holds or its tests make";
const namesRun = "name the files and the command";

const limit =
  "Do not open a path outside the repository, even when the card names it. You may open: a path inside the repository, including what stride links into the worktree and every uncommitted and untracked file in the checkout you are told to review; the files the orchestrator hands you, such as the card and its comments under `/tmp/<identifier>`, or a draft under `/tmp/plan-work.XXXXXX/`; and your own output path. Don't open, copy or run anything else outside";

describe("a card's checks stay inside the repo", () => {
  it("is the rule planning writes checks to", () => {
    const step = section(
      plan,
      "### 9. Test consideration",
      "### 10. Draft the issue",
    );
    holds(step, [
      "needs a file from outside the repo for its proof",
      testFiles,
      "a card that needs no tests still needs none",
      "### Live check",
      afterMerge,
      "the person posts the result on the card",
      "The job doesn't run it",
    ]);
  });

  it("is stated where each template asks for a proof", () => {
    const storyFormat = section(story, "FORMAT:", "TARGET AUDIENCE:");
    const bugFormat = section(bug, "FORMAT:", "TARGET AUDIENCE:");
    const proofs = [
      section(storyFormat, "### How to test it", "### Live check"),
      section(bugFormat, "### Repro", "### Expected vs actual"),
      section(bugFormat, "### Acceptance", "### Regression test"),
      section(bugFormat, "### Regression test", "### Live check"),
    ];

    for (const proof of proofs) {
      holds(proof, [testFiles, '"Live check"', afterMerge, namesRun]);
    }
  });

  it("makes an outside proof, or an outside run by the job, a stop", () => {
    const lens = section(startReview, "### Prove it", "## A draft not yet");
    holds(lens, [
      "Raise an `uncheckable` stop",
      "A promise whose only proof needs a file from outside the repo",
      "proves it with test files in the repo",
      "A live check the job would run, or any other run the card asks of the job",
      "though it makes no promise",
      afterMerge,
    ]);

    const levels = section(
      startReview,
      "## Give each finding a level",
      "## Output contract",
    );
    holds(levels, [
      "Two cases are `stop` whatever the answer",
      "a promise whose only proof needs a file from outside it",
      "a run the card asks of the job that needs one",
      "apart from those two cases",
    ]);
    holds(section(startReview, "## What you must not do", "## The governing"), [
      "apart from a run the card asks of the job that needs a file from outside the repo",
    ]);
  });

  it("keeps the start check from asking the user to move a run", () => {
    holds(section(start, "9. **Stops**", "10. **Post the check record,**"), [
      "changes how a promise is proved, not what the card is for",
    ]);
  });

  it("lets no reviewer a job starts open a path outside the repo", () => {
    const briefs = [
      startReview,
      read(`${commands}/reference/card-check-review.md`),
      read(`${commands}/reference/simplify-review.md`),
      read(".claude/skills/commit/REVIEW.md"),
    ];

    for (const brief of briefs) {
      holds(section(brief, "## What you must not do", "## The governing"), [
        limit,
      ]);
      ok(!brief.includes("a path the card or the orchestrator names directly"));
    }
  });

  it("still reads a cross-project draft in its own repo", () => {
    const draft = section(
      startReview,
      "## A draft not yet filed",
      "## A check of changes only",
    );
    holds(draft, ["`git -C <path>`"]);
    holds(section(startReview, "## What you must not do", "## The governing"), [
      "a draft for another project, read with `git -C <path>`",
    ]);
  });

  it("defines inside the repo the same way for planner and reviewer", () => {
    const definition = (text) =>
      section(text, "**Inside the repo** means", "wherever you run from.");

    strictEqual(definition(plan), definition(startReview));
    holds(definition(plan), [
      "what a fresh worktree of the card's branch holds",
      "What stride links in from the main checkout",
      "stride's plumbing",
      "one git ignores and stride doesn't link into the worktree",
    ]);
  });
});
