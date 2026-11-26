# Keep structure apart from styling

> A component says what is on the screen; a stylesheet says what it looks like.

A component holds structure only: which elements appear, in what order, and what state each is in. Its look, such as colours, spacing, sizes and fonts, comes from stylesheets that can be replaced without touching the component. When the two are mixed, every change of look means editing the component, the same colour ends up written into many components, and a redesign turns into a search through every file that draws something.

## The test

Before writing a colour, size or spacing value, ask: **could the look of this component be replaced without editing the component?** If it could, keep going. If it couldn't, move the value into a stylesheet and give the component a class name that says what the element is, not what it looks like.

## Worked example: a button that carries its own look

A form needs a save button. The author writes the look straight into the component, because it keeps everything about the button in one file and there is only one button.

```jsx
// Before: the look is written into the component
function SaveButton({ onSave }) {
  return (
    <button
      onClick={onSave}
      style={{ background: "#0a6", color: "#fff", padding: "8px 16px", borderRadius: 4 }}
    >
      Save
    </button>
  );
}

// After: the component holds structure, and the stylesheet holds the look
function SaveButton({ onSave }) {
  return <button className="button-primary" onClick={onSave}>Save</button>;
}
```

```css
/* buttons.css */
.button-primary {
  background: var(--colour-action);
  color: var(--colour-on-action);
  padding: 8px 16px;
  border-radius: 4px;
}
```

The component now says one thing: there is a primary button labelled Save that calls `onSave`. It behaves exactly as before. When a second form needs a primary button, it uses the same class instead of copying four values. When the product changes its colours, or a dark theme arrives, the stylesheet changes and no component is opened.

## Where it stops

<mark>Keeping structure apart from styling doesn't stop a component saying which state it is in; it stops the component saying what that state looks like.</mark> A button may add a `disabled` or `error` class when its state calls for it, because the state is structure. What a disabled button looks like belongs in the stylesheet. Nor does it mean one stylesheet per component from the start: where the look lives is a question of when it has earned its own file, which [Earn the split](avoid-premature-organisation.md) answers.

## Related

- [Keep each concern in one place](separation-of-concerns.md): structure and styling are two concerns, and this is one case of keeping them apart.
- [Put one thing in each file](one-thing-per-file.md): the component and its stylesheet each have their own reason to change.
- [Write each fact once](dont-repeat-yourself.md): a colour used by many components is a fact, so it is written once as a shared value.

## Source

No longer source exists; written fresh for the pack, worked example included.
