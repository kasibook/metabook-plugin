# Course file format (for `mb.py push` / `mb.py lint`)

```json
{
  "collection": {
    "name": "Japanese — JLPT N5",
    "description": "A complete N5 course. Read one grammar note a day, study the decks in order, take the unit quiz at the end of each unit.",
    "emoji": "🇯🇵",
    "color": "rose",
    "language": "ja",
    "level": "beginner"
  },
  "decks": [
    {
      "name": "N5 Grammar notes — read first",
      "description": "Short lessons on every N5 grammar point, in textbook order.",
      "deck_type": "reading",
      "daily_reading_goal": 3,
      "cards": [
        {"front_content": [{"type": "text", "content": "は — the topic marker"}],
         "back_content": [{"type": "text", "content": "は (read \"wa\") marks what the sentence is about…"}],
         "explanation_content": [{"type": "text", "content": "は = \"as for…\"; it sets the topic, not the subject."}],
         "tags": ["grammar", "particles"]}
      ]
    },
    {
      "name": "N5 Vocabulary 1 — people & places",
      "description": "…",
      "deck_type": "study",
      "daily_new_cards": 8,
      "cards": [ … ]
    },
    {
      "name": "Unit 1 check",
      "deck_type": "quiz",
      "quiz_config": {"scoring_methods": ["percentage", "letter_grade"], "time_per_question_seconds": 60},
      "cards": [ … ]
    }
  ]
}
```

Fields:

- `collection` (optional): `name` (required), `description`, `emoji` (one emoji), `color` (`violet blue sky teal
  emerald lime amber orange rose pink slate`), `language` (`en th zh ja ko es fr de vi other` — the language
  being learned/the content language), `level` (`beginner intermediate advanced`). Omit `collection` to create ungrouped decks.
- `collection_id` (optional, instead of `collection`): add the new decks to an existing collection.
- Deck: `name`, `deck_type` (`study` default, `quiz`, `reading`), `description`, `language`, `level`;
  `daily_new_cards` (study, 1–9999; app default 10), `daily_reading_goal` (reading, 1–50; default 3),
  `quiz_config` (quiz; optional: `scoring_methods` ⊆ `percentage letter_grade detailed`, `time_limit_seconds`,
  `time_per_question_seconds`, `show_timer`).
- `deck_id` on a deck entry: append its `cards` to that existing deck instead of creating one.
- Card: `front_content`, `back_content` (1–50 modules each), optional `explanation_content` (null or modules), `tags` (list of strings, 1–50 chars each).

Order matters: decks are added to the collection in file order; cards are created in file order.

## Changes file (for `mb.py update`)

```json
{
  "deck_type": "study",
  "cards": [
    {"id": 1234, "back_content": [...], "explanation_content": [...]},
    {"id": 1235, "tags": ["verbs", "n5"]}
  ],
  "new_cards": [
    {"deck_id": 42, "front_content": [...], "back_content": [...], "tags": ["verbs"]}
  ]
}
```

Only the fields you include are changed (faces and tags are replaced as a whole). `deck_type` tells the linter which
rules apply. Editing a card keeps its review history and schedule.
