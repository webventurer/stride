import { ok } from "node:assert";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";
import { SHIPPED_SKILLS } from "../install/shipped-skills.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const strideRoot = join(__dirname, "..");

function read(rel) {
  return readFileSync(join(strideRoot, rel), "utf8");
}

describe("skill documentation", () => {
  it("gives every shipped skill a docs page", () => {
    for (const { name } of SHIPPED_SKILLS) {
      const page = `docs/skills/${name}.md`;
      ok(existsSync(join(strideRoot, page)), `missing ${page}`);
    }
  });

  it("lists every shipped skill in the docs nav and sidebar", () => {
    const config = read("docs/.vitepress/config.mts");

    for (const { name } of SHIPPED_SKILLS) {
      const link = `'/skills/${name}'`;
      const count = config.split(link).length - 1;
      ok(count >= 2, `expected ${link} in both nav and sidebar, saw ${count}`);
    }
  });

  it("describes every shipped skill in the README", () => {
    const readme = read("README.md");

    for (const { name } of SHIPPED_SKILLS) {
      ok(readme.includes(`\`/${name}\``), `README never mentions /${name}`);
    }
  });
});
