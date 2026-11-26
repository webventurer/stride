import { ok, strictEqual } from "node:assert";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const PACK = ".claude/stride/docs/principles";
const KEPT_ESSAYS = [
  "principles-over-rules.md",
  "single-responsibility-principle.md",
];
const TEMPLATE_HEADINGS = [
  "## The test",
  "## Worked example",
  "## Where it stops",
  "## Related",
  "## Source",
];
const AGILITY = `- Agility
    - Find out where you are.
    - Take a small step towards your goal.
    - Adjust your understanding based on what you learned.
    - Repeat.
- When faced with **two or more alternatives** that deliver roughly the same value, **take the path that makes future change easier**.`;

function read(path) {
  return readFileSync(join(strideRoot, path), "utf8");
}

function principlePages() {
  return readdirSync(join(strideRoot, PACK)).filter(
    (name) => name.endsWith(".md") && name !== "README.md",
  );
}

function newPages() {
  return principlePages().filter((name) => !KEPT_ESSAYS.includes(name));
}

function linkedPages(text) {
  return [...text.matchAll(/\]\(([^)#]+\.md)(#[^)]*)?\)/g)].map((m) => m[1]);
}

function principleLines(text) {
  return text.split("\n").filter((line) => /^\d+\. \*\*\[/.test(line));
}

function lineSentences(line) {
  const afterName = line
    .replace(/^\d+\. \*\*\[[^\]]+\]\([^)]+\)\.?\*\*/, "")
    .replace(/^ \([^)]+\)\./, "")
    .trim();
  return afterName.split(/(?<=\.)\s+(?=[A-Z])/).filter(Boolean);
}

function wordCount(text) {
  return text
    .replace(/<!--[\s\S]*?-->/g, "")
    .split(/\s+/)
    .filter(Boolean).length;
}

function markdownFiles(dir) {
  return readdirSync(join(strideRoot, dir)).flatMap((name) => {
    const rel = join(dir, name);
    if (name === "node_modules" || name === ".vitepress") return [];
    if (statSync(join(strideRoot, rel)).isDirectory())
      return markdownFiles(rel);
    return name.endsWith(".md") ? [rel] : [];
  });
}

describe("principles pack", () => {
  const readme = read(`${PACK}/README.md`);

  it("keeps the README small enough to inject on every prompt", () => {
    ok(Buffer.byteLength(readme) <= 6144, `${Buffer.byteLength(readme)} bytes`);
    ok(wordCount(readme) <= 900, `${wordCount(readme)} words`);
  });

  it("opens by saying how to use the principles and where the pages are", () => {
    const opening = readme.split("\n## ")[0];
    for (const phrase of [
      "with judgement",
      "a case of being agile",
      "Open a principle's page when",
      `${PACK}/`,
    ]) {
      ok(opening.includes(phrase), `opening lacks "${phrase}"`);
    }
  });

  it("never tells the agent to obey a constraint", () => {
    ok(!/obey|constraint/i.test(readme));
  });

  for (const line of principleLines(readme)) {
    const page = linkedPages(line)[0];

    it(`${page}'s line says what it asks and why`, () => {
      ok(lineSentences(line).length >= 2, line);
    });

    it(`${page}'s line ends with a reason taken from its page`, () => {
      const reason = lineSentences(line).at(-1);
      ok(read(`${PACK}/${page}`).includes(reason), reason);
    });
  }

  it("lists every principle page in the README", () => {
    const listed = linkedPages(readme);
    for (const page of principlePages()) {
      ok(listed.includes(page), `README has no line for ${page}`);
    }
  });

  it("links only to principle pages that exist", () => {
    for (const page of linkedPages(readme)) {
      ok(principlePages().includes(page), `README links to missing ${page}`);
    }
  });

  it("lists 18 principles", () => {
    strictEqual(new Set(linkedPages(readme)).size, 18);
  });

  it("ends the README with The test", () => {
    ok(readme.includes("## The test"));
  });

  for (const page of newPages()) {
    it(`${page} follows the template`, () => {
      const text = read(`${PACK}/${page}`);
      for (const heading of TEMPLATE_HEADINGS) {
        ok(text.includes(heading), `${page} lacks ${heading}`);
      }
      ok(!text.includes("<!--"), `${page} still holds template comments`);
    });

    it(`${page} opens with a paragraph before The test`, () => {
      const opening = read(`${PACK}/${page}`).split("## The test")[0];
      ok(
        opening.split("\n").some((line) => /^[A-Za-z*`"]/.test(line)),
        `${page} has no opening paragraph`,
      );
    });

    it(`${page} runs to no more than 1,000 words`, () => {
      const words = wordCount(read(`${PACK}/${page}`));
      ok(words <= 1000, `${page} is ${words} words`);
    });
  }

  it("be-agile.md carries the four steps and the quote word for word", () => {
    ok(read(`${PACK}/be-agile.md`).includes(AGILITY));
  });

  it("single-responsibility-principle.md holds the read-it-aloud test", () => {
    ok(
      read(`${PACK}/single-responsibility-principle.md`).includes(
        "Read the function name aloud",
      ),
    );
  });

  it("start and quick link to the README's test", () => {
    for (const path of [
      ".claude/commands/linear/start.md",
      ".claude/commands/linear/quick.md",
    ]) {
      ok(
        read(path).includes("stride/docs/principles/README.md#the-test"),
        path,
      );
    }
  });

  it("simplify-review names the README's test", () => {
    ok(
      read(".claude/commands/linear/reference/simplify-review.md").includes(
        `${PACK}/README.md`,
      ),
    );
  });

  it("leaves no stride doc linking to design-decisions.md", () => {
    const files = [".claude/commands", ".claude/stride", "docs"].flatMap(
      markdownFiles,
    );
    for (const file of files) {
      ok(!read(file).includes("design-decisions.md"), file);
    }
  });
});
