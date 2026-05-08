import { match, notStrictEqual, ok, strictEqual } from "node:assert";
import { execSync } from "node:child_process";
import { existsSync, mkdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { after, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const strideRoot = join(__dirname, "..");
const fixtureRoot = join("/tmp", `stride-cwd-guard-${process.pid}`);

function runInstallFrom(cwd) {
  try {
    execSync(`node ${join(strideRoot, "bin/install.mjs")}`, {
      cwd,
      input: "",
      stdio: ["pipe", "pipe", "pipe"],
    });
    return null;
  } catch (err) {
    return { status: err.status, stderr: err.stderr.toString() };
  }
}

describe("install cwd guard", () => {
  after(() => rmSync(fixtureRoot, { recursive: true, force: true }));

  it("refuses to install when cwd is inside a .claude/ ancestor", () => {
    rmSync(fixtureRoot, { recursive: true, force: true });
    const claudeSubdir = join(fixtureRoot, ".claude/skills");
    mkdirSync(claudeSubdir, { recursive: true });

    const result = runInstallFrom(claudeSubdir);

    notStrictEqual(result, null, "install should exit non-zero");
    strictEqual(result.status, 1);
    match(result.stderr, /inside a \.claude\/ directory/);
    ok(
      !existsSync(join(claudeSubdir, ".claude")),
      "no nested .claude/ should be created",
    );
  });

  it("refuses when cwd is the .claude/ directory itself", () => {
    rmSync(fixtureRoot, { recursive: true, force: true });
    const claudeDir = join(fixtureRoot, ".claude");
    mkdirSync(claudeDir, { recursive: true });

    const result = runInstallFrom(claudeDir);

    notStrictEqual(result, null);
    strictEqual(result.status, 1);
    match(result.stderr, /inside a \.claude\/ directory/);
  });
});
