# TODO

## Add image verification to verify.py

`verify.py` covers titles, descriptions, and comments but doesn't verify that inline images survived migration. linear-to-linear's `compare.py` does this as a separate deep-comparison script, but trello-to-linear's `verify.py` already handles most of what both scripts do — so adding image validation as a fourth section is likely the right move rather than a separate `compare.py`.

**What to check:**
- Trello card attachments that were image types appear as inline `![alt](url)` in the Linear description
- Uploaded image URLs resolve (not broken `uploads.linear.app` links)

**What to consider from linear-to-linear's compare.py:**
- Content tolerance (100-char leeway for minor formatting differences)
- `--fix` flag for auto-repair of missing images (re-upload from Trello source)

**Why not a separate compare.py:**
- `verify.py` already fetches every issue individually, builds expected content, and reports across named sections
- Adding an "Images" section follows the existing `SectionResult` / named-sections-dict pattern
- Trello boards have minimal project-level metadata, so the project comparison piece from linear-to-linear doesn't apply
