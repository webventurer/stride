import { ok } from "node:assert";
import { execSync } from "node:child_process";
import { mkdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { after, beforeEach, describe, it } from "node:test";
import { fileURLToPath } from "node:url";
import { linearCommandNames } from "../install/linear-commands.mjs";
import { SHIPPED_SKILLS } from "../install/shipped-skills.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const strideRoot = join(__dirname, "..");
const fixtureRoot = join("/tmp", `stride-report-${process.pid}`);

// Prompts in order: gitignore (n), settings merge (n).
function run(script) {
  return execSync(`node ${join(strideRoot, "bin", script)}`, {
    cwd: fixtureRoot,
    input: "n\nn\n",
    stdio: ["pipe", "pipe", "pipe"],
  }).toString();
}

beforeEach(() => {
  rmSync(fixtureRoot, { recursive: true, force: true });
  mkdirSync(fixtureRoot, { recursive: true });
});
after(() => rmSync(fixtureRoot, { recursive: true, force: true }));

describe("install reporting", () => {
  it("names every shipped skill in the install output", () => {
    const output = run("install.mjs");

    for (const { name } of SHIPPED_SKILLS) {
      ok(output.includes(`skills/${name}/`), `expected skills/${name}/`);
      ok(output.includes(`/${name} `), `expected the /${name} command line`);
    }
  });

  it("names every linear command in the install output", () => {
    const output = run("install.mjs");

    for (const name of linearCommandNames(strideRoot)) {
      ok(output.includes(`/linear:${name} `), `expected /linear:${name}`);
    }
  });

  it("names every shipped skill in the uninstall output", () => {
    run("install.mjs");
    const output = run("uninstall.mjs");

    for (const { name } of SHIPPED_SKILLS) {
      ok(output.includes(`skills/${name}/`), `expected skills/${name}/`);
    }
  });
});
