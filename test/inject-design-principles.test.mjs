import { strictEqual } from "node:assert";
import { execFileSync, execSync } from "node:child_process";
import {
  mkdirSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { after, before, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const strideRoot = join(__dirname, "..");
const fixtureRoot = join("/tmp", `stride-design-principles-${process.pid}`);
const HOOK_PATH = ".claude/hooks/userpromptsubmit/inject_design_principles.sh";
const hook = join(fixtureRoot, HOOK_PATH);
const worktreeRoot = `${fixtureRoot}-worktree`;
const worktreeDoc =
  "design-decisions text found under the worktree's own root\n";
const doc = readFileSync(
  join(strideRoot, ".claude/stride/docs/principles/design-decisions.md"),
  "utf8",
);

function injectedFrom(cwd) {
  const output = execFileSync(hook, {
    input: JSON.stringify({ cwd }),
    encoding: "utf8",
  });
  return JSON.parse(output).hookSpecificOutput.additionalContext;
}

before(() => {
  rmSync(fixtureRoot, { recursive: true, force: true });
  rmSync(worktreeRoot, { recursive: true, force: true });
  mkdirSync(join(fixtureRoot, "docs/guides"), { recursive: true });
  execSync(`node ${join(strideRoot, "bin/install.mjs")}`, {
    cwd: fixtureRoot,
    input: "n\nn\n",
    stdio: ["pipe", "pipe", "pipe"],
  });
});
after(() => {
  rmSync(fixtureRoot, { recursive: true, force: true });
  rmSync(worktreeRoot, { recursive: true, force: true });
});

describe("inject_design_principles hook", () => {
  it("injects the design-decisions document from the repo root", () => {
    strictEqual(injectedFrom(fixtureRoot), doc);
  });

  it("injects it when the shell sits in a subfolder", () => {
    strictEqual(injectedFrom(join(fixtureRoot, "docs")), doc);
  });

  it("injects it when the shell sits two folders down", () => {
    strictEqual(injectedFrom(join(fixtureRoot, "docs/guides")), doc);
  });

  it("injects it when the payload carries no cwd", () => {
    const output = execFileSync(hook, { input: "{}", encoding: "utf8" });

    strictEqual(JSON.parse(output).hookSpecificOutput.additionalContext, doc);
  });

  it("injects it by the relative path Codex registers, with no CLAUDE_PROJECT_DIR", () => {
    const { CLAUDE_PROJECT_DIR, ...env } = process.env;
    const output = execFileSync(HOOK_PATH, {
      cwd: fixtureRoot,
      env,
      input: JSON.stringify({ cwd: join(fixtureRoot, "docs") }),
      encoding: "utf8",
    });

    strictEqual(JSON.parse(output).hookSpecificOutput.additionalContext, doc);
  });

  it("injects the document under a worktree's own root when its hooks folder is linked", () => {
    mkdirSync(join(worktreeRoot, ".claude/stride/docs/principles"), {
      recursive: true,
    });
    symlinkSync(
      join(fixtureRoot, ".claude/hooks"),
      join(worktreeRoot, ".claude/hooks"),
    );
    writeFileSync(
      join(worktreeRoot, ".claude/stride/docs/principles/design-decisions.md"),
      worktreeDoc,
    );
    const output = execFileSync(join(worktreeRoot, HOOK_PATH), {
      input: JSON.stringify({ cwd: worktreeRoot }),
      encoding: "utf8",
    });

    strictEqual(
      JSON.parse(output).hookSpecificOutput.additionalContext,
      worktreeDoc,
    );
  });
});
