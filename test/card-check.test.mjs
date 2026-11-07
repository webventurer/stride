import { ok } from "node:assert";
import { existsSync, readFileSync } from "node:fs";
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
  });

  it("judges only what the finished change can show", () => {
    const template = read(
      ".claude/commands/linear/reference/templates/story.md",
    );
    const brief = read(
      ".claude/commands/linear/reference/card-check-review.md",
    );
    const start = read(".claude/commands/linear/start.md");

    ok(!template.includes("Write tests first"));
    ok(template.includes('goes under "Live\ncheck" instead'));
    ok(template.includes('belongs under "Live check" too'));
    ok(
      brief.includes('"Assumptions to confirm" and "Live check" give context'),
    );
    ok(start.includes("Write the failing tests first"));
  });

  it("runs three Sonnet reviewers, each through its own lens, and keeps the worst verdict", () => {
    const check = read(".claude/commands/linear/reference/card-check.md");
    const brief = read(
      ".claude/commands/linear/reference/card-check-review.md",
    );
    const lenses = ["Promise by promise", "Try to break it", "Prove it"];

    for (const lens of lenses) {
      ok(check.includes(`"${lens}"`), lens);
      ok(brief.includes(`### ${lens}`), lens);
    }
    ok(check.includes("Your lens is <"));
    ok(brief.includes("Every lens keeps the read-only rule"));
    ok(brief.includes("only from the sections [Find the promises]"));
    ok(check.includes("Spawn three fresh sub-agents at once"));
    ok(check.includes("model `sonnet`"));
    ok(check.includes("each with its own output path"));
    ok(
      check.includes(
        "Each promise takes the worst verdict any reviewer gave it, in this order: `unclear`, `broken`, `kept-unproven`, `kept`",
      ),
    );
    ok(check.includes("An unclear verdict or an empty file from any reviewer"));
    ok(check.includes("| <the card's words> | Not acted on |"));
    ok(
      check.includes(
        "Same tree, same card, every verdict Kept, Fixed or Not acted on",
      ),
    );
  });

  it("records what each check cost and found, so the checks can be judged on real cards", () => {
    const check = read(".claude/commands/linear/reference/card-check.md");
    const start = read(".claude/commands/linear/start.md");

    ok(
      check.includes(
        "Check cost: start <s> s (slowest of three), <n> stops, <n> notes · end <s> s (slowest of three), <n> findings: <n> fixed, <n> not acted on",
      ),
    );
    ok(start.includes("Note how long the check took"));
  });

  it("checks once and leaves a second look at fixes to the user", () => {
    const check = read(".claude/commands/linear/reference/card-check.md");
    const brief = read(
      ".claude/commands/linear/reference/card-check-review.md",
    );

    ok(check.includes("The check runs once"));
    ok(check.includes("do not run the reviewers again"));
    ok(check.includes("The pull request records each fix next to its verdict"));
    ok(!check.includes("try to disprove that"));
    ok(!brief.includes("disprove a pass"));
  });

  it("re-checks before merge when the branch content or the card changed", () => {
    const check = read(".claude/commands/linear/reference/card-check.md");

    ok(check.includes("Checked tree:"));
    ok(check.includes("Checked card:"));
    ok(
      check.includes(
        "Note the tree straight after committing the check's fixes",
      ),
    );
    ok(check.includes("git rev-parse HEAD^{tree}"));
    ok(
      check.includes(
        "Different tree, different card, no `## Card check` section, or any other verdict",
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

describe("carrying a merged card's lesson to Todo", () => {
  it("runs in /linear:finish after Done and before the milestone check", () => {
    const finish = read(".claude/commands/linear/finish.md");

    ok(
      inOrder(finish, [
        "### 10. Update Linear → done",
        "### 11. Carry the lesson to Todo",
        "reference/carry-lessons.md",
        "### 12. Check milestone completion",
      ]),
    );
  });

  it("rewords with old and new lines, asks on purpose, and says when there's nothing", () => {
    const brief = read(".claude/commands/linear/reference/carry-lessons.md");
    const unattended = read(".claude/commands/linear/reference/unattended.md");

    ok(brief.includes("Old line:"));
    ok(brief.includes("New line:"));
    ok(brief.includes("no lesson for Todo"));
    ok(
      brief.includes(
        "A run through Todo leaves only that card out of its later batches",
      ),
    );
    ok(unattended.includes("A lesson question open on a card started by name"));
    ok(unattended.includes("A run through Todo doesn't stop for it"));
    ok(
      brief.includes(
        "A card started by name stops there, before the next card starts",
      ),
    );
    ok(brief.includes("read it from its record alone"));
    ok(brief.includes("whose verdict is Fixed or Not acted on, as one rule"));
    ok(brief.includes('order-todo --project "<project>" --dry-run'));
    ok(
      brief.includes(
        "never adds or removes a card, or moves one between columns",
      ),
    );
  });

  it("keeps a card with an open lesson question from being built", () => {
    const start = read(".claude/commands/linear/start.md");
    const brief = read(".claude/commands/linear/reference/carry-lessons.md");
    const focus = read(".claude/commands/linear/reference/output-focus.md");

    ok(brief.includes("**Lesson question from <merged card>**"));
    ok(
      start.includes(
        "no later comment starts `Answer:`, stop before anything else",
      ),
    );
    ok(
      start.includes(
        "Other comments posted after the question, including stride's own, don't answer it",
      ),
    );
    ok(focus.includes("Lessons: <cards reworded"));
  });
});

describe("card start check", () => {
  it("runs three Sonnet reviewers at once, one per lens, in /linear:start step 3", () => {
    const start = read(".claude/commands/linear/start.md");
    const step3 = start.slice(
      start.indexOf("### 3. Check the card"),
      start.indexOf("### 4. Load project context"),
    );

    ok(step3.includes("three reviewers at once"));
    ok(step3.includes("model `sonnet`"));
    ok(!step3.includes("`opus`"));
    for (const lens of ["Promise by promise", "Try to break it", "Prove it"]) {
      ok(step3.includes(lens), lens);
    }
    ok(step3.includes("as one list"));
    ok(step3.includes("leaves no findings file is run once more"));
    ok(step3.includes("the slowest of the three"));
    ok(step3.includes("git fetch origin main"));
  });

  it("gives the start and end reviewers the same three lens names", () => {
    const startBrief = read(
      ".claude/commands/linear/reference/card-start-review.md",
    );
    const endBrief = read(
      ".claude/commands/linear/reference/card-check-review.md",
    );

    for (const brief of [startBrief, endBrief]) {
      ok(brief.includes("## Read through your lens"));
      for (const lens of [
        "### Promise by promise",
        "### Try to break it",
        "### Prove it",
      ]) {
        ok(brief.includes(lens), lens);
      }
    }
  });

  it("reads promises from the same definition the end check uses", () => {
    const start = read(
      ".claude/commands/linear/reference/card-start-review.md",
    );

    ok(start.includes("card-check-review.md#find-the-promises"));
    ok(!start.includes('each scenario under "How to test it"'));
  });

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

    ok(
      start.includes(
        "continue to step 4, Load project context, without a prompt",
      ),
    );
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

  it("reads what changed since the card's description last changed", () => {
    const start = read(".claude/commands/linear/start.md");
    const brief = read(
      ".claude/commands/linear/reference/card-start-review.md",
    );
    const agility = read(".claude/commands/linear/reference/agility.md");

    ok(brief.includes("issue description-changed-at <card-id>"));
    ok(brief.includes(".claude/tools/main_changes_since.sh <time>"));
    ok(brief.includes("made since that time"));
    ok(brief.includes("[Agility](agility.md)"));
    ok(start.includes("[agility](reference/agility.md)"));
    ok(agility.includes("A plan is a map, not a contract"));
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

  it("judges a promise by the same two tests when a card is written and when work starts", () => {
    for (const path of [
      ".claude/commands/linear/reference/card-language.md",
      ".claude/commands/linear/reference/templates/story.md",
      ".claude/commands/linear/reference/card-start-review.md",
    ]) {
      const text = read(path).replace(/\s+/g, " ");

      ok(text.includes("can answer it yes or no"), path);
      ok(text.includes("the change was made but doesn't work"), path);
    }
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

describe("reviewers never change the branch", () => {
  const briefs = ["card-start-review.md", "card-check-review.md", "simplify-review.md"];

  for (const brief of briefs) {
    it(`forbids ${brief}'s reviewer every command that moves the branch`, () => {
      const text = read(`.claude/commands/linear/reference/${brief}`);

      ok(
        text.includes("no `git checkout`, `git switch`, `git stash` or `git reset`"),
        brief,
      );
    });
  }

  for (const brief of ["card-start-review.md", "simplify-review.md"]) {
    it(`points ${brief}'s reviewer at the read-only base version of a file`, () => {
      const text = read(`.claude/commands/linear/reference/${brief}`);

      ok(text.includes("`git show $(git merge-base main HEAD):<file>`"), brief);
      ok(text.includes("`git restore`"), brief);
    });
  }
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

describe("the start and end reviewers' setting", () => {
  const files = [
    [".claude/commands/linear/start.md", "**Spawn three reviewers at once.**"],
    [".claude/commands/linear/reference/card-check.md", "Spawn three fresh sub-agents at once"],
  ];

  for (const [path, marker] of files) {
    it(`starts the three reviewers as Sonnet at high effort in ${path}`, () => {
      const spawn = read(path)
        .split("\n")
        .find((line) => line.includes(marker));

      ok(spawn.includes("model `sonnet`"), spawn);
      ok(spawn.includes("effort `high`"), spawn);
    });

    it(`links the measurement behind the setting from ${path}`, () => {
      const link = read(path).match(/\]\(([^)]*chain-of-command-config\.md)[^)]*\)/);

      ok(link, "no link to chain-of-command-config.md");
      ok(existsSync(join(strideRoot, dirname(path), link[1])), link[1]);
    });
  }
});

describe("the simplification reviewer's setting", () => {
  const start = read(".claude/commands/linear/start.md");
  const step10 = start.slice(
    start.indexOf("### 10. Simplification review"),
    start.indexOf("### 11. Card check"),
  );

  it("starts the reviewer as Sonnet at high effort, not Opus", () => {
    const spawn = step10
      .split("\n")
      .find((line) => line.includes("**Spawn the reviewer.**"));

    ok(spawn.includes("model `sonnet`"), spawn);
    ok(spawn.includes("effort `high`"), spawn);
    ok(!step10.includes("`opus`"));
  });

  it("links the measurement behind the setting from step 10", () => {
    const link = step10.match(/\]\(([^)#]*chain-of-command-config\.md)[^)]*\)/);

    ok(link, "no link to chain-of-command-config.md in step 10");
    ok(existsSync(join(strideRoot, ".claude/commands/linear", link[1])), link[1]);
  });
});

describe("where reviewers look for files", () => {
  const briefs = ["card-start-review.md", "card-check-review.md", "simplify-review.md"];

  for (const brief of briefs) {
    it(`keeps the ${brief} reviewer's searches inside the repository`, () => {
      const text = read(`.claude/commands/linear/reference/${brief}`);

      ok(text.includes("git ls-files --cached --others --exclude-standard"), brief);
      ok(text.includes("git grep --untracked"), brief);
      ok(text.includes("never start a search from `/` or the home folder"), brief);
    });
  }

  it("tells card writers to name a file by its path from the repository root", () => {
    const language = read(".claude/commands/linear/reference/card-language.md");

    ok(language.includes("exact file paths from the repository root"));
  });
});
