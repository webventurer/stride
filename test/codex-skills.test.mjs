import { deepStrictEqual, match, strictEqual, throws } from "node:assert";
import {
  mkdirSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { after, beforeEach, describe, it } from "node:test";
import {
  COMMANDS_ROOT,
  renderCodexSkills,
  SKILLS_ROOT,
} from "../bin/codex-skills.mjs";

const fixtureRoot = join("/tmp", `stride-codex-skills-${process.pid}`);
const skillsDir = join(fixtureRoot, SKILLS_ROOT);

const COMMANDS = {
  "start.md":
    "---\ndescription: Implement a Linear issue and open a PR.\n---\n\n# Start work on a Linear issue\n",
  "finish.md":
    "---\ndescription: Merge the PR and close the Linear issue.\n---\n\n# Finish issue\n",
  "reference/workflow.md": "# Linear workflow\n",
  "recovery/backfill-focus-field.md": "# Backfill focus\n",
  "linear_statuses.json": "{}\n",
};

function seed(files) {
  rmSync(fixtureRoot, { recursive: true, force: true });
  for (const [path, content] of Object.entries(files)) {
    const full = join(fixtureRoot, COMMANDS_ROOT, "linear", path);
    mkdirSync(dirname(full), { recursive: true });
    writeFileSync(full, content);
  }
}

function skillBody(name) {
  return readFileSync(join(skillsDir, name, "SKILL.md"), "utf8");
}

beforeEach(() => seed(COMMANDS));
after(() => rmSync(fixtureRoot, { recursive: true, force: true }));

describe("renderCodexSkills", () => {
  it("emits one skill per top-level command, skipping subdirectories", () => {
    const written = renderCodexSkills(fixtureRoot);

    deepStrictEqual(written, ["linear-finish", "linear-start"]);
    deepStrictEqual(readdirSync(skillsDir).sort(), written);
  });

  it("carries the name and the source description as frontmatter", () => {
    renderCodexSkills(fixtureRoot);

    match(
      skillBody("linear-start"),
      /^---\nname: linear-start\ndescription: Implement a Linear issue and open a PR\.\n---\n/,
    );
  });

  it("points at the canonical command file rather than copying its body", () => {
    renderCodexSkills(fixtureRoot);
    const body = skillBody("linear-start");

    match(body, /\.claude\/commands\/linear\/start\.md/);
    strictEqual(body.includes("# Start work on a Linear issue"), false);
  });

  it("rewrites identical output when run again", () => {
    renderCodexSkills(fixtureRoot);
    const first = skillBody("linear-start");

    renderCodexSkills(fixtureRoot);

    strictEqual(skillBody("linear-start"), first);
  });

  it("throws when a command has no frontmatter description", () => {
    seed({ ...COMMANDS, "quick.md": "# Quick\n" });

    throws(() => renderCodexSkills(fixtureRoot), /quick\.md/);
  });
});
