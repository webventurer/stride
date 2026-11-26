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
const drafting = section(
  plan,
  "### 7. Write the brief",
  "### 8. Check the code",
);

describe("a card drafted from a brief", () => {
  it("gives the drafter the brief as all it has from the conversation", () => {
    ok(
      drafting.includes(
        "It is the only thing the drafter gets from this conversation",
      ),
    );
    for (const held of [
      "**The person's words,** quoted exactly",
      "**The decisions agreed**",
      "**What is ruled out**",
      "**Facts and evidence the code doesn't show,**",
      "**How the run was called:**",
    ]) {
      ok(drafting.includes(held), held);
    }
    ok(drafting.includes("It holds no plan and no card wording"));
    ok(drafting.includes("it is all you have from the conversation"));
  });

  it("reads fetched main for a redraft and for another project", () => {
    ok(drafting.includes("fetch `main` again as item 3 does"));
    ok(
      drafting.includes(
        "reads that code with `git -C <target-repo>` on `origin/main`",
      ),
    );
    ok(!plan.includes("Grep/Glob, and read it"));
  });

  it("reads a Vision changed in this checkout, for drafter and reviewers", () => {
    ok(drafting.includes("and to each reviewer's in step 12"));
    ok(
      read(".claude/commands/linear/reference/card-start-review.md").includes(
        "read `VISION.md` from the working tree instead",
      ),
    );
  });

  it("keeps a read time for each card", () => {
    ok(drafting.includes("> <card-folder>/read-at.txt"));
    ok(plan.includes('--read-at "$(cat <card-folder>/read-at.txt)"'));
  });

  it("has the drafter read the Vision", () => {
    ok(drafting.includes("Read `VISION.md` first"));
  });

  it("fetches main before the drafter reads the code in full", () => {
    ok(
      inOrder(drafting, [
        "read-at.txt",
        "git fetch origin main",
        "**Spawn the drafter**",
      ]),
    );
    ok(plan.includes("read it in full"));
    ok(!plan.includes("2–5"));
  });
});
