import { ok } from "node:assert";
import { readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const strideRoot = join(__dirname, "..");
const DISPATCHERS = ["bin/install.mjs", "bin/uninstall.mjs"];

function agentNames() {
  return readdirSync(join(strideRoot, "install/agents"), {
    withFileTypes: true,
  })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name);
}

function mentioning(file, name) {
  return readFileSync(join(strideRoot, file), "utf8")
    .split("\n")
    .filter((line) => new RegExp(name, "i").test(line));
}

describe("agent modules", () => {
  it("names an agent only where the dispatcher imports and registers it", () => {
    for (const name of agentNames()) {
      for (const file of DISPATCHERS) {
        for (const line of mentioning(file, name)) {
          const trimmed = line.trim();
          ok(
            trimmed.startsWith("import ") ||
              /^(const AGENTS|\w+,$)/.test(trimmed),
            `${file} mentions ${name} outside the import and registry: ${trimmed}`,
          );
        }
      }
    }
  });

  it("generates only inside the root it declares", async () => {
    for (const name of agentNames()) {
      const module = await import(
        join(strideRoot, "install/agents", name, "index.mjs")
      );
      const agent = module[name];
      ok(agent.root.startsWith("."), `${name} should declare a footprint root`);
      ok(
        agent.generates.every((path) => path.startsWith(agent.root)),
        `${name} generates outside the root it declares`,
      );
    }
  });
});
