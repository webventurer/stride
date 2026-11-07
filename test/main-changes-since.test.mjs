import { ok, strictEqual } from "node:assert";
import { execFileSync } from "node:child_process";
import {
  chmodSync,
  mkdirSync,
  mkdtempSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { afterEach, beforeEach, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const script = join(
  dirname(fileURLToPath(import.meta.url)),
  "../.claude/tools/main_changes_since.sh",
);

function git(cwd, ...args) {
  return execFileSync("git", ["-C", cwd, ...args], { encoding: "utf8" }).trim();
}

function commit(repo, subject, date) {
  writeFileSync(join(repo, `${subject}.txt`), subject);
  git(repo, "add", ".");
  execFileSync(
    "git",
    [
      "-C",
      repo,
      "-c",
      "user.email=t@t",
      "-c",
      "user.name=t",
      "commit",
      "-qm",
      subject,
    ],
    {
      env: { ...process.env, GIT_AUTHOR_DATE: date, GIT_COMMITTER_DATE: date },
    },
  );
  return git(repo, "rev-parse", "HEAD");
}

function fakeGh(dir, events) {
  const gh = join(dir, "gh");
  writeFileSync(
    gh,
    `#!/bin/bash\ncat <<'JSON'\n${JSON.stringify(events)}\nJSON\n`,
  );
  chmodSync(gh, 0o755);
}

describe("main_changes_since.sh", () => {
  let base;
  let repo;
  let bin;
  let first;
  let pushedLate;

  beforeEach(() => {
    base = mkdtempSync(join(tmpdir(), "stride-main-changes-"));
    repo = join(base, "repo");
    bin = join(base, "bin");
    mkdirSync(bin);
    execFileSync("git", [
      "init",
      "-q",
      "--bare",
      "-b",
      "main",
      join(base, "origin.git"),
    ]);
    execFileSync("git", ["clone", "-q", join(base, "origin.git"), repo], {
      stdio: "ignore",
    });
    first = commit(repo, "first", "2026-11-07T08:00:00Z");
    git(repo, "push", "-q", "origin", "HEAD:main");
    pushedLate = commit(repo, "made-early-pushed-late", "2026-11-07T09:00:00Z");
    git(repo, "push", "-q", "origin", "HEAD:main");
    fakeGh(bin, [
      { timestamp: "2026-11-07T12:00:00Z", before: first, after: pushedLate },
      {
        timestamp: "2026-11-07T08:00:00Z",
        before: "0".repeat(40),
        after: first,
      },
    ]);
  });

  afterEach(() => rmSync(base, { recursive: true, force: true }));

  function run(since) {
    return execFileSync(script, [since], {
      cwd: repo,
      encoding: "utf8",
      env: { ...process.env, PATH: `${bin}:${process.env.PATH}` },
    });
  }

  it("lists a commit by when it reached main, not the date it carries", () => {
    const listed = run("2026-11-07T10:00:00.000Z");

    ok(listed.includes("made-early-pushed-late"));
    ok(!listed.includes(" first"));
  });

  it("lists nothing when nothing reached main since the time", () => {
    strictEqual(run("2026-11-07T13:00:00.000Z"), "");
  });
});
