# Put one thing in each file

> Give each component, class or module its own file, named for the thing it holds.

A file that holds one thing, such as one component, can be found by its name, read without scrolling past its neighbours, and changed without touching them. Its history and its diffs show changes to that thing alone. When several things share a file, a reader has to open the file to learn what is in it, a change to one shows up in the history of the others, and code elsewhere that needs one of them has to import it from a file named after something else. A thing earns its own file once it has its own reason to change; until then it can stay beside the thing it serves.

## The test

Before adding a second component, class or module to a file, or when one already in a file gains a new user, ask: **does this thing have its own reason to change?** A caller outside this file is the usual sign that it does.

- If it does, give it its own file, named for it.
- If it is a helper that serves only the file's main thing and changes when that thing changes, it stays where it is.

## Worked example: an invoice page that grew

An invoice page was built in one file while its shape was still unclear, which was the right call at the time. It now holds the page, a table of invoice lines and a pay button, and the order page has started using the same pay button.

```text
# Before: three components in one file, one of them used elsewhere
InvoicePage.tsx
├── InvoicePage     the page layout
├── InvoiceTable    the table of invoice lines
│   └── lineTotal   works out one line's total
└── PayButton       also imported by OrderPage.tsx

# After: each component in its own file, named for it
InvoicePage.tsx     the page layout
InvoiceTable.tsx    the table of invoice lines
  └── lineTotal     stays: only the table uses it, and it changes with it
PayButton.tsx       imported by InvoicePage.tsx and OrderPage.tsx
```

In the before, the order page imports `PayButton` from `InvoicePage.tsx`, so a reader looking for the button has to know it lives in the invoice page, and every change to the button lands in the invoice page's history. In the after, each file's name says what is in it, a change to the button touches only `PayButton.tsx`, and the order page imports it from a file named for it. The table moves too, because what an invoice line shows changes for different reasons from how the page is laid out. The `lineTotal` helper stays inside `InvoiceTable.tsx`, because it has no reason to change apart from the table. When the table gains a second helper, it joins `lineTotal` rather than getting a file of its own.

## Where it stops

<mark>One thing per file does not mean one function per file.</mark> The thing is a component, class or module with its own reason to change; the small helpers that serve it and change with it belong in its file. Splitting every helper out leaves a folder of fragments that has to be opened file by file to read one thing.

When a new thing has earned its own file is set out in [earn the split](avoid-premature-organisation.md).

## Related

- [Earn the split](avoid-premature-organisation.md): when a thing has shown it needs its own file.
- [Give each piece of code one reason to change](single-responsibility-principle.md): what makes something one thing.
- [Keep each concern in one place](separation-of-concerns.md): the same idea for a worry that spans several files.
- [Name things for what they do](name-things-for-what-they-do.md): the file's name is the thing's name, so it carries the same care.

## Source

No longer source exists; written fresh for the pack.
