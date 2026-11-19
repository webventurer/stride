import { ok, strictEqual } from "node:assert";
import { execFileSync } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { afterEach, beforeEach, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const script = join(
  dirname(fileURLToPath(import.meta.url)),
  "../.claude/tools/delete_job_branch.sh",
);

const CARD_BRANCH = "mikemindel/wb-9999";

function git(cwd, ...args) {
  return execFileSync(
    "git",
    ["-C", cwd, "-c", "user.email=t@t", "-c", "user.name=t", ...args],
    { encoding: "utf8" },
  ).trim();
}

function commitFile(repo, name, content) {
  writeFileSync(join(repo, name), content);
  git(repo, "add", name);
  git(repo, "commit", "-qm", `add ${name}`);
}

function run(worktree) {
  return execFileSync("bash", [script, CARD_BRANCH], {
    cwd: worktree,
    encoding: "utf8",
  }).trim();
}

describe("delete_job_branch.sh", () => {
  let dir;
  let origin;
  let main;
  let worktree;

  beforeEach(() => {
    dir = mkdtempSync(join(tmpdir(), "stride-delete-job-branch-"));
    origin = join(dir, "origin.git");
    main = join(dir, "main");
    worktree = join(dir, "job");
    execFileSync("git", ["init", "-q", "--bare", "-b", "main", origin]);
    execFileSync("git", ["clone", "-q", origin, main]);
    git(main, "checkout", "-q", "-B", "main");
    commitFile(main, "tracked.txt", "one");
    git(main, "push", "-q", "-u", "origin", "main");
    git(main, "worktree", "add", "-q", "-b", CARD_BRANCH, worktree, "main");
    commitFile(worktree, "card.txt", "the card's work");
  });

  afterEach(() => {
    rmSync(dir, { recursive: true, force: true });
  });

  function mergeCardOnGitHub() {
    git(worktree, "push", "-q", "origin", CARD_BRANCH);
    const other = join(dir, "merger");
    execFileSync("git", ["clone", "-q", origin, other]);
    git(other, "merge", "-q", "--no-ff", "-m", "merge", `origin/${CARD_BRANCH}`);
    git(other, "push", "-q", "origin", "main");
  }

  function branches() {
    return git(main, "branch", "--list", CARD_BRANCH);
  }

  it("detaches the worktree and deletes the branch once its work is on origin/main, though the main checkout lacks the merge", () => {
    mergeCardOnGitHub();
    const head = git(worktree, "rev-parse", "HEAD");
    strictEqual(run(worktree), "deleted");
    strictEqual(branches(), "");
    strictEqual(git(worktree, "rev-parse", "HEAD"), head);
    strictEqual(git(worktree, "branch", "--show-current"), "");
    strictEqual(git(worktree, "status", "--porcelain"), "");
  });

  it("lets the worktree be removed afterwards without force", () => {
    mergeCardOnGitHub();
    run(worktree);
    git(main, "worktree", "remove", worktree);
    strictEqual(branches(), "");
  });

  it("keeps a branch whose work isn't on origin/main", () => {
    const line = run(worktree);
    ok(line.startsWith("kept: "), line);
    ok(line.includes("not on origin/main"), line);
    strictEqual(branches().includes(CARD_BRANCH), true);
    strictEqual(git(worktree, "branch", "--show-current"), CARD_BRANCH);
  });

  it("reports deleted when the branch is already gone", () => {
    mergeCardOnGitHub();
    run(worktree);
    strictEqual(run(worktree), "deleted");
  });
});
