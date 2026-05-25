import { strictEqual } from "node:assert";
import { execSync } from "node:child_process";
import {
  existsSync,
  lstatSync,
  mkdirSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { after, describe, it } from "node:test";
import { fileURLToPath } from "node:url";
import { REMOVED_PATHS } from "../bin/removed-paths.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const strideRoot = join(__dirname, "..");
const fixtureRoot = join("/tmp", `stride-prune-${process.pid}`);

function seed(extra = {}) {
  rmSync(fixtureRoot, { recursive: true, force: true });
  mkdirSync(fixtureRoot, { recursive: true });
  for (const [rel, content] of Object.entries(extra)) {
    const full = join(fixtureRoot, rel);
    mkdirSync(dirname(full), { recursive: true });
    writeFileSync(full, content);
  }
}

function runInstall(input) {
  execSync(`node ${join(strideRoot, "bin/install.mjs")}`, {
    cwd: fixtureRoot,
    input,
    stdio: ["pipe", "pipe", "pipe"],
  });
}

describe("install prune", () => {
  after(() => rmSync(fixtureRoot, { recursive: true, force: true }));

  it("removes an orphan from an older version when confirmed", () => {
    const orphan = ".claude/tools/linear_client.py";
    seed({ [orphan]: "stale stride code\n" });
    runInstall("y\nn\nn\n"); // prune Y, gitignore n
    strictEqual(existsSync(join(fixtureRoot, orphan)), false);
  });

  it("keeps the orphan when prune is declined", () => {
    const orphan = ".claude/tools/linear_client.py";
    seed({ [orphan]: "stale stride code\n" });
    runInstall("n\nn\nn\n"); // prune n, gitignore n
    strictEqual(existsSync(join(fixtureRoot, orphan)), true);
  });

  it("removes the orphan's now-empty ancestor directories", () => {
    seed({ ".claude/docs/concepts/atomicity.md": "stale doc\n" });
    runInstall("y\nn\nn\n");
    strictEqual(existsSync(join(fixtureRoot, ".claude/docs")), false);
  });

  it("prunes nothing and still installs on a clean repo", () => {
    seed(); // no orphans → no prune prompt
    runInstall("n\nn\n"); // gitignore n
    strictEqual(
      existsSync(join(fixtureRoot, ".claude/tools/linear_cli.py")),
      true,
    );
  });

  it("never deletes through a symlinked dir (codefu dev setup)", () => {
    seed();
    const external = join("/tmp", `stride-prune-ext-${process.pid}`);
    rmSync(external, { recursive: true, force: true });
    const target = join(
      external,
      "principles/single-responsibility-principle.md",
    );
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, "codefu source — must survive\n");
    mkdirSync(join(fixtureRoot, ".claude"), { recursive: true });
    symlinkSync(external, join(fixtureRoot, ".claude/docs"));

    runInstall("n\nn\n"); // no real orphan detected → no prune prompt

    strictEqual(existsSync(target), true);
    rmSync(external, { recursive: true, force: true });
  });

  it("lists no path stride still ships", () => {
    for (const rel of REMOVED_PATHS) {
      strictEqual(shipped(rel), false, `REMOVED_PATHS still shipped: ${rel}`);
    }
  });
});

function shipped(rel) {
  let current = strideRoot;
  for (const part of rel.split("/")) {
    current = join(current, part);
    if (!existsSync(current) || lstatSync(current).isSymbolicLink()) {
      return false;
    }
  }
  return true;
}
