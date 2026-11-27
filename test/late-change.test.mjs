import { strictEqual, throws } from "node:assert";
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

  describe("given the checked change", () => {
    const unchanged = "no fresh check: the card's own change is as checked";
    const clash =
      "fresh check: the checked change doesn't replay cleanly on main";
    const lines = (edits = {}) =>
      Array.from({ length: 20 }, (_, i) => edits[i + 1] ?? `line ${i + 1}`)
        .join("\n")
        .concat("\n");

    function onMain(path, content) {
      git("switch", "-q", "main");
      write(path, content);
      commit();
      git("update-ref", "refs/remotes/origin/main", "HEAD");
      git("switch", "-q", "card");
    }

    function mergeMain() {
      git("merge", "-q", "--no-edit", "main");
    }

    beforeEach(() => {
      write("src/app.js", lines());
      write("src/run.py", "if ready:\n    load()\n    start()\n");
      commit();
      git("update-ref", "refs/remotes/origin/main", "HEAD");
      const base = git("rev-parse", "HEAD");
      git("switch", "-qc", "card");
      write("src/app.js", lines({ 10: "card" }));
      commit();
      checked = `${base}..${git("rev-parse", "HEAD^{tree}")}`;
    });

    it("sees no change on the branch as checked", () => {
      strictEqual(verdict(checked), unchanged);
    });

    it("sees none when main moved but the branch hasn't merged it", () => {
      onMain("src/other.js", "another card");
      strictEqual(verdict(checked), unchanged);
    });

    it("sees none after a merge that only brings in other files", () => {
      onMain("src/other.js", "another card");
      mergeMain();
      strictEqual(verdict(checked, "src/"), unchanged);
    });

    for (const line of [8, 12]) {
      it(`sees none after a clean merge that edits line ${line} beside the card's line 10`, () => {
        onMain("src/app.js", lines({ [line]: "main" }));
        mergeMain();
        strictEqual(verdict(checked), unchanged);
      });
    }

    it("sees none after a clean merge that renames a card file", () => {
      git("switch", "-q", "main");
      git("mv", "src/app.js", "src/main.js");
      git("commit", "-qm", "rename");
      git("update-ref", "refs/remotes/origin/main", "HEAD");
      git("switch", "-q", "card");
      mergeMain();
      strictEqual(verdict(checked), unchanged);
    });

    it("sees none when the same change is replayed on a newer base", () => {
      onMain("src/app.js", lines({ 1: "main" }));
      git("rebase", "-q", "main");
      strictEqual(verdict(checked), unchanged);
    });

    it("sees one line altered", () => {
      write("src/app.js", lines({ 10: "card, altered" }));
      commit();
      strictEqual(
        verdict(checked),
        "fresh check: src/app.js is not a file that can skip it",
      );
    });

    it("sees a change of indentation alone", () => {
      write("src/run.py", "if ready:\n    load()\nstart()\n");
      commit();
      strictEqual(
        verdict(checked),
        "fresh check: src/run.py is not a file that can skip it",
      );
    });

    it("needs one after a clash resolved in a card file", () => {
      onMain("src/app.js", lines({ 10: "main" }));
      throws(mergeMain);
      write("src/app.js", lines({ 10: "main and card" }));
      commit();
      strictEqual(verdict(checked), clash);
    });

    it("needs one after a clash settled by keeping only the card's side", () => {
      onMain("src/app.js", lines({ 10: "main" }));
      throws(mergeMain);
      write("src/app.js", lines({ 10: "card" }));
      commit();
      strictEqual(verdict(checked), clash);
    });

    it("sees none after two clean merges that one replay would clash on", () => {
      onMain("src/app.js", lines({ 1: "main" }));
      mergeMain();
      onMain("src/app.js", lines({ 1: "main", 10: "card" }));
      mergeMain();
      onMain("src/app.js", lines({ 1: "main", 10: "main again" }));
      mergeMain();
      strictEqual(verdict(checked), unchanged);
    });

    it("needs one after a clash that main later reverted", () => {
      for (const line of ["main", "line 10"]) {
        onMain("src/app.js", lines({ 10: line }));
        throws(mergeMain);
        write("src/app.js", lines({ 10: "card" }));
        commit();
      }
      strictEqual(verdict(checked), clash);
    });

    it("counts what a merge of another branch brought in", () => {
      git("switch", "-qc", "helper", "main");
      change("src/helper.js");
      git("switch", "-q", "card");
      git("merge", "-q", "--no-edit", "helper");
      strictEqual(
        verdict(checked),
        "fresh check: src/helper.js is not a file that can skip it",
      );
    });

    describe("on a git too old to replay", () => {
      let bin;

      beforeEach(() => {
        bin = mkdtempSync(join(tmpdir(), "stride-old-git-"));
        const real = execFileSync("which", ["git"], {
          encoding: "utf8",
        }).trim();
        writeFileSync(
          join(bin, "git"),
          `#!/bin/sh\n[ "$1" = merge-tree ] && exit 129\nexec "${real}" "$@"\n`,
          { mode: 0o755 },
        );
      });

      afterEach(() => rmSync(bin, { recursive: true, force: true }));

      function oldGitVerdict() {
        return execFileSync("bash", [script, checked], {
          cwd: repo,
          encoding: "utf8",
          env: { ...process.env, PATH: `${bin}:${process.env.PATH}` },
        }).trim();
      }

      it("sees no change on an untouched branch", () => {
        strictEqual(oldGitVerdict(), unchanged);
      });

      it("needs one once the branch has moved", () => {
        change("docs/guide.md");
        strictEqual(oldGitVerdict(), clash);
      });
    });

    it("judges only late files after a merge that brought in code", () => {
      onMain("src/other.js", "another card");
      mergeMain();
      change("docs/guide.md");
      strictEqual(verdict(checked), "no fresh check: docs/guide.md");
      strictEqual(
        verdict(checked, "docs/"),
        "fresh check: docs/guide.md is named by a promise",
      );
    });

    for (const [part, broken] of [
      ["base", (tree) => `${"0".repeat(40)}..${tree}`],
      ["tree", (_, base) => `${base}..${"0".repeat(40)}`],
    ]) {
      it(`needs one when the checked ${part} can't be read`, () => {
        const [base, tree] = checked.split("..");
        strictEqual(
          verdict(broken(tree, base)),
          "fresh check: the checked change can't be read",
        );
      });
    }

    it("needs one when origin's main can't be found", () => {
      change("docs/guide.md");
      git("update-ref", "-d", "refs/remotes/origin/main");
      strictEqual(verdict(checked), clash);
    });
  });
});
