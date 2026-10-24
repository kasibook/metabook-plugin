# Metabook API — the parts this skill uses

Base URL `https://meta.kasibook.com/api` (or `$METABOOK_API_URL`). Every request: `Authorization: Bearer $METABOOK_API_KEY`.
JSON in and out. Paths work with or without a trailing slash. Full docs (fetch when you need more):

- Agent playbook: https://meta.kasibook.com/api/docs/AGENTS.md
- Every endpoint: https://meta.kasibook.com/api/docs/backend/API.md
- Card modules: https://meta.kasibook.com/api/docs/features/MODULAR_FLASHCARDS.md
- Quizzes: https://meta.kasibook.com/api/docs/features/QUIZ_SYSTEM.md
- OpenAPI schema: https://meta.kasibook.com/openapi.json

`mb.py api METHOD PATH [JSON|@file]` calls any endpoint with the key attached.

## Reading
| Call | Returns |
|---|---|
| `GET /auth/me` | the account (username, timezone) — works with any key |
| `GET /collections` | collections with deck/card counts |
| `GET /collections/{id}` | one collection + its decks in order |
| `GET /decks?limit=500` | all decks with `card_count`, `due_count`, `collection_id` |
| `GET /flashcards?deck_id={id}&limit=500` | a deck's cards (reading/quiz decks in deck order), each with `reps`, `lapses`, `state`, `due`, `last_review` |
| `GET /flashcards?q=text&tags=a` | search |

## Writing
| Call | Body / notes |
|---|---|
| `POST /collections` | `{name, description?, emoji?, color?, language?, level?}` → 201 |
| `POST /decks` | `{name, deck_type, description?, language?, level?, collection_id?, quiz_config?, daily_new_cards? (study), daily_reading_goal? (reading)}` → 201 |
| `PATCH /decks/{id}` | `{daily_new_cards?, daily_reading_goal?, name?, description?, …}` |
| `POST /collections/{id}/decks` | `{deck_ids: [...]}` — add existing ungrouped decks |
| `POST /flashcards/batch` | `{cards: [1–100 × {deck_id, front_content, back_content, explanation_content?, tags?}]}` → always 200, per-card `results[{index, success, flashcard_id, errors[{path,msg}]}]` |
| `PATCH /flashcards/{id}` | any of `front_content, back_content, explanation_content, tags, deck_id` (replaces those fields; keeps review history) |
| `DELETE /flashcards/{id}`, `DELETE /decks/{id}` | permanent — only when the user asks |
| `POST /collections/{id}/share` | `{is_public, allow_copy}` → `share_token`; link `https://meta.kasibook.com/shared/collection/{token}` |

## Errors
- 401 bad/expired key · 403 key lacks a permission · 404 not found or not yours · 422 invalid (read `detail[].path` and `msg` — it names the fix) · 429 slow down (honour `Retry-After`; `mb.py` retries automatically).

## Studying from the agent (rarely needed — the app does this better)
- Due cards: `GET /reviews/due?deck_id=` → show front, collect recall, `POST /reviews/submit {flashcard_id, rating 1–4, expected_reps, client_review_id}`.
- Quiz: `POST /quizzes/start {deck_id}` → `POST /quizzes/{id}/submit {flashcard_id, user_answer}` → `POST /quizzes/{id}/complete`. Answer shapes: QUIZ_SYSTEM.md.
