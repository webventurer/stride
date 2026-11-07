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
});
