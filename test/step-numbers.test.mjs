import { deepStrictEqual } from "node:assert";
import { mkdtempSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, relative } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const commandsDir = join(strideRoot, ".claude/commands");
const skillsDir = join(strideRoot, ".claude/skills");

const markdownFilesUnder = (dir) =>
  readdirSync(dir, { recursive: true })
    .filter((path) => path.endsWith(".md"))
    .map((path) => join(dir, path));

const letteredStepHeading = /^#{1,6} (?:Step )?(\d+)[a-zA-Z]\b/;
const plainStepHeading = /^#{1,6} (?:Step )?(\d+)(?![a-zA-Z\d])/;

const headingsIn = (file) => readFileSync(file, "utf8").split("\n");

const letteredHeadings = (files) =>
  files.flatMap((file) =>
    headingsIn(file)
      .filter((line) => letteredStepHeading.test(line))
      .map((line) => `${relative(strideRoot, file)}: ${line}`),
  );

const squeezedInHeadings = (files) =>
  files.flatMap((file) => {
    const lines = headingsIn(file);
    const plainNumbers = new Set(
      lines.flatMap((line) => plainStepHeading.exec(line)?.slice(1) ?? []),
    );
    return lines
      .filter((line) => plainNumbers.has(letteredStepHeading.exec(line)?.[1]))
      .map((line) => `${relative(strideRoot, file)}: ${line}`);
  });

const fixtureFile = (content) => {
  const file = join(mkdtempSync(join(tmpdir(), "step-numbers-")), "SKILL.md");
  writeFileSync(file, content);
  return file;
};

describe("command step numbering", () => {
  it("never puts a letter after a step number in a heading", () => {
    deepStrictEqual(letteredHeadings(markdownFilesUnder(commandsDir)), []);
  });
});

describe("skill step numbering", () => {
  it("never squeezes a lettered step in beside a plain step of the same number", () => {
    deepStrictEqual(squeezedInHeadings(markdownFilesUnder(skillsDir)), []);
  });

  it("fails on a lettered step heading beside a plain heading of its number", () => {
    const file = fixtureFile(
      "### Step 1: One\n\n### Step 2: Two\n\n### Step 2b: Extra\n\n### Step 3: Three\n",
    );
    deepStrictEqual(squeezedInHeadings([file]).length, 1);
  });

  it("passes on lettered alternatives that stand in for a step with no plain heading", () => {
    const file = fixtureFile(
      "### 2. Choose\n\n### 3a. Short\n\n### 3b. Full\n\n### 4. Assemble\n",
    );
    deepStrictEqual(squeezedInHeadings([file]), []);
  });
});
