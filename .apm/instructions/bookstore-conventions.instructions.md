---
description: Bookstore API conventions that every change must follow
applyTo: "**"
---

# Bookstore conventions

- Commit messages are imperative, present tense ("Add", "Fix", "Remove"), so
  the changelog can be generated from history.
- `CHANGELOG.md` follows Common Changelog; update it through the `changelog`
  skill, never by hand during a commit.
- Any change to an HTTP handler or a store function gets a security review
  by the `security-auditor` agent before it is merged.
