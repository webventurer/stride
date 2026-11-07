import { ok } from "node:assert";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

const cardFile = "/tmp/<identifier>/card.md";
const saveCommand = `jq -r .description > ${cardFile}`;

const places = [
  {
    name: "start.md step 3 (start check)",
    path: ".claude/commands/linear/start.md",
    brief: "card-start-review.md",
  },
  {
    name: "start.md step 10 (simplification review)",
    path: ".claude/commands/linear/start.md",
    brief: "simplify-review.md",
  },
  {
    name: "card-check.md step 1 (end check)",
    path: ".claude/commands/linear/reference/card-check.md",
    brief: "card-check-review.md",
  },
];

describe("reviewers read the card's exact text from a file", () => {
  for (const { name, path, brief } of places) {
    it(`${name} saves the card to a per-card file and names it in the prompt`, () => {
      const lines = readFileSync(join(strideRoot, path), "utf8").split("\n");
      const promptStart = "> Read `.claude/commands/linear/reference/";
      const prompt = lines.findIndex((line) =>
        line.includes(`${promptStart}${brief}\``),
      );
      const previousPrompt = lines
        .slice(0, prompt)
        .findLastIndex((line) => line.includes(promptStart));

      ok(prompt !== -1, "reviewer prompt line exists");
      ok(lines[prompt].includes(cardFile), "prompt names the card file");
      ok(
        !lines[prompt].includes("described as: `<issue description>`"),
        "prompt does not paste the description",
      );
      ok(
        lines
          .slice(previousPrompt + 1, prompt)
          .some((line) => line.includes(saveCommand)),
        "the card is saved between the previous reviewer prompt and this one",
      );
    });
  }
});
