import { deepStrictEqual, ok, strictEqual } from "node:assert";
import { execSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { after, beforeEach, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const strideRoot = join(__dirname, "..");
const fixtureRoot = join("/tmp", `stride-targets-${process.pid}`);

// Prompts in order: gitignore (y), settings merge (n).
function runInstall(args = "") {
  execSync(`node ${join(strideRoot, "bin/install.mjs")} ${args}`, {
    cwd: fixtureRoot,
    input: "y\nn\n",
    stdio: ["pipe", "pipe", "pipe"],
  });
}

function codexSkills() {
  const dir = join(fixtureRoot, ".codex/skills");
  return existsSync(dir) ? readdirSync(dir).sort() : [];
}

function gitignore() {
  return readFileSync(join(fixtureRoot, ".gitignore"), "utf8");
}

beforeEach(() => {
  rmSync(fixtureRoot, { recursive: true, force: true });
  mkdirSync(fixtureRoot, { recursive: true });
});
after(() => rmSync(fixtureRoot, { recursive: true, force: true }));

describe("install targets", () => {
  it("writes no Codex footprint by default", () => {
    runInstall();

    ok(existsSync(join(fixtureRoot, ".claude/commands/linear")));
    strictEqual(existsSync(join(fixtureRoot, ".codex")), false);
  });

  it("installs the shipped skills and command skills for Codex", () => {
    runInstall("--agent codex");

    const names = codexSkills();
    for (const skill of ["commit", "craft", "vision", "clear-speak"]) {
      ok(names.includes(skill), `expected ${skill} in .codex/skills/`);
    }
    ok(
      names.includes("linear-start"),
      "expected the rendered linear-start command skill",
    );
  });

  it("keeps the authoring source so Codex skills can point at it", () => {
    runInstall("--agent codex");

    const skill = readFileSync(
      join(fixtureRoot, ".codex/skills/linear-start/SKILL.md"),
      "utf8",
    );
    ok(skill.includes(".claude/commands/linear/start.md"));
    ok(existsSync(join(fixtureRoot, ".claude/commands/linear/start.md")));
  });

  it("sets up both targets with --agent all", () => {
    runInstall("--agent all");

    ok(existsSync(join(fixtureRoot, ".claude/skills/commit")));
    ok(codexSkills().includes("commit"));
  });

  it("gitignores the generated Codex tree only when Codex is selected", () => {
    runInstall();
    strictEqual(gitignore().includes(".codex/skills/"), false);

    rmSync(fixtureRoot, { recursive: true, force: true });
    mkdirSync(fixtureRoot, { recursive: true });
    runInstall("--agent codex");
    ok(gitignore().includes(".codex/skills/"));
  });

  it("leaves an existing skill with matching content alone", () => {
    const dest = join(fixtureRoot, ".codex/skills/commit/SKILL.md");
    const src = join(strideRoot, ".claude/skills/commit/SKILL.md");
    mkdirSync(dirname(dest), { recursive: true });
    writeFileSync(dest, readFileSync(src));
    const before = readFileSync(dest, "utf8");

    runInstall("--agent codex");

    strictEqual(readFileSync(dest, "utf8"), before);
  });

  it("refuses an unknown agent", () => {
    let failed = false;
    try {
      runInstall("--agent gemini");
    } catch (err) {
      failed = true;
      ok(err.stderr.toString().includes("gemini"));
    }
    ok(failed, "install should exit non-zero for an unknown agent");
  });
});

describe("uninstall targets", () => {
  it("removes the generated Codex tree", () => {
    runInstall("--agent codex");
    ok(codexSkills().length > 0);

    execSync(`node ${join(strideRoot, "bin/uninstall.mjs")}`, {
      cwd: fixtureRoot,
      stdio: ["pipe", "pipe", "pipe"],
    });

    deepStrictEqual(codexSkills(), []);
  });
});
