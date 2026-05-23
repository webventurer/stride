# Data display options — from dataframe to viewer

> **AI Assistant Note**: When a user asks how to show analysis results — charts, tables, dashboards — to themselves or a stakeholder, reference this document first. The options are ordered by how much new infrastructure each introduces; the recommendation defaults to the leftmost option that meets the requirement.

This is the sibling question to [`data-format.md`](./data-format.md). Once raw sources are in a useable shape (typically pandas dataframes), the next question is: how does the result reach a viewer? The temptation is to reach for a dashboard framework or a full web app. The YAGNI answer is almost always smaller. This document weighs the realistic options and gives a default ordering.

## 🚨 Quick reference

<mark>**Default recommendation: render charts inline in the notebook or script that already holds the analysis — pandas `.plot()` or `plotly.express` — no separate display layer.**</mark>

Why: for typical small-scale analytical work (one analyst, exploratory questions, a stakeholder who wants to see a result), the chart belongs next to the dataframe that produced it. Adding a display layer earns its keep only when concrete signals fire.

**When to revisit the default:**

| Signal | Switch to |
|:-------|:----------|
| The output needs to leave the notebook (email a stakeholder, embed in a doc) | Export static HTML (`fig.write_html(...)`) or a PNG |
| The stakeholder wants to filter or drill in themselves | Single-file Streamlit app |
| Filters and controls interact in non-trivial ways | Dash (callbacks) or Panel |
| Display becomes part of a real product, not a one-shot view | FastAPI + JS frontend (app-starter pattern) |
| Multiple non-technical users need their own dashboards on shared data | Hosted BI tool (Metabase, Superset, Hex) |

## The three concerns this question hides

Before comparing options, untangle what "display the data" actually means. It mixes three independent decisions:

| Concern | What it picks | Examples |
|:--------|:--------------|:--------|
| **Render layer** | The library that draws the chart | matplotlib, plotly, altair/vega-lite, Recharts, Observable Plot |
| **Interaction model** | How the viewer engages with the result | Static image, static HTML, reactive server, full SPA |
| **Hosting** | Where the viewer accesses it | Notebook output, single file, local Python server, deployed web app |

Most of the *"Dash vs Streamlit vs a web app"* debate is actually three separate debates mashed together. Pulling them apart is what surfaces the YAGNI answer: **change as few of the three as the problem demands**.

## The options, simplest first

### Option 1 — inline charts in the notebook or script (recommended default)

**What it is**: the same notebook or script that loads dataframes also produces charts. `df.plot()` for quick exploration; `plotly.express` for interactive hover/zoom; `altair` if you prefer declarative grammar.

**Cost**: one dependency (matplotlib ships with pandas; plotly is one `pip install`).

**What it buys**:

- Chart is created next to the data that produced it — no synchronisation problem
- The notebook *is* the display surface for the analyst
- Output is rich: tables, charts, prose, all in one place
- Source-of-truth stays one place (the analysis code)

**Earns its place when**: the audience is the analyst, or a stakeholder who can open the notebook (or receive an exported HTML). *This is the common case.*

### Option 2 — exported static HTML or image

**What it is**: same as Option 1, plus a final step — `fig.write_html("chart.html")` or `plt.savefig("chart.png")`. The artefact can be emailed, embedded in a doc, or committed to a repo.

**Cost**: one extra line per chart.

**What it buys**: the result survives outside the notebook. The viewer needs nothing but a browser or image viewer. Plotly HTML keeps hover/zoom interactivity without any server.

**Earns its place when**: the stakeholder wants a *file*, not a process. A reasonable evolution of Option 1 once sharing matters.

### Option 3 — single-file Streamlit app

**What it is**: one Python file. Widgets at the top (`st.selectbox`, `st.slider`), dataframe and chart code below, `streamlit run app.py` to launch. No callback wiring — Streamlit re-runs the script when widgets change.

**Cost**: one dependency (`streamlit`); a process to keep running if shared with others (or a hosted Streamlit Cloud account).

**What it buys**: lets the *stakeholder* choose filters, not just the analyst. Most expressive thing you can do with the same Python skill set used to write the analysis.

**Earns its place when**: the same view needs to answer slightly different questions ("what if we filter to last 30 days?"). Avoids the analyst becoming a human callback.

### Option 4 — Dash by Plotly

**What it is**: a Python web framework purpose-built for analytical dashboards. Reactive callbacks tie inputs to outputs. More boilerplate than Streamlit but more control over layout and update semantics.

**Cost**: one dependency (`dash`); callback wiring; a process to host.

**What it buys**: fine-grained control over which component updates when. Streamlit re-runs the whole script on any change; Dash updates only the affected callback. Useful when filters interact in non-trivial ways or chart updates are expensive.

**Where it loses on YAGNI**: most analytical views don't need callback granularity. Streamlit's "re-run the whole script" model is fast enough at small scale, and lower boilerplate matters more than the optimisation.

**Earns its place when**: the dashboard has many interacting controls and Streamlit's re-run cost becomes visible, *or* you need precise control over component updates.

### Option 5 — Panel, Voila, or Marimo

**What it is**: variations on the notebook-as-app theme. Panel layers widgets onto notebook code; Voila publishes an existing notebook as a no-edit dashboard; Marimo is a reactive notebook with built-in widgets.

**Cost**: one dependency each.

**What it buys**: a different point on the spectrum between "notebook" and "dashboard" — if you've already invested heavily in a notebook, these turn it into a shareable app with minimal restructuring.

