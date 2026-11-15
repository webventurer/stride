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

const step10a = finish.slice(
  finish.indexOf("**Step 10a"),
  finish.indexOf("**Step 10b"),
);

const step10c = finish.slice(
  finish.indexOf("**Step 10c"),
  finish.indexOf("### 11."),
);

const step15 = finish.slice(
  finish.indexOf("### 15."),
  finish.indexOf("### 16."),
);

const errorHandling = finish.slice(finish.indexOf("## Error handling"));

describe("/linear:finish updating the main checkout", () => {
  it("never runs a pull that could merge or rebase", () => {
    const pulls = finish
      .split("\n")
      .filter(
        (line) =>
          !line.startsWith("|") && /\bgit\s+(-C\s+\S+\s+)?pull\b/.test(line),
      );
    ok(pulls.length > 0, "finish.md has no git pull command at all");
    for (const line of pulls) {
      ok(line.includes("--ff-only"), `pull without --ff-only: ${line}`);
    }
  });

  it("pulls in step 10a with --ff-only on the main checkout", () => {
    ok(step10a.includes("git -C <main-repo-path> pull --ff-only"));
  });

  it("reports a refused pull in step 10a with the local commits", () => {
    ok(step10a.includes("git -C <main-repo-path> log origin/main..main"));
    ok(/refus/i.test(step10a));
  });

  it("runs the check script before the checkout and the pull", () => {
    const script = step10a.indexOf(".claude/tools/main_checkout_update.sh");
    ok(script >= 0, "step 10a doesn't run main_checkout_update.sh");
    ok(script < step10a.indexOf("checkout main"));
    ok(script < step10a.indexOf("pull --ff-only"));
    ok(step10a.includes("`updated`"));
  });

  it("leaves the checkout alone for every reason the script prints", () => {
    for (const reason of [
      "uncommitted changes",
      "unpushed commits",
      "on branch",
      "detached HEAD",
      "the fetch failed",
    ]) {
      ok(step10a.includes(reason), `step 10a doesn't cover: ${reason}`);
    }
    ok(step10a.includes("git pull --rebase"));
    ok(
      step10a.includes("include the reason in the message to the coordinator"),
    );
  });

  it("skips the local branch deletion when the checkout was left alone", () => {
    ok(/left alone/.test(step10c));
  });

  it("reads the merge commit from origin/main, not the main checkout", () => {
    ok(step15.includes("git -C <main-repo-path> fetch origin main"));
    ok(step15.includes("log origin/main --first-parent"));
    ok(!step15.includes("log -1"));
  });

  it("syncs the Vision from the merge, not the main checkout's copy", () => {
    ok(step15.includes("show <merge_commit>:VISION.md"));
    ok(step15.includes("--content @/tmp/<identifier>/VISION.md"));
    ok(!step15.includes("--content @VISION.md"));
  });

  it("lists a left-alone checkout in the error handling", () => {
    ok(/left alone/.test(errorHandling));
  });
});
