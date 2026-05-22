# Data format options — from raw files to useable shape

> **AI Assistant Note**: When a user asks how to load, query, or cross-reference raw source files for analysis, reference this document first. The options are ordered by how much new infrastructure each introduces; the recommendation defaults to the leftmost option that meets the requirement.

When starting a data project, you face an early question: how should raw source files (Excel, CSV, API dumps, log exports) become a useable shape for analysis? The temptation is to reach for "real" infrastructure — a database, an ORM, a pipeline. The YAGNI answer is almost always smaller. This document weighs the realistic options and gives a default ordering.

## 🚨 Quick reference

<mark>**Default recommendation: pandas dataframes loaded directly from the source files via a small `loaders.py` — no intermediate storage.**</mark>

Why: for typical small-to-medium analytical workloads (thousands of rows, single consumer, exploratory questions), every cross-reference you need — date joins, percentiles, day-of-week grouping, lookups against reference tables — is a one-liner in pandas. Adding storage layers earns its keep only when concrete signals fire.

**When to revisit the default:**

| Signal | Switch to |
|:-------|:----------|
| Loaders take more than a second to run | Add a parquet cache (intermediate flat files) |
| A non-Python consumer needs the cleaned data | Export to CSV/JSON as an *output* of the pandas layer |
| Working set exceeds comfortable memory | Move to a file-based analytical store (duckdb) |
| Multi-user concurrent edits enter the picture | Then — and only then — consider a hosted database |

## The three concerns this question hides

Before comparing options, untangle what "useable format" actually means. It mixes three independent decisions:

| Concern | What it picks | Examples |
|:--------|:--------------|:--------|
| **Storage format** | Where the bytes live on disk | Excel/CSV source, JSON, Parquet, sqlite, duckdb, Postgres |
| **Access layer** | The code that loads and queries | Loaders module, ORM, raw SQL, hand-rolled JSON parser |
| **Working representation** | The in-memory shape you analyse | pandas DataFrame, polars DataFrame, dict of lists, ORM objects |

Most of the *"JSON vs ORM vs pandas"* debate is actually three separate debates mashed together. Pulling them apart is what surfaces the YAGNI answer: **change as few of the three as the problem demands**.

## The options, simplest first

### Option 1 — pandas dataframes from source files (recommended default)

**What it is**: write a `loaders.py` with one function per source (`load_swipes()`, `load_orders()`, `load_inventory()` — whatever the domain calls for). Each function reads the source file directly (`pd.read_excel`, `pd.read_csv`), skips metadata header rows, normalises column names and types, and returns a DataFrame. Analysis happens in a notebook or script that imports and joins.

**Cost**: ~200 lines of Python; one dependency (pandas + openpyxl for Excel).

**What it buys**:

- Date joins → `df.merge(other, on="date")`
- Percentiles → `df.value.quantile(0.9)`
- Day-of-week grouping → `df.groupby(df.date.dt.day_name())`
- Source-of-truth stays one place (the raw files)
- No format drift between two representations of the same data

**Earns its place when**: data is small, single-consumer, analysis is the goal. *This is the common case.*

### Option 2 — pandas with a parquet cache

**What it is**: same as Option 1, plus loaders write a `.parquet` cache after parsing. Subsequent reads skip the slow Excel parsing.

**Cost**: ~10 extra lines (write/read parquet), one extra dependency (`pyarrow`).

**What it buys**: faster repeated reads. Negligible at small scale, meaningful if loaders run inside a tight loop or notebook restart cycle.

**Earns its place when**: loaders become a bottleneck, or you want a shareable cleaned-data artefact that survives the source files moving.

### Option 3 — JSON files

**What it is**: a one-time extraction step writes each source to a `.json` file in `data/clean/`. Analysis code reads JSON and processes the list-of-dicts shape directly (or loads it into pandas anyway).

**Cost**: extraction script, JSON files committed to repo, **plus a query layer you build by hand** — every `for row in data: if row["date"] == ...` is a line pandas would give you for free.

**What it buys**: git-diffable cleaned data (you see schema changes in PRs); human-readable in any text editor; consumable by tools outside Python.

**Where it loses on YAGNI**: if the analysis happens in Python, JSON is a worse pandas. You either reinvent filter/join/groupby by hand, or load the JSON into pandas anyway — at which point the JSON file is dead weight between the source and the dataframe.

**Earns its place when**: a non-Python consumer needs the cleaned data, *or* you want git-diffable schema reviews. Both are valid reasons — neither is the default.

### Option 4 — CSV or Parquet flat files as a cleaned tier

**What it is**: like Option 3 but tabular-native — cleaned data lives as CSV (human-readable) or Parquet (compressed, typed) in `data/clean/`.

**Cost**: extraction script + cleaned-data files.

**What it buys**: same git-diffable / shareable advantages as JSON, *without* the impedance mismatch. Pandas reads CSV and Parquet natively — no hand-rolled query layer.

**Earns its place when**: the same triggers as Option 3, but you want the cleaned tier to also serve as the analysis input. A reasonable evolution of Option 1 once sharing matters.

### Option 5 — sqlite

