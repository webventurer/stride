import { ok, strictEqual } from "node:assert";
import { execFileSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  realpathSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { afterEach, beforeEach, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const tools = join(dirname(fileURLToPath(import.meta.url)), "../.claude/tools");
const removeScript = join(tools, "remove_card_worktree.sh");

function git(cwd, ...args) {
  return execFileSync("git", ["-C", cwd, ...args], { encoding: "utf8" });
}

function makeRepo(root, gitignore) {
  mkdirSync(root, { recursive: true });
  git(root, "init", "-q", "-b", "main");
  writeFileSync(join(root, ".gitignore"), gitignore);
  writeFileSync(join(root, "README.md"), "x");
  git(root, "add", ".");
  git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init");
}

function run(script, ...args) {
  return execFileSync(script, args, { encoding: "utf8", stdio: "pipe" });
}

function worktreeListed(mainRepo, path) {
  return git(mainRepo, "worktree", "list", "--porcelain").includes(path);
}

describe("worktree place", () => {
  let base;
  let mainRepo;

  beforeEach(() => {
    base = realpathSync(mkdtempSync(join(tmpdir(), "stride-place-")));
    mainRepo = join(base, "app");
  });

  afterEach(() => {
    rmSync(base, { recursive: true, force: true });
  });

  describe("teardown", () => {
    it("removes a worktree in .claude/worktrees, found by its branch", () => {
      makeRepo(mainRepo, ".claude/worktrees/\n");
      const path = join(mainRepo, ".claude/worktrees/wb-1");
      git(mainRepo, "worktree", "add", "-q", path, "-b", "wb-1");

      const output = run(removeScript, mainRepo, "wb-1");

      ok(!existsSync(path));
      strictEqual(output.trim(), path);
    });

    it("removes a worktree beside the repo, found by its branch", () => {
      makeRepo(mainRepo, ".claude/worktrees/\n");
      const path = join(base, "app-wb-1");
      git(mainRepo, "worktree", "add", "-q", path, "-b", "wb-1");

      run(removeScript, mainRepo, "wb-1");

      ok(!existsSync(path));
      ok(!worktreeListed(mainRepo, path));
    });

    it("prunes a worktree whose folder is gone, so the branch can be deleted", () => {
      makeRepo(mainRepo, ".claude/worktrees/\n");
      const path = join(base, "app-wb-1");
      git(mainRepo, "worktree", "add", "-q", path, "-b", "wb-1");
      rmSync(path, { recursive: true, force: true });

      run(removeScript, mainRepo, "wb-1");
      git(mainRepo, "branch", "-d", "wb-1");

      ok(!worktreeListed(mainRepo, path));
    });

    it("skips silently when no worktree has the branch", () => {
      makeRepo(mainRepo, ".claude/worktrees/\n");
      git(mainRepo, "branch", "wb-1");

      strictEqual(run(removeScript, mainRepo, "wb-1"), "");
    });
  });
});
