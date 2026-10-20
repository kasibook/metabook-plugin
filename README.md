# Metabook plugin for Claude Code

Let your AI agent build real courses in [Metabook](https://meta.kasibook.com): short reading notes that teach,
spaced-repetition study decks that make it stick, and quizzes that check it — grouped into a collection,
paced for a few minutes a day, ready to study on your phone.

> "Make me a JLPT N5 course — I'm an English speaker, 20 minutes a day, exam in March."
> "Turn chapter 4 of this PDF into study cards and a quiz."
> "My Spanish deck has 600 cards and I keep forgetting them. Fix it."

## Install

```
/plugin marketplace add kasibook/metabook-plugin
/plugin install metabook@metabook
```

## Connect your account

1. In Metabook, open **Profile → API keys → New key**, tick all four permissions, and copy the key (`mb_…`).
2. In your terminal (or shell profile):
   ```bash
   export METABOOK_API_KEY=mb_...
   ```
   Keep the key out of chats and files you share. You can revoke it any time in the same screen.
3. Ask your agent to "check my Metabook connection".

## What's inside

- `skills/metabook/SKILL.md` — how to plan, write, check and push a course, and how to audit existing decks.
- `skills/metabook/references/` — course design principles, language-course patterns, card module formats, a quality checklist, the API subset.
- `skills/metabook/scripts/mb.py` — a dependency-free client (Python 3.8+): `whoami`, `ls`, `export`, `lint`, `push`, `update`, `api`.

The skill folder follows the open Agent Skills format, so it also works in other agents that support skills —
copy `skills/metabook` into their skills directory.

## Privacy

The plugin talks only to the Metabook API with your key. Your agent writes the content; Metabook stores it.

MIT licensed.
