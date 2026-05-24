import { deepStrictEqual, ok, strictEqual } from "node:assert";
import { describe, it } from "node:test";
import {
  missingPrereqs,
  prereqReport,
  requirePrerequisites,
} from "../bin/prereqs.mjs";

describe("missingPrereqs", () => {
  it("returns only the tools absent from PATH", () => {
    const present = (cmd) => cmd !== "linctl"; // linctl missing, rest present
    const missing = missingPrereqs(present);

    deepStrictEqual(
      missing.map((p) => p.cmd),
      ["linctl"],
    );
  });

  it("returns empty when every tool is present", () => {
    deepStrictEqual(
      missingPrereqs(() => true),
      [],
    );
  });

  it("returns all four when none are present", () => {
    deepStrictEqual(
      missingPrereqs(() => false).map((p) => p.cmd),
      ["gh", "uv", "linctl", "jq"],
    );
  });
});

describe("prereqReport", () => {
  it("reports all-found when nothing is missing", () => {
    deepStrictEqual(prereqReport([]), [
      "Prerequisites: gh, uv, linctl, jq all found.",
    ]);
  });

  it("names each missing tool with its install command", () => {
    const lines = prereqReport([{ cmd: "jq", install: "brew install jq" }]);

    ok(lines[0].startsWith("Missing prerequisites"));
    ok(lines.includes("  jq — brew install jq"));
  });
});

describe("requirePrerequisites", () => {
  it("prints the report and exits non-zero when a tool is missing", () => {
    const out = [];
    let exitCode = null;
    requirePrerequisites(
      () => false,
      (line) => out.push(line),
      (code) => {
        exitCode = code;
      },
    );

    ok(out.some((l) => l.startsWith("Missing prerequisites")));
    ok(out.some((l) => l.includes("linctl — brew tap dorkitude/linctl")));
    strictEqual(exitCode, 1);
  });

  it("does not exit when every tool is present", () => {
    let exited = false;
    requirePrerequisites(
      () => true,
      () => {},
      () => {
        exited = true;
      },
    );

    strictEqual(exited, false);
  });
});
