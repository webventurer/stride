import { execSync } from "node:child_process";

// The CLIs the /linear:* workflow needs on PATH. Install commands mirror
// docs/install.md so the two never drift; brew covers macOS and Linux.
export const PREREQS = [
  { cmd: "gh", install: "brew install gh" },
  { cmd: "uv", install: "brew install uv" },
  {
    cmd: "linctl",
    install: "brew tap dorkitude/linctl && brew install linctl",
  },
  { cmd: "jq", install: "brew install jq" },
];

// The prereqs absent from PATH. `isPresent` is injectable so tests don't shell out.
export function missingPrereqs(isPresent = onPath) {
  return PREREQS.filter((p) => !isPresent(p.cmd));
}

// The lines the doctor prints — pure, so tests assert on the array.
export function prereqReport(missing) {
  if (missing.length === 0)
    return ["Prerequisites: gh, uv, linctl, jq all found."];
  return [
    "Missing prerequisites — stride needs these on your PATH. Install them, then re-run:",
    ...missing.map((p) => `  ${p.cmd} — ${p.install}`),
    "  (Non-macOS or no Homebrew? See docs/install.md. install.mjs won't run these for you.)",
  ];
}

// What native Windows sees instead of the (POSIX-only) tool probes. WSL is
// stride's supported Windows path — the hooks and linctl both need a POSIX
// shell — so say that plainly rather than report every tool "missing".
export function windowsReport() {
  return [
    "stride requires WSL on Windows — its commit hooks and the linctl CLI",
    "both need a bash/zsh shell. Install WSL, then run the install from",
    "inside it. See the Windows section of docs/install.md.",
  ];
}

// Blocking gate: print the report, and stop the installer if anything is
// missing — stride's /linear:* workflow can't run without these tools, so
// installing half of stride leaves a broken state. On native Windows the
// POSIX `command -v` probe can't run at all, so point at WSL instead of
// reporting a misleading all-missing result.
export function requirePrerequisites(
  isPresent = onPath,
  log = console.log,
  exit = process.exit,
  platform = process.platform,
) {
  log("");
  if (platform === "win32") {
    for (const line of windowsReport()) log(line);
    exit(1);
    return;
  }
  const missing = missingPrereqs(isPresent);
  for (const line of prereqReport(missing)) log(line);
  if (missing.length > 0) exit(1);
}

function onPath(cmd) {
  try {
    execSync(`command -v ${cmd}`, { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}
