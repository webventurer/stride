import { ok } from "node:assert";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

function read(path) {
  return readFileSync(join(strideRoot, path), "utf8");
}

describe("moves the needle", () => {
  it("is a shared reference that keeps recurring learnings and names one-offs in one line", () => {
    const path = ".claude/commands/linear/reference/moves-the-needle.md";

    ok(existsSync(join(strideRoot, path)));
    const reference = read(path);
    ok(reference.includes("recurs"));
    ok(reference.includes("one line"));
    ok(reference.includes("safety"));
  });

  it("is checked by plan-work after the code check and before the draft, in both modes", () => {
    const plan = read(".claude/commands/linear/plan-work.md");
    const check = plan.indexOf("Will it move the needle?");

    ok(check > plan.indexOf("### 7. "));
    ok(check < plan.indexOf("### 9. Draft the issue"));
    ok(plan.includes("reference/moves-the-needle.md"));
    ok(plan.includes("In unattended mode, file nothing and report the reason"));
    ok(plan.includes("recommend not filing"));
    ok(plan.includes("In interactive mode the person can overrule the recommendation"));
  });

  it("counts a person's own request as the case but not a follow-up an agent found", () => {
    const plan = read(".claude/commands/linear/plan-work.md");

    ok(plan.includes("the person's own words ask for this specific piece of work"));
    ok(plan.includes("not an explicit request"));
  });

  it("files only the follow-ups that make the case when one run files several", () => {
    const plan = read(".claude/commands/linear/plan-work.md");

    ok(plan.includes("names each one left out"));
  });

  it("puts the three answers in Why this matters, cross-project drafts included", () => {
    const plan = read(".claude/commands/linear/plan-work.md");

    ok(plan.includes("how often it happened, what it costs, and what happens if nothing is done"));
    ok(plan.includes("beside the cross-project line"));

    for (const name of ["story", "bug", "epic"]) {
      const template = read(`.claude/commands/linear/reference/templates/${name}.md`);
      ok(template.includes("what happens if nothing is done"), name);
    }
  });

  it("is where carry-lessons and /vision-evolve send the same judgement", () => {
    const carry = read(".claude/commands/linear/reference/carry-lessons.md");
    const evolve = read(".claude/skills/vision-evolve/SKILL.md");

    ok(carry.includes("moves-the-needle.md"));
    ok(evolve.includes("moves-the-needle.md"));
  });

  it("leaves a one-off lesson and a one-off learning as they were", () => {
    const carry = read(".claude/commands/linear/reference/carry-lessons.md");
    const evolve = read(".claude/skills/vision-evolve/SKILL.md");

    ok(carry.includes("no card in Todo is reworded for it"));
    for (const path of [
      ".claude/commands/linear/reference/carry-lessons.md",
      ".claude/commands/linear/reference/output-focus.md",
      ".claude/commands/linear/reference/todo-run.md",
    ]) {
      ok(read(path).includes("one-off lessons named and left"), path);
    }
    ok(evolve.includes("adds no Success criterion"));
    ok(evolve.includes("still gets the line it needs"));
  });
});
