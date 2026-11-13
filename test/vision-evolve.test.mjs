import { ok } from "node:assert";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";
import { SHIPPED_SKILLS } from "../install/shipped-skills.mjs";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

describe("vision-evolve skill", () => {
  it("names its five principles", () => {
    const skill = read(".claude/skills/vision-evolve/SKILL.md");

    ok(skill.includes("says something true and useful"));
    ok(skill.includes("has grown"));
    ok(skill.includes("become one stronger line"));
    ok(skill.includes("lasting outcome"));
    ok(skill.includes("needs no sign-off"));
  });

  it("says a Success criterion is one sentence of 25 words or fewer", () => {
    for (const path of [
      ".claude/skills/vision-evolve/SKILL.md",
      "docs/skills/vision-evolve.md",
    ]) {
      ok(read(path).includes("one sentence of 25 words or fewer"), path);
    }
  });

  it("keeps every Success criterion to one sentence of 25 words or fewer", () => {
    const section = read("VISION.md")
      .split("## Success criteria")[1]
      .split("\n## ")[0];
    const criteria = section
      .split("\n")
      .filter((line) => line.startsWith("- ["))
      .map((line) => line.replace(/^- \[.\] /, ""));

    ok(criteria.length > 0);
    for (const criterion of criteria) {
      ok(criterion.split(/\s+/).length <= 25, criterion);
      ok(!/[.!?]\s/.test(criterion), criterion);
    }
  });

  it("copies the changed Vision to the Linear project page", () => {
    const skill = read(".claude/skills/vision-evolve/SKILL.md");

    ok(skill.includes("/linear:update-vision"));
    ok(skill.includes("say the Linear copy was skipped"));
  });

  it("is where finish, quick and plan-work send work that fits no criterion", () => {
    for (const name of ["finish", "quick", "plan-work"]) {
      const command = read(`.claude/commands/linear/${name}.md`);
      ok(command.includes("/vision-evolve"), name);
    }
  });

  it("is where /vision sends the changing of an existing Vision", () => {
    const vision = read(".claude/skills/vision/SKILL.md");

    ok(vision.includes("/vision-evolve"));
    ok(!vision.includes("Edit — switch to direct editing"));
    const editChoice = vision.split("\n").find((line) => line.startsWith("- **Edit**"));
    ok(editChoice?.includes("/vision-evolve"));
  });

  it("is counted in the Codex install page", () => {
    const page = read("docs/install-codex.md");
    const words = [
      "zero",
      "one",
      "two",
      "three",
      "four",
      "five",
      "six",
      "seven",
      "eight",
      "nine",
      "ten",
    ];

    ok(page.includes(`the ${words[SHIPPED_SKILLS.length]} shipped skills`));
  });
});

function read(path) {
  return readFileSync(join(strideRoot, path), "utf8");
}
