import { ok } from "node:assert";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const finish = readFileSync(
  join(strideRoot, ".claude/commands/linear/finish.md"),
  "utf8",
);

const step9a = finish.slice(
  finish.indexOf("**Step 9a"),
  finish.indexOf("**Step 9b"),
);

describe("/linear:finish updating the main checkout", () => {
  it("never runs a pull that could merge or rebase", () => {
    const pulls = finish
      .split("\n")
      .filter((line) => /\bgit\s+(-C\s+\S+\s+)?pull\b/.test(line));
    ok(pulls.length > 0, "finish.md has no git pull command at all");
    for (const line of pulls) {
      ok(line.includes("--ff-only"), `pull without --ff-only: ${line}`);
    }
  });

  it("pulls in step 9a with --ff-only on the main checkout", () => {
    ok(step9a.includes("git -C <main-repo-path> pull --ff-only"));
  });

  it("reports a refused pull in step 9a with the local commits", () => {
    ok(step9a.includes("git -C <main-repo-path> log origin/main..main"));
    ok(/refus/i.test(step9a));
  });
});