**Earns its place when**: the analysis already lives in a notebook and you want to publish that notebook *as-is* to a stakeholder.

### Option 6 — FastAPI backend + JS frontend (the app-starter pattern)

**What it is**: Python becomes a data service. Either FastAPI exposes endpoints that return JSON (`/api/swipes-by-day`), or pandas exports flat files (CSV/JSON/Parquet — see [data-format.md](./data-format.md) Option 4) that the JS side reads directly. A separate JavaScript app — e.g., the [app-starter](https://github.com/webventurer/app-starter) repo dropped into a subdirectory — renders charts using Recharts, Plotly.js, or Observable Plot.

**Cost**: a second language and toolchain (Node, bundler), a network or file boundary, two deployment targets, JSON schema as a contract between Python and JS.

**What it buys**: the display layer becomes a real product — routing, navigation, design system, multiple pages, authentication, custom interactions that go beyond what Streamlit/Dash render. The Python side stays focused on data; the JS side stays focused on UI.

**Where it loses on YAGNI hard**: introduces *two* new layers (HTTP API or export step + JS app) for output that may only need a single chart. JSON shapes and URLs get baked in as contracts — exactly the kind of decision *Postpone decisions* says to defer until forced.

**Earns its place when**: the display has graduated from "show a result" to "be a product" — multiple views, routing, branded UI, end users who aren't the analyst. *That's a different project, reached by evolution, not predicted up front.*

**Two sub-shapes worth distinguishing:**

| Sub-shape | What Python emits | What JS consumes | When it fits |
|:----------|:------------------|:-----------------|:-------------|
| **File bridge** | CSV/JSON/Parquet on disk | `fetch('/data/swipes.json')` at build or runtime | Read-only display; static export pipeline; no live filtering |
| **API bridge (FastAPI)** | HTTP endpoints returning JSON | `fetch('/api/swipes?from=...')` with query params | Filters, parameters, or computations the JS can't precompute |

The file bridge is meaningfully lighter than the API bridge — no running Python process, no schema drift between server and client. Reach for it first.

### Option 7 — hosted BI tool (Metabase, Superset, Hex, Mode)

**What it is**: drop-in dashboard tool. Point it at a database or warehouse, build dashboards in a UI, share links with stakeholders.

**Cost**: hosting (or SaaS subscription); data must live in a queryable store (sqlite, duckdb, Postgres — see [data-format.md](./data-format.md) Options 5–8); learning the tool's idioms.

**What it buys**: multi-user, multi-dashboard, governed access without writing display code. The Python analysis becomes the data pipeline; the BI tool becomes the display layer.

**Earns its place when**: many non-technical users need their own dashboards over shared data, or the organisation has standardised on a BI tool. *Not the right shape for a single-analyst project.*

## Comparison table

| # | Option | New infra | Effort | Best for |
|:--|:-------|:----------|:-------|:---------|
| 1 | **Inline charts in notebook/script (default)** | matplotlib / plotly | Trivial | Analyst-facing exploration |
| 2 | Exported HTML / PNG | Same | +1 line | Emailable, embeddable artefact |
| 3 | Streamlit single-file app | +streamlit | One file | Stakeholder-driven filtering |
| 4 | Dash | +dash | Moderate boilerplate | Many interacting controls |
| 5 | Panel / Voila / Marimo | +one dep | Low (notebook reuse) | Publishing an existing notebook |
| 6 | FastAPI + JS (app-starter) | API + JS toolchain | High | Display has graduated to a product |
| 7 | Hosted BI tool | SaaS / hosting + a queryable store | High | Multi-user dashboard governance |

## The decision, applied

For a typical small-scale analysis project — single analyst, exploratory questions, output consumed by a stakeholder as a one-shot or short-lived demo — **Option 1 (evolving to Option 2 when sharing matters) is the only choice that doesn't add infrastructure for a requirement that doesn't exist yet**.

| Principle | Verdict |
|:----------|:--------|
| *Do the simplest thing that works* | Option 1 — the chart lives next to the data |
| *YAGNI* | Options 3–7 all build for requirements we don't have |
| *Postpone decisions* | Option 1 keeps every door open; any pandas chart can be re-used inside Streamlit, Dash, or exported HTML later |
| *Choose the path that makes change easier* | Option 1 — if any "when to revisit" signal fires, swap in Streamlit or static export without re-architecting |

The trap to avoid: **picking a heavyweight option because the eventual end state might be a dashboard or web app**. Most analysis projects never get there, and even when they do, the path is *Option 1 → Option 2 → Option 3 → onwards as signals fire* — not jumping to Option 6 on day one. Every layer added before it's needed is a layer that must be maintained, explained, and worked around.

## The torch — what shifts this recommendation

- **Display is the product, not the byproduct.** If the *deliverable* is the dashboard (not the analysis behind it), the calculus flips — Option 3 or 6 becomes the starting point, not the destination. Most analysis projects are the opposite: the deliverable is an answer to a question, and the chart is one way to convey it.
- **Cross-language consumers.** If the chart must render inside an existing JS app (a marketing site, an internal tool), Option 6 is forced — but only the JSON or file-export side, not necessarily a full app-starter subdirectory. Skip the JS scaffold if you're embedding into something that already exists.
- **Audience size.** A single stakeholder reading a report is Option 1–2. Ten stakeholders, each filtering for themselves, is Option 3. A hundred stakeholders with role-based access is Option 7.

---

*A pattern: keep the display layer at the leftmost option that still meets the requirement. Move right only when a concrete signal forces it.*