**What it is**: extract each source into a table in a single `.sqlite` file. Query with SQL or `pd.read_sql`.

**Cost**: extraction script, schema definitions, a `.sqlite` file in the repo (or generated on the fly).

**What it buys**: real SQL joins and aggregations; ACID guarantees; widely supported; no server.

**Where it loses on YAGNI**: pandas already does joins and aggregations on dataframes. sqlite earns its keep when **the working set doesn't fit in memory** or when **multiple processes** need to read it. Neither is common at small scale.

**Earns its place when**: data outgrows memory, *or* multiple tools/scripts need to query the same cleaned data without re-running loaders.

### Option 6 — duckdb

**What it is**: a file-based analytical database, like sqlite but column-store, optimised for analytics. Crucially, **duckdb reads Excel/CSV/Parquet directly without an import step** — `SELECT * FROM read_excel('source.xlsx')`.

**Cost**: one dependency (`duckdb`).

**What it buys**: SQL syntax on the source files with no extraction layer. Faster aggregations than pandas on bigger data. The same dataframe-friendly ergonomics (`duckdb.sql(...).df()`).

**Earns its place when**: you prefer SQL to dataframe syntax, *or* data grows past comfortable pandas size (millions of rows). Underrated middle ground — but pandas is already enough for most analytical work.

### Option 7 — polars dataframes

**What it is**: a modern pandas alternative — Rust-backed, lazy evaluation, multi-threaded. Otherwise structurally identical to pandas (loaders module + dataframes).

**Cost**: one dependency. Slightly steeper learning curve (lazy API differs from pandas).

**What it buys**: 10–100× faster on bigger data; cleaner expression syntax; better type discipline.

**Earns its place when**: pandas is a known bottleneck, *or* the team already knows polars.

### Option 8 — hosted database via an ORM

**What it is**: a networked database (Postgres on Neon, Supabase, RDS, etc.) accessed via an ORM (Drizzle in TypeScript, SQLAlchemy in Python).

**Cost**: hosting account, schema migrations, network round-trips for every query, ORM-specific tooling, potential language switch.

**What it buys**: multi-user concurrent access; production-grade durability; rich SQL; integration with web apps if the project grows into one.

**Where it loses on YAGNI hard**: introduces *three* layers of new infrastructure (hosting, migrations, network) for data that fits in a spreadsheet. Every operation pays a network round-trip. Schema must be designed up front — exactly the decision *Postpone decisions* says to defer.

**Earns its place when**: the work grows into a multi-user web app where multiple people query the data concurrently. *That's a different project, reached by evolution, not predicted up front.*

## Comparison table

| # | Option | New infra | Effort | Best for |
|:--|:-------|:----------|:-------|:---------|
| 1 | **pandas from source (default)** | pandas + openpyxl | ~200 lines | Single-consumer analysis at small scale |
| 2 | pandas + parquet cache | +pyarrow | +10 lines | When loaders get slow |
| 3 | JSON files | extraction script | Significant query layer | Non-Python consumers, git-diffable schemas |
| 4 | CSV/Parquet cleaned tier | extraction script | Modest | Same as 3, but pandas-friendly |
| 5 | sqlite | +sqlite | Schema design | Working set exceeds memory |
| 6 | duckdb | +duckdb | Trivial | SQL preference, growing data |
| 7 | polars | +polars | Re-learn API | When pandas is a real bottleneck |
| 8 | Hosted database + ORM | Hosting + ORM + migrations | High | Multi-user web app |

## The decision, applied

For a typical small-scale analysis project — single analyst, exploratory questions, output consumed by a stakeholder as a one-shot or short-lived demo — **Option 1 is the only choice that doesn't add infrastructure for a requirement that doesn't exist yet**.

| Principle | Verdict |
|:----------|:--------|
| *Do the simplest thing that works* | Option 1 — direct read, no intermediate storage |
| *YAGNI* | Options 3–8 all build for requirements we don't have |
| *Postpone decisions* | Option 1 keeps every door open; the source files are unchanged, so we can pivot to any other option later from the same starting point |
| *Choose the path that makes change easier* | Option 1 — if any "when to revisit" signal fires, swap in cache/CSV/duckdb without re-architecting |

The trap to avoid: **picking a heavyweight option because it sounds more "real engineering"**. The project's success metric is usually *can the stakeholder see a useful result*, not *did we build production data infrastructure*. Every layer added before it's needed is a layer that must be maintained, explained, and worked around.

## The torch — what shifts this recommendation

- **Sharing.** If the cleaned data needs to leave the repo (a stakeholder wants the CSV, or a non-Python tool ingests it), evolve Option 1 → Option 4 (add a `data/clean/` export tier *as an output* of pandas, not as the storage layer).
- **Domain ambiguity in the source.** If the schema of a source is unclear (free-text headers, mixed semantics, unknown filter), the loader doing the cleaning is also doing the negotiating-with-reality. That investment is the same regardless of which storage option you pick — don't let storage debate eat the time that should go into understanding the data.

---

*A pattern: keep the storage layer at the leftmost option that still meets the requirement. Move right only when a concrete signal forces it.*
