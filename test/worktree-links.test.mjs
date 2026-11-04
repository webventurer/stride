import { deepStrictEqual, ok, strictEqual } from "node:assert";
import { execFileSync } from "node:child_process";
import {
  lstatSync,
  mkdirSync,
  mkdtempSync,
  readlinkSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { afterEach, beforeEach, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const linkScript = join(
  dirname(fileURLToPath(import.meta.url)),
  "../.claude/tools/link_stride_install.sh",
);

const strideSection = [
  "# >>> stride (auto-managed, do not edit) >>>",
  ".claude/commands/linear/",
  ".claude/stride/docs/concepts/",
  ".claude/tools/",
  ".codex/skills/",
  "# <<< stride <<<",
].join("\n");

function git(cwd, ...args) {
  return execFileSync("git", ["-C", cwd, ...args], { encoding: "utf8" });
}

function writeFile(root, path, text = "x") {
  mkdirSync(dirname(join(root, path)), { recursive: true });
  writeFileSync(join(root, path), text);
}

function makeRepo(root, gitignore) {
  mkdirSync(root);
  git(root, "init", "-q", "-b", "main");
  writeFile(root, ".gitignore", gitignore);
  writeFile(root, "README.md");
  git(root, "add", ".");
  git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init");
}

function runLinking(mainRepo, worktree) {
  return execFileSync(linkScript, [mainRepo, worktree], { encoding: "utf8" });
}

describe("worktree linking step", () => {
  let base;
  let mainRepo;
  let worktree;

  beforeEach(() => {
    base = mkdtempSync(join(tmpdir(), "stride-worktree-"));
    mainRepo = join(base, "app");
    worktree = join(base, "app-wb-1");
  });

  afterEach(() => {
    rmSync(base, { recursive: true, force: true });
  });

  it("links every stride path, the settings file and the venv", () => {
    makeRepo(mainRepo, `.venv/\n.claude/settings.local.json\n${strideSection}\n`);
    for (const path of [
      ".claude/commands/linear/start.md",
      ".claude/stride/docs/concepts/a.md",
      ".claude/tools/linear_cli.py",
      ".codex/skills/commit/SKILL.md",
      ".claude/settings.local.json",
      ".venv/bin/python",
    ]) {
      writeFile(mainRepo, path);
    }
    git(mainRepo, "worktree", "add", "-q", worktree, "-b", "wb-1");

    const output = runLinking(mainRepo, worktree);

    for (const path of [
      ".claude/commands/linear",
      ".claude/stride/docs/concepts",
      ".claude/tools",
      ".codex/skills",
      ".claude/settings.local.json",
      ".venv",
    ]) {
      ok(lstatSync(join(worktree, path)).isSymbolicLink(), path);
      strictEqual(readlinkSync(join(worktree, path)), join(mainRepo, path));
    }
    strictEqual(git(worktree, "status", "--porcelain"), "");
    strictEqual(output.trim().split("\n").length, 1);
  });

  it("links into a worktree inside .claude/worktrees", () => {
    makeRepo(mainRepo, `.claude/worktrees/\n${strideSection}\n`);
    writeFile(mainRepo, ".claude/tools/linear_cli.py");
    const inside = join(mainRepo, ".claude/worktrees/wb-1");
    git(mainRepo, "worktree", "add", "-q", inside, "-b", "wb-1");

    runLinking(mainRepo, inside);

    strictEqual(
      readlinkSync(join(inside, ".claude/tools")),
      join(mainRepo, ".claude/tools"),
    );
    strictEqual(git(inside, "status", "--porcelain"), "");
  });

  it("leaves a path the branch tracks alone", () => {
    makeRepo(mainRepo, `${strideSection}\n`);
    writeFile(mainRepo, ".claude/tools/linear_cli.py", "tracked");
    git(mainRepo, "add", "-f", ".claude/tools/linear_cli.py");
    git(mainRepo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "tools");
    git(mainRepo, "worktree", "add", "-q", worktree, "-b", "wb-1");

    runLinking(mainRepo, worktree);

    ok(!lstatSync(join(worktree, ".claude/tools")).isSymbolicLink());
    strictEqual(git(worktree, "status", "--porcelain"), "");
  });

  it("prints nothing when there is nothing to link", () => {
    makeRepo(mainRepo, "node_modules/\n");
    git(mainRepo, "worktree", "add", "-q", worktree, "-b", "wb-1");

    const output = runLinking(mainRepo, worktree);

    deepStrictEqual(output, "");
  });
});
