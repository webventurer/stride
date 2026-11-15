import { strictEqual } from "node:assert";
import { execFileSync } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { afterEach, beforeEach, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const script = join(
  dirname(fileURLToPath(import.meta.url)),
  "../.claude/tools/main_checkout_update.sh",
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

function check(main) {
  return execFileSync("bash", [script, main, CARD_BRANCH], {
    encoding: "utf8",
  }).trim();
}

function snapshot(main) {
  return [
    git(main, "branch", "--show-current"),
    git(main, "rev-parse", "HEAD"),
    git(main, "rev-parse", "main"),
    git(main, "status", "--porcelain"),
  ].join("\n");
}

describe("main_checkout_update.sh", () => {
  let dir;
  let main;

  beforeEach(() => {
    dir = mkdtempSync(join(tmpdir(), "stride-main-update-"));
    const origin = join(dir, "origin.git");
    main = join(dir, "main");
    execFileSync("git", ["init", "-q", "--bare", "-b", "main", origin]);
    execFileSync("git", ["clone", "-q", origin, main]);
    git(main, "checkout", "-q", "-B", "main");
    commitFile(main, "tracked.txt", "one");
    git(main, "push", "-q", "-u", "origin", "main");
  });

  afterEach(() => {
    rmSync(dir, { recursive: true, force: true });
  });

  function leaves(expectedLine) {
    const before = snapshot(main);
    strictEqual(check(main), expectedLine);
    strictEqual(snapshot(main), before);
  }

  it("updates a clean checkout on main", () => {
    strictEqual(check(main), "updated");
  });

  it("updates a clean checkout on the finishing card's own branch", () => {
    git(main, "switch", "-q", "-c", CARD_BRANCH);
    strictEqual(check(main), "updated");
  });

  it("does not count files git ignores", () => {
    writeFileSync(join(main, ".gitignore"), "scratch.txt\n");
    git(main, "add", ".gitignore");
    git(main, "commit", "-qm", "ignore scratch");
    git(main, "push", "-q");
    writeFileSync(join(main, "scratch.txt"), "noise");
    strictEqual(check(main), "updated");
  });

  it("leaves an uncommitted change", () => {
    writeFileSync(join(main, "tracked.txt"), "edited");
    leaves("left: uncommitted changes");
  });

  it("leaves a staged change", () => {
    writeFileSync(join(main, "tracked.txt"), "edited");
    git(main, "add", "tracked.txt");
    leaves("left: uncommitted changes");
  });

  it("leaves an untracked file", () => {
    writeFileSync(join(main, "new.txt"), "new");
    leaves("left: uncommitted changes");
  });

  it("leaves local main commits that GitHub lacks", () => {
    commitFile(main, "local.txt", "local");
    leaves("left: unpushed commits");
  });

  it("leaves a clean checkout on another branch", () => {
    git(main, "switch", "-q", "-c", "other");
    leaves("left: on branch other");
  });

  it("leaves a detached HEAD", () => {
    git(main, "checkout", "-q", "--detach");
    leaves("left: detached HEAD");
  });

  it("leaves the checkout when the fetch fails", () => {
    git(main, "remote", "set-url", "origin", join(dir, "missing.git"));
    leaves("left: the fetch failed");
  });
});
