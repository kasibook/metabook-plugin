# Quality checklist

Use this after `mb.py lint` passes (lint catches format problems; this is about learning value).
Read ~10 cards spread across each deck as the learner would see them.

## Content
- [ ] Every fact, translation, reading and answer is correct. When unsure, leave it out.
- [ ] Each study card asks for one thing, answerable from memory in a few seconds.
- [ ] Backs give the answer first, then a short example or context.
- [ ] Cards with rules, exceptions or confusables have `explanation_content` (aim for ≥ 50 % of grammar/concept cards).
- [ ] No near-duplicate cards; no cards that give away the answer on the front.
- [ ] Explanations are in the learner's language.

## Course
- [ ] Theory exists: a reading deck (or notes) explains what the study cards test.
- [ ] Decks and cards are in learning order.
- [ ] Production / application cards exist where the goal needs them.
- [ ] Quizzes use new questions, every card has an interactive module and an explanation.
- [ ] Daily load: sum of `daily_new_cards` fits the learner (≈10–15 casual, 20–30 serious); notes 2–3/day.
- [ ] Collection and every deck have a description saying what it covers and when to use it.
- [ ] Every card has topic tags.

## Format
- [ ] Plain text only: no `**`, `#`, backticks — use line breaks and `• ` bullets.
- [ ] Speech modules use a supported language and the native script.
- [ ] Reading notes ≤ ~200 words; long topics split.
- [ ] Multiple choice: 3–4 plausible options, correct answers copied exactly from the options.

## Common failures seen in real decks
- Hundreds of cards, zero explanations → learners memorise answers without understanding.
- Only target → meaning cards → learners can recognise but never produce.
- Romanised text sent to a Japanese/Chinese/Thai voice → nonsense audio.
- A quiz that repeats the study cards word-for-word → tests memory of the card, not the skill.
- 40 new cards/day per deck × 5 decks → a review backlog of hundreds within a week.
- Markdown in text modules → asterisks and hashes shown on the card.
