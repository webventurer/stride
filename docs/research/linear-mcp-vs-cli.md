# Linear MCP vs Linear CLI

## CLI vs MCP

CLIs are eating MCPs. The industry is converging on the very same idea. MCPs for all their merit can be token hungry, slow, and unreliable for complex tool chaining. However, coding agents have become incredibly good at working with CLIs, and in fact they are far more comfortable working with CLI tools than MCP.

## The bigger pattern across r/Linear

The strongest recurring theme isn't "which CLI" — it's "move off Linear MCP because of context bloat." One representative quote: *"GitHub, Linear, Playwright MCPs can consume 60,000 tokens before the conversation even begins. This seriously degrades LLM's ability to reason."* Several people describe a pattern of "start with MCP enabled so the agent can see the connections, ask it to build a custom CLI, then remove the MCP." That's the meta-recommendation right now.

Worth flagging since you've already got `linear-webventurer` MCP wired into `.mcp.json` — the people writing this advice are running into exactly your setup.

## Research from Reddit

### Recommendation by use case

| Your situation | Pick |
|:---|:---|
| Driving Linear from Claude Code / agent workflows (your case in this repo) | **dorkitude/linctl** — explicitly built for this; most mentions; consistently recommended over MCP for context efficiency |
| Mature, terminal-focused human use (jump to issue, create PR with Linear context) | **schpet/linear-cli** — the elder, most often cited as "robust" |
| JSON-out CLI that an agent calls as a skill, with GraphQL fallback | **czottmann/linearis** |
| Maximum token efficiency in agent context | **joa23/linear-cli** |

## Bottom line

For most people, **linctl** looks like the best dedicated Linear CLI for Claude workflows right now, because it's purpose-built for agents like Claude Code and is designed around issue listing, creation, and workflow actions from the terminal.

## Linear CLIs surveyed

- **linctl** — <https://github.com/dorkitude/linctl>
- **linear-cli** (schpet) — <https://github.com/schpet/linear-cli>
  - <https://www.claudepluginhub.com/marketplaces/schpet-linear-cli>
  - <https://crates.io/crates/linear-cli/0.3.8>
  - <https://github.com/Finesssee/linear-cli>
- **Composio** — <https://composio.dev/toolkits/linear/framework/cli>
- **Linearis** — <https://github.com/linearis-oss/linearis>
  - <https://zottmann.org/2025/09/03/linearis-my-linear-cli-built.html>
- **Linear developers** — <https://linear.app/developers>
