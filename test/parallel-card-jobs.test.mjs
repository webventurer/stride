import { ok, strictEqual } from "node:assert";
import { execFileSync } from "node:child_process";
import {
  lstatSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readlinkSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
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

const skill = read(".claude/skills/parallel-sessions/SKILL.md");
const brief = read(".claude/skills/parallel-sessions/BRIEF.md");

describe("a /parallel-sessions job running a stride card", () => {
  it("gets the main checkout's .stride.json in the worktree the skill makes", () => {
    ok(
      inOrder(skill, [
        "#### Without a side-session tool",
        ".claude/tools/link_stride_install.sh",
        ".claude/tools/share_stride_settings.sh",
        "**Check git sees nothing new.**",
      ]),
    );
    ok(skill.includes("report it and don't start that job"));
  });

  it("leaves the worktree with .stride.json linked and git status clean", () => {
    const base = mkdtempSync(join(tmpdir(), "stride-card-job-"));
    const main = join(base, "app");
    const worktree = join(main, ".claude/worktrees/job-1");
    const git = (cwd, ...args) =>
      execFileSync("git", ["-C", cwd, ...args], { encoding: "utf8" });
    const tools = join(strideRoot, ".claude/tools");
    try {
      mkdirSync(join(main, ".claude/tools"), { recursive: true });
      git(base, "init", "-q", "-b", "main", main);
      writeFileSync(
        join(main, ".gitignore"),
        ".stride.json\n.claude/worktrees/\n# >>> stride (auto-managed, do not edit) >>>\n.claude/tools/\n# <<< stride <<<\n",
      );
      writeFileSync(join(main, ".stride.json"), '{"unattended": true}');
      writeFileSync(join(main, ".claude/tools/linear_cli.py"), "x");
      git(main, "add", ".gitignore");
      git(
        main,
        "-c",
        "user.email=t@t",
        "-c",
        "user.name=t",
        "commit",
        "-qm",
        "init",
      );
      git(main, "worktree", "add", "-q", worktree, "-b", "job-1");

      execFileSync(join(tools, "link_stride_install.sh"), [main, worktree]);
      execFileSync(join(tools, "share_stride_settings.sh"), [main, worktree]);

      const settings = join(worktree, ".stride.json");
      ok(lstatSync(settings).isSymbolicLink());
      strictEqual(readlinkSync(settings), join(main, ".stride.json"));
      strictEqual(git(worktree, "status", "--porcelain"), "");
    } finally {
      rmSync(base, { recursive: true, force: true });
    }
  });

  it("stops at its pull request, whatever unattended says", () => {
    const start = read(".claude/commands/linear/start.md");

    ok(
      inOrder(start, [
        "### 19. Review",
        "When this card runs as a `/parallel-sessions` job",
        "whatever `unattended` says",
      ]),
    );
    ok(brief.includes("`/linear:start` stops once the pull request is open"));
  });

  it("merges one card at a time, when the coordinator says", () => {
    ok(skill.includes("one card at a time"));
    ok(skill.includes("only once the job reports that its merge has landed"));
    ok(skill.includes("tell its session to run `/linear:finish`"));
    ok(
      brief.includes(
        "Keep your slot, renewing it at each interval, until `/linear:finish` is done",
      ),
    );
  });

  it("leaves the job's worktree and local branch for the coordinator to remove", () => {
    const finish = read(".claude/commands/linear/finish.md");

    ok(finish.includes("As a `/parallel-sessions` job, skip this step"));
    ok(
      finish.includes(
        "As a `/parallel-sessions` job, delete only the remote branch",
      ),
    );
    ok(brief.includes("Message the coordinator that the card has merged"));
  });

  it("runs the next batch from Todo when /linear:start names no card", () => {
    const start = read(".claude/commands/linear/start.md");

    ok(start.includes("linear_cli.py start-choice --project"));
    ok(
      inOrder(start, [
        "run [`/linear:next-steps`](next-steps.md) first",
        "linear_cli.py start-choice --project",
      ]),
    );
    ok(
      read(".claude/commands/linear/next-steps.md").includes(
        "When `/linear:start` runs next-steps because no card was named, skip this step",
      ),
    );
    ok(brief.includes("message the coordinator with the question instead"));
    ok(
      skill.includes(
        "reports a question instead of a pull request leaves its card out",
      ),
    );
    for (const action of [
      "`resume`",
      "`ask`",
      "`batch`",
      "`single`",
      "`blocked`",
      "`empty`",
    ]) {
      ok(start.includes(action), action);
    }
    ok(start.includes('gives the skill its "go" itself'));
    ok(start.includes("As a `/parallel-sessions` job, run this step anyway"));
  });

  it("lets /linear:start settle a card batch and, unattended, give the go", () => {
    ok(skill.includes("When `/linear:start` runs a batch of cards"));
    ok(skill.includes("always as background `claude -p` sessions"));
    ok(skill.includes("once the user has approved its pull request"));
  });

  it("frees an exited job's slot and keeps its worktree until the exit notice", () => {
    ok(
      inOrder(skill, [
        "When a job's session exits holding a slot, release its slot at once",
        "An idle notice releases nothing",
        "exited, waiting to be resumed",
        "a job already marked merged or failed keeps that state",
        "tells it to claim a slot before it carries on",
        "resume an exited job only when `slots.py status` shows a free slot",
        "give the go to a card whose job holds a slot",
        "Remove a job's worktree and archive its session only after that job's exit notice has arrived",
      ]),
    );
  });

  it("keeps a waiting job's turn open and has a job claim again after an exit", () => {
    ok(
      inOrder(brief, [
        "A `claude -p` session ends when its turn ends",
        "keep your turn open for every wait on the coordinator",
        "renewing your slot at each interval while you hold one",
        "Wait in steps of no more than 60 seconds",
        "never in one long sleep",
        "told to carry on after your session exited, claim a slot first",
      ]),
    );
  });
});

describe("the coordinator's steps for a batch of stride cards", () => {
  const step5 = skill.slice(
    skill.indexOf("### 5. Watch and check"),
    skill.indexOf("### 6. Report"),
  );
  const referenceFiles = [
    "chain-of-command.md",
    "chain-of-command-config.md",
    "testing-the-chain-of-command.md",
  ].map((name) => read(`.claude/skills/parallel-sessions/reference/${name}`));

  it("names the card in a card job's brief and checks the pull request's files against it", () => {
    ok(skill.includes("names the card in place of a path list"));
    ok(brief.includes("**Scope:**"));
    ok(step5.includes("gh pr diff <number> --name-only"));
    ok(step5.includes("the card's \"What we'll do\" doesn't call for"));
  });

  it("builds the combined check in a scratch worktree with the install linked and settings shared", () => {
    ok(
      inOrder(step5, [
        "scratch worktree",
        "link_stride_install.sh",
        "share_stride_settings.sh",
        "don't run the check",
      ]),
    );
  });

  it("keeps each batch in its own folder under work/runs", () => {
    ok(skill.includes("`work/runs/<batch>/`"));
    ok(skill.includes("YYYY-MM-DD-HHMMSS"));
    ok(skill.includes("never reuses a folder that exists"));
    for (const text of [skill, brief, ...referenceFiles]) {
      ok(!/work\/(logs|briefs)\//.test(text));
      ok(!text.includes("work/progress.md"));
    }
  });

  it("has the card that merges second merge main in before it gets the go", () => {
    ok(
      inOrder(step5, [
        "also changed",
        "merge `main` into its branch",
        "fix any clash keeping both cards' lines",
        "rerun its checks",
        "give the go only after",
      ]),
    );
    ok(step5.includes("you ask the user, because which card's wording wins"));
  });

  it("removes a job's worktree with git worktree remove and never --force", () => {
    ok(step5.includes("`git worktree remove <path>`"));
    ok(step5.includes("git -C <path> status --porcelain"));
    ok(step5.includes("not to use `remove_card_worktree.sh`"));
    for (const text of [skill, brief, ...referenceFiles]) {
      ok(!/worktree remove[^`\n]*--force/.test(text));
    }
  });
});

describe("an unattended run through Todo", () => {
  const todoRun = read(".claude/commands/linear/reference/todo-run.md");
  const start = read(".claude/commands/linear/start.md");

  it("is the route /linear:start takes after a batch when unattended", () => {
    ok(start.includes("[Todo run](reference/todo-run.md)"));
    ok(!start.includes("running on through Todo is a later story"));
  });

  it("asks stride for the next batch with every card it has started", () => {
    ok(todoRun.includes("start-choice --project"));
    ok(todoRun.includes("--started <card>"));
    ok(todoRun.includes("as a batch of one"));
  });

  it("holds every question for one message at the end of the run", () => {
    ok(todoRun.includes("No batch's report puts a question to the user"));
    ok(skill.includes("no batch's report puts a question to the user"));
    ok(skill.includes("put no question to the user mid-run"));
  });

  it("names the failed cards and each lesson in the final report", () => {
    ok(
      inOrder(todoRun, [
        "**Done:**",
        "**Failed:**",
        "**Waiting:**",
        "**Lessons:**",
        "**Questions:**",
      ]),
    );
  });
});

describe("an unattended run through a named epic", () => {
  const epicIteration = read(
    ".claude/commands/linear/reference/epic-iteration.md",
  );
  const start = read(".claude/commands/linear/start.md");
  const batchOnMain = epicIteration.slice(
    epicIteration.indexOf("## Batch on `main`"),
    epicIteration.indexOf("## E1."),
  );

  it("asks stride again after each batch with the epic and every card run", () => {
    ok(batchOnMain.includes('--epic "<epic-identifier>"'));
    ok(batchOnMain.includes("--started <card>"));
    ok(batchOnMain.includes("[Todo run](todo-run.md)"));
  });

  it("runs a lone card as a batch of one so the run goes on", () => {
    ok(batchOnMain.includes("as a batch of one"));
    ok(
      !batchOnMain.includes(
        "even for a `single` card: when that card's pull request is merged, the run ends",
      ),
    );
  });

  it("stops after one batch only in interactive mode", () => {
    ok(batchOnMain.includes("Interactive mode"));
    ok(!batchOnMain.includes("Then stop: one batch, in both modes"));
  });

  it("reports each of the epic's cards as done, failed or waiting", () => {
    ok(inOrder(batchOnMain, ["**Done:**", "**Failed:**", "**Waiting:**"]));
  });

  it("lists a failed card once, and ends on blocked or empty with that report", () => {
    ok(batchOnMain.includes("that isn't listed as failed"));
    ok(batchOnMain.includes("it opens the final report below"));
  });

  it("is described by /linear:start as running on until the epic is done", () => {
    ok(start.includes("until none of its cards can start"));
  });
});
