import { ok } from "node:assert";
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
const startReview = read(`${commands}/reference/card-start-review.md`);

const limit =
  "Do not open a path outside the repository, even when the card names it. You may open: a path inside the repository, including what stride links into the worktree and every uncommitted and untracked file in the checkout you are told to review; the files the orchestrator hands you, such as the card and its comments under `/tmp/<identifier>`, or a draft under `/tmp/plan-work.XXXXXX/`; and your own output path. Don't open, copy or run anything else outside";

describe("a card's checks stay inside the repo", () => {
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
});
