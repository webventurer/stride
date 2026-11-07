import { ok } from "node:assert";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

function read(path) {
  return readFileSync(join(strideRoot, path), "utf8").replace(/\s+/g, " ");
}

function inOrder(text, markers) {
  let at = -1;
  return markers.every((marker) => {
    at = text.indexOf(marker, at + 1);
    return at !== -1;
  });
}

const brief = read(".claude/commands/linear/reference/card-start-review.md");
const start = read(".claude/commands/linear/start.md");
const step3 = start.slice(
  start.indexOf("### 3. Check the card"),
  start.indexOf("### 4. Load project context"),
);

describe("a card whose work is already done", () => {
  it("is reported by a reviewer as a `done` finding that names what keeps each promise", () => {
    ok(brief.includes("## The six kinds of finding"));
    ok(brief.includes("| `done` |"));
    ok(
      brief.includes(
        "Every promise that describes a result on `main` is already kept by what is on `main`",
      ),
    );
    ok(
      brief.includes("For each promise, the commit, card or file that keeps it"),
    );
    ok(brief.includes('"finding": "done | uncheckable'));
  });

  it("counts only promises about a result on `main`", () => {
    ok(brief.includes("Only promises about a result on `main` count towards `done`"));
    ok(
      brief.includes(
        "a \"What we won't do\" line, a \"How to test it\" line and the \"Live check\" neither count",
      ),
    );
    ok(brief.includes("A card with no promise about a result on `main`"));
  });

  it("is cancelled in /linear:start only when all three reviewers say so", () => {
    ok(step3.includes("**Already done** — when all three files hold a `done` finding"));
    ok(
      step3.includes(
        "A `done` finding from fewer than all three reviewers cancels nothing",
      ),
    );
  });

  it("is moved to Canceled with a comment naming what keeps each promise, and builds nothing", () => {
    ok(
      inOrder(step3, [
        "**Already done**",
        "comment",
        "names, for each promise, the commit, card or file that keeps it",
        "--state Canceled",
        "starts no branch and opens no pull request",
      ]),
    );
    ok(!step3.includes("--state Cancelled"));
  });

  it("is checked before any branch exists, in both modes", () => {
    ok(
      inOrder(start, [
        "**Already done**",
        "in both modes",
        "### 6. Resolve the correct branch",
      ]),
    );
  });

  it("is reworded, not cancelled, when only partly done", () => {
    ok(
      step3.includes(
        "A card that is only partly done is not cancelled: its `stale` findings reword it",
      ),
    );
  });
});

describe("a cancelled card in a batch", () => {
  const jobBrief = read(".claude/skills/parallel-sessions/BRIEF.md");
  const todoRun = read(".claude/commands/linear/reference/todo-run.md");

  it("tells the coordinator it ended in Canceled, in place of a pull request, and ends at once", () => {
    ok(
      inOrder(jobBrief, [
        "the card ended in Canceled",
        "no pull request",
        "Release your slot and end your turn at once",
      ]),
    );
  });

  it("is listed in the Todo run's final report with the reason in its comment", () => {
    const report = todoRun.slice(todoRun.indexOf("## The final report"));

    ok(report.includes("**Canceled:**"));
    ok(report.includes("the reason in its comment"));
  });

  it("is left out of the next batch", () => {
    ok(todoRun.includes("A card that ended in Canceled leaves the batch"));
  });

  it("is finished for the coordinator, not resumed, not a failure and not waited for", () => {
    const skill = read(".claude/skills/parallel-sessions/SKILL.md");

    ok(
      skill.includes(
        "A card job that reports its card Canceled leaves it out of the batch the same way",
      ),
    );
    ok(skill.includes("it is finished, not failed"));
    ok(skill.includes("a job already marked merged, failed or canceled keeps that state"));
    ok(skill.includes("which cards ended in Canceled"));
  });
});
