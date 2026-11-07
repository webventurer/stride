import { ok, strictEqual } from "node:assert";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

function read(path) {
  return readFileSync(join(strideRoot, path), "utf8");
}

function principleSection(text) {
  const start = text.indexOf("## The principle\n");
  ok(start !== -1, "no `## The principle` heading");
  const afterHeading = start + "## The principle\n".length;
  const next = text.slice(afterHeading).search(/^#{1,6} /m);
  return next === -1
    ? text.slice(start)
    : text.slice(start, afterHeading + next);
}

describe("stride's principle", () => {
  const vision = principleSection(read("VISION.md"));

  for (const path of ["README.md", "docs/why-stride.md", "CLAUDE.md"]) {
    it(`${path} states it exactly as VISION.md does`, () => {
      strictEqual(principleSection(read(path)), vision);
    });
  }

  it("README.md puts it before What you get", () => {
    const readme = read("README.md");
    ok(
      readme.indexOf("## The principle\n") <
        readme.indexOf("## What you get\n"),
    );
  });

  it("docs/why-stride.md puts it after its opening paragraph", () => {
    const page = read("docs/why-stride.md");
    ok(
      page.indexOf("## The principle\n") >
        page.indexOf("Vibe coding builds on"),
    );
  });
});
