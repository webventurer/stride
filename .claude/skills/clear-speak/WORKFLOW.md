# Clear speak workflow

> **AI Assistant Note**: When writing or reviewing stride's own output — command files, issue drafts, commit messages, README text — apply this workflow to replace jargon with concrete, immediately understandable language. Proactively suggest clear-speak alternatives when you notice abstract or academic terms.

Replace fancy words with ones that land immediately. Academic language creates barriers. Clear speak creates understanding.

---

## Background reading

The essentials are inlined below. Open a full document only when you need its deeper detail or examples — don't load all three on every rewrite:

1. **George Orwell's six rules** — `writing/george-orwell-rules-for-writing.md`
   - Never use a long word where a short one will do
   - Never use jargon if you can think of an everyday equivalent
   - If you can cut a word out, cut it out

2. **Write clearly, simply, with action** — `writing/write-clearly-simply-with-action.md`
   - Use everyday words over jargon
   - One idea per sentence
   - Tell people what to DO, not just what to know

3. **Headings guide, vocabulary inside** — `writing/headings-guide-vocabulary-inside.md`
   - Plain headings for scanning
   - Precise terms introduced in the content, not the heading

---

## The transformation process

### Step 1: Spot the jargon

Look for these warning signs:

- **Latin or Greek roots**: "pedagogical", "synthesize", "articulate"
- **-tion/-ment/-ism suffixes**: "enumeration", "assessment", "mechanism"
- **Abstract nouns**: "facilitation", "implementation", "optimization"
- **Compound academic phrases**: "cognitive mode", "architectural analysis"
- **Bare code identifiers in prose**: `migrate_from_legacy()`, `bearer_token` — name the behaviour, not the symbol
- **Words you'd never say out loud**: if you wouldn't say it in conversation, don't write it

### Step 2: Ask the replacement question

For each suspect word, ask:

> **"How would I explain this to a smart friend who doesn't know this field?"**

The answer is usually your clear-speak version.

### Step 3: Apply the transformation

| Pattern | Jargon | Clear speak |
|:--------|:-------|:------------|
| Action hiding as noun | "Perform enumeration of" | "List" |
| Latin verb | "Synthesize" | "Pull together" |
| Greek adjective | "Pedagogical" | "Teaching" or "learning" |
| Code identifier in prose | "`migrate_from_legacy()` runs" | "The settings upgrade runs" |
| Compound phrase | "Architectural analysis" | "Map the shape" |
| -tion noun | "Facilitation" | "Help" |
| -ment noun | "Assessment" | "Check" or "review" |

---

## Before and after examples

### From stride's own output

| Before (jargon) | After (clear speak) |
|:----------------|:--------------------|
| `migrate_from_legacy()` deletes the legacy config unconditionally | The settings upgrade deletes your old file even when something went wrong halfway |
| Add a parse-before-delete guard | Check the old file is readable before deleting it |
| The lazy migration trigger fires from credential lookup | The upgrade runs on its own the first time a command needs your login |
| Removes dead code | Removes code nothing uses anymore |
| Idempotent re-install dedupes hooks | Running the install twice is safe — it won't add the same hook again |

### Common transformations

| Jargon | Clear speak |
|:-------|:------------|
| Utilize | Use |
| Facilitate | Help |
| Implement | Build / Do |
| Leverage | Use |
| Articulate | Say / Explain |
| Synthesize | Pull together |
| Optimize | Improve / Speed up |
| Validate | Check |
| Instantiate | Create |
| Iterate | Repeat / Go again |
| Prioritize | Rank / Put first |
| Contextualize | Explain the background |
| Conceptualize | Think through |
| Operationalize | Put into practice |

---

## Red flags checklist

When reviewing content, flag these patterns:

- [ ] Words ending in -ization, -ification, -ation
- [ ] Words ending in -ological, -istical
- [ ] Phrases like "in terms of", "with respect to"
- [ ] "Utilize" instead of "use"
- [ ] "Facilitate" instead of "help"
- [ ] "Leverage" instead of "use"
- [ ] A bare function or variable name where a plain description would do
- [ ] Any word you'd need to define for a newcomer
- [ ] Compound phrases that could be one simple word

---

## The exceptions

Some technical terms earn their place:

**Keep when:**
- The term is genuinely precise and has no simpler equivalent
- The audience expects and understands the term
- Simplifying would lose important meaning
- It's a proper noun or established name

**Replace when:**
- A simpler word means the same thing
- The fancy word is just habit or showing off
- Newcomers would stumble on it
- You're writing for a general audience

<mark>**Keep the precise term, add the plain gloss — never strip the precise word.**</mark> When a term is load-bearing (e.g. "atomic commit"), give it a one-line plain explanation the first time, then use it freely. Don't delete it for a vaguer phrase.

---

## Quality check

After applying clear speak, verify:

- [ ] **The 16-year-old test**: would a smart 16-year-old understand this?
- [ ] **The conversation test**: would you say this out loud to a friend?
- [ ] **The speed test**: can readers understand it on first read?
- [ ] **The meaning test**: did you preserve the actual meaning?

---

## The deeper principle

Academic language often masks unclear thinking. When you're forced to say something simply, you discover whether you actually understand it.

Clear speak isn't dumbing down. It's thinking through.

> **"If you can't explain it simply, you don't understand it well enough."**
> — Often attributed to Einstein

---

_Fancy words hide. Plain words land._
