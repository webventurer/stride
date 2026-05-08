import { match, notStrictEqual, strictEqual } from "node:assert";
import { execSync } from "node:child_process";
import {
  cpSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { after, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const strideRoot = join(__dirname, "..");
const fixtureRoot = join("/tmp", `stride-symlink-prompt-${process.pid}`);
const SKILL_REL = ".claude/skills/commit";
const SKILL_FILE_REL = `${SKILL_REL}/SKILL.md`;

function resetFixture() {
  rmSync(fixtureRoot, { recursive: true, force: true });
  mkdirSync(fixtureRoot, { recursive: true });
}

function readStride(relPath) {
  return readFileSync(join(strideRoot, relPath), "utf8");
}

function readFixture(relPath) {
  return readFileSync(join(fixtureRoot, relPath), "utf8");
}

function setupDifferingSymlink() {
  const external = join(fixtureRoot, "external-tool/skills/commit");
  mkdirSync(external, { recursive: true });
  cpSync(join(strideRoot, SKILL_REL), external, { recursive: true });
  writeFileSync(
    join(external, "SKILL.md"),
    "external tool's different content",
  );
  const symlinkPath = join(fixtureRoot, SKILL_REL);
  mkdirSync(dirname(symlinkPath), { recursive: true });
  symlinkSync(external, symlinkPath);
  return { external, symlinkPath };
}

function runInstallWith(input) {
  return execSync(`node ${join(strideRoot, "bin/install.mjs")}`, {
    cwd: fixtureRoot,
    input,
    stdio: ["pipe", "pipe", "pipe"],
  });
}

function runInstallWithExpectFailure(input) {
  try {
    execSync(`node ${join(strideRoot, "bin/install.mjs")}`, {
      cwd: fixtureRoot,
      input,
      stdio: ["pipe", "pipe", "pipe"],
    });
    return null;
  } catch (err) {
    return { status: err.status, stderr: err.stderr.toString() };
  }
}

describe("install symlink prompt", () => {
  after(() => rmSync(fixtureRoot, { recursive: true, force: true }));

  it("prompts then replaces a symlinked skill with stride's copy on confirm", () => {
    resetFixture();
    const { external, symlinkPath } = setupDifferingSymlink();

    runInstallWith("y\nn\nnone\nn\n");

    strictEqual(lstatSync(symlinkPath).isSymbolicLink(), false);
    strictEqual(readFixture(SKILL_FILE_REL), readStride(SKILL_FILE_REL));
    strictEqual(
      readFileSync(join(external, "SKILL.md"), "utf8"),
      "external tool's different content",
      "external tool's content should be untouched",
    );
  });

  it("reports the conflict and exits when the user declines the overwrite", () => {
    resetFixture();
    const { symlinkPath } = setupDifferingSymlink();

    const result = runInstallWithExpectFailure("n\nn\nnone\nn\n");

    notStrictEqual(result, null, "install should exit with non-zero status");
    strictEqual(result.status, 1);
    match(result.stderr, /SKILL\.md/);
    strictEqual(lstatSync(symlinkPath).isSymbolicLink(), true);
  });
});
