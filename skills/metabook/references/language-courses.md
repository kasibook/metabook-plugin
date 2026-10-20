# Language courses

Write all explanations, translations and notes in the **learner's** language (ask if unclear).

## Recommended collection layout

1. 📖 **Grammar notes** (reading) — one short note per grammar point, textbook order.
2. 🧠 **Script** (study), if the language has its own (kana, hangul, Thai, Cyrillic…) — before anything else.
3. 🧠 **Vocabulary** (study), split into themed decks of 40–80 words (greetings, food, travel, work…),
   most frequent words first.
4. 🧠 **Grammar practice** (study) — sentence-level cards per grammar point (cloze, transform, translate).
5. 🎧 **Listening** (study), if speech is available for the language — audio prompt → pick/type the meaning.
6. 📝 **Unit quizzes** (quiz) — mixed questions per unit, plus a final mock test for exams.

## Vocabulary cards

- **Recognition card** (target → meaning): front = the word (+ `tts` so they hear it); back = meaning,
  reading/pronunciation if not obvious, one short example sentence (target language + translation, `tts` of the sentence).
- **Production card** (meaning → target): front = meaning in the learner's language + a `text_input` for typing
  the word; back = the word + `tts`. Add `accepted_answers` for alternative spellings / romanisation
  (e.g. kana answer with `["taberu"]`; Japanese long vowels both ways: `"gakkou"`, `"gakkoo"`).
- **Listening card**: front = `tts` with `"show_text": false, "autoplay": true` + `multi_select` of meanings; back = the text + meaning.
- Put tricky points in `explanation_content`: irregular forms, false friends, politeness level, confusable words.

## Writing systems

- Show the native script everywhere. Romanisation (romaji, pinyin, RTGS…) only as a small helper in brackets
  on the back, or in beginner-level script drills — it becomes a crutch otherwise.
- Kanji/hanzi words: give the reading — `食べる（たべる）`. If the learner already reads Chinese characters,
  the hard part is the *reading*: test "how is 食べる read?" rather than the meaning.
- Speech modules must contain the native script, never romanisation (a Japanese voice reading "tabemasu" sounds wrong).

## Speech support

`tts` / `dictation` / `speak` only support `en-US`, `ja`, `zh-CN`, `th-TH`. For other target languages,
use `text` (and IPA or a simple pronunciation hint in brackets), and tell the user audio isn't available for that language.
Use `speak` (speaking practice with speech recognition) only if the user wants it — many learners study in public.

## Grammar cards

- A cloze in a natural sentence (`彼は毎日{{c1::学校に}}行きます。`) with the translation on the back and the rule in the explanation.
- Transformation: "Make it past tense: 食べます → ?" with `text_input` and accepted answers.
- Anything the learner types in a non-Latin script needs `text_input` with romanised `accepted_answers` — many
  learners have no native keyboard; cloze blanks accept only the exact answer.
- Minimal pairs for confusions (は vs が, ser vs estar, a vs the): one card each side, explanation contrasts them.

## Typical pace

Beginners: 8–12 new words/day + 2–3 grammar cards/day + 2–3 notes/day ≈ 15–20 min/day.
