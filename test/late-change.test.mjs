import { strictEqual } from "node:assert";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { afterEach, beforeEach, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const script = join(
  dirname(fileURLToPath(import.meta.url)),
  "../.claude/tools/late_change.sh",
);

describe("late_change.sh", () => {
  let repo;
  let checked;

  function git(...args) {
    return execFileSync(
      "git",
      ["-C", repo, "-c", "user.email=t@t", "-c", "user.name=t", ...args],
      { encoding: "utf8" },
    ).trim();
  }

  function write(path, content) {
    mkdirSync(join(repo, dirname(path)), { recursive: true });
    writeFileSync(join(repo, path), content);
  }

  function commit() {
    git("add", "-A");
    git("commit", "-qm", "change");
  }

  function change(...paths) {
    for (const path of paths) write(path, "after");
    commit();
  }

  function verdict(...args) {
    return execFileSync("bash", [script, ...args], {
      cwd: repo,
      encoding: "utf8",
    }).trim();
  }

  beforeEach(() => {
    repo = mkdtempSync(join(tmpdir(), "stride-late-change-"));
    git("init", "-q", "-b", "main");
    write("VISION.md", "before");
    write("docs/guide.md", "before");
    write("src/app.js", "before");
    commit();
    checked = git("rev-parse", "HEAD^{tree}");
  });

  afterEach(() => {
    rmSync(repo, { recursive: true, force: true });
  });

  it("needs no fresh check when nothing changed", () => {
    strictEqual(verdict(checked), "no fresh check: no file changed");
  });

  it("needs none for a Vision line", () => {
    change("VISION.md");
    strictEqual(verdict(checked), "no fresh check: VISION.md");
  });

  it("needs none for unpromised docs, naming each", () => {
    change("README.md", "docs/guide.md", "docs/skills/nested page.md");
    strictEqual(
      verdict(checked, "src/app.js"),
      "no fresh check: README.md, docs/guide.md, docs/skills/nested page.md",
    );
  });

  for (const path of [
    "src/app.js",
    "test/app.test.mjs",
    "package.json",
    ".claude/commands/linear/finish.md",
    "CLAUDE.md",
    "AGENTS.md",
    "docs/.vitepress/config.mjs",
    "docs/CLAUDE.md",
    "docs/guides/AGENTS.md",
    "docs/.claude/commands/deploy.md",
    "src/README.md",
    "src/docs/page.md",
    "notes.txt",
  ]) {
    it(`needs one for ${path}, even beside a harmless change`, () => {
      change("VISION.md", path);
      strictEqual(
        verdict(checked),
        `fresh check: ${path} is not a file that can skip it`,
      );
    });
  }

  for (const promised of ["docs/guide.md", "./docs/guide.md", "docs/"]) {
    it(`needs one when a promise names ${promised}`, () => {
      change("docs/guide.md");
      strictEqual(
        verdict(checked, "VISION.md", promised),
        "fresh check: docs/guide.md is named by a promise",
      );
    });
  }

  it("needs one when a code file moves into docs", () => {
    git("mv", "src/app.js", "docs/app.md");
    commit();
    strictEqual(
      verdict(checked),
      "fresh check: src/app.js is not a file that can skip it",
    );
  });

  it("needs one when the checked tree can't be read", () => {
    change("VISION.md");
    strictEqual(
      verdict("0123456789012345678901234567890123456789"),
      "fresh check: the checked tree can't be read",
    );
  });
});
