# Designing a course that works

These are the principles behind good Metabook courses. They come from auditing real learners' decks: the
most common failure is not bad cards, it's a pile of cards that *tests* without ever *teaching*, served
faster than anyone can keep up with.

## 1. Teach, then practise, then check

For each unit of the subject:

1. **Reading notes** explain it: the rule, why it works that way, 2–4 examples, the common mistakes.
2. **Study cards** make the pieces stick, one small fact per card.
3. **A quiz** at the end of a unit checks understanding with fresh questions.

A study deck with no notes behind it forces the learner to reverse-engineer the rules from the answers.
A reading deck with no study cards is forgotten within a week.

## 2. One idea per study card, and make it *recallable*

- The front asks for exactly one thing; the back answers it in a few words, then adds context.
- Prefer questions the learner can actually answer from memory over "explain everything about X".
- Split lists: "the 3 types of muscle" → one card per type, plus at most one card asking for the list.
- Cloze works well for facts inside a sentence — but blank the important word, not a trivial one.
- Avoid yes/no study cards; they are 50 % guessable. Use them in quizzes only, with an explanation.

## 3. Always give the "why"

Add `explanation_content` to every card where a learner could get it right for the wrong reason or wrong
without knowing why: rules, exceptions, look-alikes, false friends, anything confusing. One or two sentences.
In reviews it sits behind a "Show explanation" button, so it costs nothing when not needed.

## 4. Context beats isolation

Every fact or word gets one short, natural example on the back (a sentence, a worked number, a real case).
Examples are what make cards memorable and usable outside the app.

## 5. Both directions for things the learner must *produce*

Recognition (see X → know what it means) is easier than production (need X → come up with it).
If the goal includes producing it (speaking/writing a language, writing formulas, naming structures),
add production cards for the most useful items — typically 30–50 % of a vocabulary deck, in a later deck
or after the recognition cards.

## 6. Pace: a load the learner can sustain

- Each new study card costs roughly 5–10 reviews over the following month. New cards/day × 7 ≈ reviews/day after a few weeks.
- Casual learner: 10–15 new cards/day **across all decks**. Serious: 20–30. Set each study deck's `daily_new_cards` so the sum fits.
- Reading decks: `daily_reading_goal` 2–3 notes/day.
- Tell the user the resulting daily time (~10 s per review, ~1–2 min per note) and the finish date.
- A course that dumps 300 new cards on day one creates a backlog the learner never clears and quits over.

## 7. Order is part of the teaching

- Decks in the collection: in the order the learner should start them (notes first, foundations before applications, quiz last).
- Cards inside a deck: simplest / most frequent / most useful first. Study decks introduce new cards in file order.
- Reading notes: like chapters in a good textbook — overview first, each note building on the previous ones.

## 8. Reading notes: short and skimmable

- One topic per note, **≤ ~200 words (one or two phone screens)**. Split longer topics into "(1/2)", "(2/2)".
- Front: a clear title. Back: 1–3 text modules — the explanation, then "Examples" (short lines starting with `• `),
  then "Common mistakes" (lines starting with `✗ `). `explanation_content`: the one-sentence key point.
- 20+ notes is fine — the app shows a contents list, saves progress and serves them a few per day.

## 9. Quizzes test understanding, not memory of the exact card

- Every quiz card needs an interactive module (multiple choice, typing, cloze, matching, ordering, true/false) —
  otherwise it is display-only and always counts as correct.
- Write new questions that apply the material (a new sentence, a new problem) instead of copying study cards.
- Multiple choice: 3–4 options, distractors that reflect real misconceptions, one clearly correct answer
  (or `allow_multiple: true` and say "choose all that apply"). Options appear in the order written, so spread
  the correct answer across positions, and keep options a similar length (the longest option shouldn't
  give the answer away).
- Explain each answer in `explanation_content` — the quiz is also a teaching moment.
- 10–25 questions per quiz.

## 10. Tags and descriptions

- Tag every card with the topic (kebab-case: `cell-biology`, `past-tense`) so learners can drill a topic later.
- Every deck and the collection get a 1–2 sentence description: what it covers and how to use it ("study after reading notes 1–5").

## 11. When starting from the user's material

- The material is the source of truth: cover what it emphasises, keep its terminology, examples and level.
- Don't pad with outside facts; if the material has gaps the learner will need, say so and offer to add them separately.
- "Common mistakes" should be the ones the material warns about or that are well known — don't invent new ones.
- Exams with written answers: add a few study cards that ask for the explanation itself ("Explain how … "),
  with a model answer on the back.
- Long material: plan by its chapters/sections; one reading note per subsection, study cards for its key facts,
  a quiz per chapter.
