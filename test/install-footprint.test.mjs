import { strictEqual } from "node:assert";
import { execSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, join, relative } from "node:path";
import { after, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const strideRoot = join(__dirname, "..");
const fixtureRoot = join("/tmp", `stride-footprint-${process.pid}`);

const SENTINELS = {
  "tools/format-mdx.sh": "consumer tool — must not change",
  "tools/remark/parse.mjs": "consumer remark plugin",
  "src/app.mjs": "consumer app code",
  "docs/README.md": "consumer docs",
  "package.json": '{"name":"consumer"}',
  ".env.example": "consumer env template",
  ".gitignore": "node_modules\n",
};

function seedFixture() {
  rmSync(fixtureRoot, { recursive: true, force: true });
  for (const [path, content] of Object.entries(SENTINELS)) {
    const full = join(fixtureRoot, path);
    mkdirSync(dirname(full), { recursive: true });
    writeFileSync(full, content);
  }
}

function runInstall({ gitignore = "n" } = {}) {
  // Prompts in order: gitignore, settings merge (n).
  const input = `${gitignore}\nn\n`;
  execSync(`node ${join(strideRoot, "bin/install.mjs")}`, {
    cwd: fixtureRoot,
    input,
    stdio: ["pipe", "pipe", "pipe"],
  });
}

function walk(dir, base = dir) {
  const paths = [];
  for (const entry of readdirSync(dir)) {
    if (entry === ".claude") continue;
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) paths.push(...walk(full, base));
    else paths.push(relative(base, full));
  }
  return paths;
}

describe("install footprint", () => {
  after(() => rmSync(fixtureRoot, { recursive: true, force: true }));

  it("does not modify or delete files outside .claude/", () => {
    seedFixture();
    runInstall();

    for (const [path, expected] of Object.entries(SENTINELS)) {
      const actual = readFileSync(join(fixtureRoot, path), "utf8");
      strictEqual(actual, expected, `sentinel changed: ${path}`);
    }
  });

  it("does not create any new files outside .claude/", () => {
    seedFixture();
    runInstall();

    const after = new Set(walk(fixtureRoot));
    const expected = new Set(Object.keys(SENTINELS));
    for (const path of after) {
      strictEqual(expected.has(path), true, `unexpected file: ${path}`);
    }
    strictEqual(
      after.size,
      expected.size,
      "file count changed outside .claude/",
    );
  });

  it("creates the expected .claude/ subdirs", () => {
    seedFixture();
    runInstall();

    const claudeDir = join(fixtureRoot, ".claude");
    strictEqual(existsSync(join(claudeDir, "skills/commit")), true);
    strictEqual(
      existsSync(join(claudeDir, "skills/clear-speak/SKILL.md")),
      true,
    );
    strictEqual(existsSync(join(claudeDir, "commands/linear")), true);
    strictEqual(existsSync(join(claudeDir, "hooks")), true);
    strictEqual(existsSync(join(claudeDir, "tools/openrouter_cli.py")), true);
  });

  it("installs /parallel-sessions without its tests", () => {
    seedFixture();
    runInstall();

    const skill = join(fixtureRoot, ".claude/skills/parallel-sessions");
    for (const file of [
      "SKILL.md",
      "BRIEF.md",
      "reference/chain-of-command.md",
      "reference/chain-of-command.pdf",
      "reference/chain-of-command-config.md",
      "reference/model-costs.md",
      "reference/testing-the-chain-of-command.md",
      "scripts/slots.py",
      "scripts/measure_run.py",
    ]) {
      strictEqual(existsSync(join(skill, file)), true, file);
    }
    strictEqual(existsSync(join(skill, "scripts/tests")), false);
  });

  it("installs /parallel-sessions naming no codefu page, every link opening", () => {
    seedFixture();
    runInstall();

    const skill = join(fixtureRoot, ".claude/skills/parallel-sessions");
    for (const file of walk(skill).filter((path) => path.endsWith(".md"))) {
      const text = readFileSync(join(skill, file), "utf8");
      strictEqual(/codefu/i.test(text), false, `${file} names codefu`);
      for (const [, target] of text.matchAll(/\]\(([^)#\s]+)/g)) {
        if (target.startsWith("http")) continue;
        const resolved = join(skill, dirname(file), target);
        strictEqual(existsSync(resolved), true, `${file} -> ${target}`);
      }
    }
  });

  it("does not ship stride's own test files", () => {
    seedFixture();
    runInstall();

    const claudeDir = join(fixtureRoot, ".claude");
    strictEqual(existsSync(join(claudeDir, "tools/tests")), false);
  });

  it("writes the stride section to .gitignore when accepted", () => {
    seedFixture();
    runInstall({ gitignore: "y" });

    const gitignore = readFileSync(join(fixtureRoot, ".gitignore"), "utf8");
    strictEqual(
      gitignore.includes("# >>> stride (auto-managed, do not edit) >>>"),
      true,
    );
    strictEqual(gitignore.includes("# <<< stride <<<"), true);
    strictEqual(gitignore.includes(".claude/tools/"), true);
    strictEqual(gitignore.includes(".claude/stride/"), true);
    strictEqual(
      gitignore.includes(
        ".claude/hooks/userpromptsubmit/inject_design_principles.sh",
      ),
      true,
    );
  });

  it("ignores .claude/worktrees/ once, however often stride installs", () => {
    seedFixture();
    runInstall({ gitignore: "y" });
    runInstall({ gitignore: "y" });

    const gitignore = readFileSync(join(fixtureRoot, ".gitignore"), "utf8");
    strictEqual(gitignore.match(/^\.claude\/worktrees\/$/gm)?.length, 1);
  });

  it("leaves .claude/worktrees/ out when the .gitignore prompt is declined", () => {
    seedFixture();
    runInstall({ gitignore: "n" });

    const gitignore = readFileSync(join(fixtureRoot, ".gitignore"), "utf8");
    strictEqual(gitignore.includes(".claude/worktrees/"), false);
  });

  it("adds no second .claude/worktrees/ when the repo already ignores it", () => {
    seedFixture();
    writeFileSync(
      join(fixtureRoot, ".gitignore"),
      "node_modules\n.claude/worktrees/\n",
    );

    runInstall({ gitignore: "y" });

    const gitignore = readFileSync(join(fixtureRoot, ".gitignore"), "utf8");
    strictEqual(gitignore.match(/^\.claude\/worktrees\/$/gm)?.length, 1);
  });

  it("preserves existing .gitignore entries when adding the stride section", () => {
    seedFixture();
    runInstall({ gitignore: "y" });

    const gitignore = readFileSync(join(fixtureRoot, ".gitignore"), "utf8");
    strictEqual(gitignore.includes("node_modules"), true);
  });

  it("replaces an existing stride section rather than duplicating", () => {
    seedFixture();
    const existing = `node_modules\n\n# >>> stride (auto-managed, do not edit) >>>\n.claude/old-entry/\n# <<< stride <<<\n`;
    writeFileSync(join(fixtureRoot, ".gitignore"), existing);

    runInstall({ gitignore: "y" });

    const gitignore = readFileSync(join(fixtureRoot, ".gitignore"), "utf8");
    const matches = gitignore.match(/# >>> stride/g);
    strictEqual(matches?.length, 1, "stride section should not duplicate");
    strictEqual(gitignore.includes(".claude/old-entry/"), false);
    strictEqual(gitignore.includes(".claude/tools/"), true);
    strictEqual(gitignore.includes("node_modules"), true);
  });
});
