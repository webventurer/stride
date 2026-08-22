# Conventions

**How work is specified and checked here.** A card says what must be true when it is done. A package says what it owns. Either may propose how — neither makes it a condition of being done.

The first four shape change: make the next change easier, declare the result and boundary, derive the current route, and give the responsibility one home. The rest keep the set honest through consistency checks and the habit of asking to be proved wrong.

| Convention | Core idea | Link |
|:--|:--|:--|
| **Make future change easier** | Meaningful simplification leaves the next change touching fewer concepts and fewer places | [make-future-change-easier](make-future-change-easier.md) |
| **Specify the result, not the edit** | A card declares the state that must hold, not the changes that produce it | [specify-the-result-not-the-edit](specify-the-result-not-the-edit.md) |
| **Derive the plan when work starts** | The card defines done; the current repository determines the implementation route | [derive-the-plan-when-work-starts](derive-the-plan-when-work-starts.md) |
| **Give each responsibility one visible home** | One responsibility, one sentence, one place to look | [give-each-responsibility-one-visible-home](give-each-responsibility-one-visible-home.md) |
| **Keep every restatement true** | A rule stated twice is a fact with copies, and copies drift | [keep-every-restatement-true](keep-every-restatement-true.md) |
| **Read the set as one document** | Read every document together after a change; contradictions are findings | [read-the-set-as-one-document](read-the-set-as-one-document.md) |
| **Ask for the disproof** | State the hypothesis, then ask for it to be broken | [ask-for-the-disproof](ask-for-the-disproof.md) |

New conventions copy [template.md](template.md).

## Card checklist

1. Can the outcome be stated without filenames? An expected shape may name them; the outcome may not
2. Does the specification describe observable completion?
3. Is there exactly one responsibility?
4. Is its boundary explicit?
5. Are package/module choices proportional to the code that exists now?
6. Could another implementation satisfy the same specification?
7. Does the result or expected shape make the next change easier, or merely make this change smaller?
8. Does every place that restates a changed rule still agree with it?
9. Read end to end, does the set contradict itself anywhere?
10. Was the implementation checklist derived from the current repository rather than frozen into the card?

---

_Say what must be true. Let the implementation earn its own shape._
