import { deepStrictEqual, ok, strictEqual } from "node:assert";
import { describe, it } from "node:test";
import {
  missingPrereqs,
  prereqReport,
  requirePrerequisites,
  windowsReport,
} from "../bin/prereqs.mjs";

describe("missingPrereqs", () => {
  it("returns only the tools absent from PATH", () => {
    const present = (cmd) => cmd !== "jq"; // jq missing, rest present
    const missing = missingPrereqs(present);

    deepStrictEqual(
      missing.map((p) => p.cmd),
      ["jq"],
    );
  });

  it("returns empty when every tool is present", () => {
    deepStrictEqual(
      missingPrereqs(() => true),
      [],
    );
  });

  it("returns all three when none are present", () => {
    deepStrictEqual(
      missingPrereqs(() => false).map((p) => p.cmd),
      ["gh", "uv", "jq"],
    );
  });
});

describe("prereqReport", () => {
  it("reports all-found when nothing is missing", () => {
    deepStrictEqual(prereqReport([]), ["Prerequisites: gh, uv, jq all found."]);
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
    ok(out.some((l) => l.includes("jq — brew install jq")));
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

  it("points native Windows at WSL and exits non-zero without probing", () => {
    const out = [];
    let exitCode = null;
    let probed = false;
    requirePrerequisites(
      () => {
        probed = true;
        return false;
      },
      (line) => out.push(line),
      (code) => {
        exitCode = code;
      },
      "win32",
    );

    ok(out.some((l) => l.includes("requires WSL on Windows")));
    strictEqual(probed, false); // never shells out to the POSIX-only probe
    strictEqual(exitCode, 1);
  });

  it("uses the command -v probe path on linux/darwin", () => {
    const out = [];
    let exitCode = null;
    requirePrerequisites(
      () => false,
      (line) => out.push(line),
      (code) => {
        exitCode = code;
      },
      "linux",
    );

    ok(out.some((l) => l.startsWith("Missing prerequisites")));
    strictEqual(exitCode, 1);
  });
});

describe("windowsReport", () => {
  it("points at WSL and the install docs", () => {
    const lines = windowsReport();

    ok(lines[0].includes("requires WSL on Windows"));
    ok(lines.some((l) => l.includes("docs/install.md")));
  });
});
