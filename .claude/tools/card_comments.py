"""
Turns a card's comments into the file the end card check hands its reviewers.

The reviewers can't reach Linear themselves, so the check saves the comments
beside the card file. A card with no comments gives an empty file.
"""


def comments_text(comments: list[dict]) -> str:
    ordered = sorted(comments, key=lambda comment: comment["createdAt"])
    return "\n".join(comment_block(comment) for comment in ordered)


def comment_block(comment: dict) -> str:
    author = (comment.get("user") or {}).get("name", "unknown")
    return f"### {author}, {comment['createdAt']}\n\n{comment['body']}\n"
