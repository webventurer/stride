import { ok, strictEqual } from "node:assert";
import {
  lstatSync,
  mkdirSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { after, beforeEach, describe, it } from "node:test";
import { codex } from "../install/agents/codex/index.mjs";
import { SKILLS_ROOT } from "../install/agents/codex/skills.mjs";

const srcRoot = join("/tmp", `stride-codex-src-${process.pid}`);
const destRoot = join("/tmp", `stride-codex-dest-${process.pid}`);
const SKILL = "vision";
const skillFile = join(destRoot, SKILLS_ROOT, SKILL, "SKILL.md");

function write(path, content) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content);
}

beforeEach(() => {
  for (const root of [srcRoot, destRoot]) {
    rmSync(root, { recursive: true, force: true });
  }
  write(join(srcRoot, ".claude/skills", SKILL, "SKILL.md"), "# Vision\n");
  mkdirSync(join(destRoot, ".claude/commands/linear"), { recursive: true });
  mkdirSync(join(destRoot, SKILLS_ROOT), { recursive: true });
});
after(() => {
  for (const root of [srcRoot, destRoot]) {
    rmSync(root, { recursive: true, force: true });
  }
});

describe("codex.install with a dangling skill symlink", () => {
  it("replaces the dead link with the real skill files", () => {
    symlinkSync("/nowhere/that/exists", join(destRoot, SKILLS_ROOT, SKILL));

    codex.install({ srcRoot, destRoot, skills: [SKILL] });

    ok(!lstatSync(join(destRoot, SKILLS_ROOT, SKILL)).isSymbolicLink());
    strictEqual(readFileSync(skillFile, "utf8"), "# Vision\n");
  });

  it("leaves a live symlink alone", () => {
    const target = join(destRoot, "elsewhere", SKILL);
    write(join(target, "SKILL.md"), "# Vision\n");
    symlinkSync(target, join(destRoot, SKILLS_ROOT, SKILL));

    codex.install({ srcRoot, destRoot, skills: [SKILL] });

    ok(lstatSync(join(destRoot, SKILLS_ROOT, SKILL)).isSymbolicLink());
  });
});
