# Card content: modules

A card has `front_content`, `back_content` and optional `explanation_content`, each a list of modules.
Use exactly these field names — the server rejects wrong ones with a 422 that names the right field.
Full reference (always current): https://meta.kasibook.com/api/docs/features/MODULAR_FLASHCARDS.md

## Display modules

| Module | Example | Notes |
|---|---|---|
| text | `{"type":"text","content":"The capital of France"}` | Line breaks kept, ≤10 000 chars. Light markdown: `**bold**`, `*italic*`, `# heading` (1–3 #), `- item`, `` `code` ``, `[link](https://…)`. No tables/code blocks. Also in `hint` and explanations. |
| tts | `{"type":"tts","text":"ありがとう","lang":"ja","autoplay":false,"show_text":true,"rate":0.9}` | Read aloud by the device. `lang`: `en-US`, `ja`, `zh-CN`, `th-TH` only. `text` must be in that language's script. `show_text:false` + `autoplay:true` = a listening prompt. |
| hint | `{"type":"hint","content":"Think of the verb tense"}` | Collapsed "Show hint" button. A nudge, never the answer. |
| image / audio | `{"type":"image","media":{"id":"<uuid>"},"alt":"…"}` | Upload first (`POST /api/uploads/`, multipart `file`) — no external URLs. |
| image_occlusion | `{"type":"image_occlusion","media":{"id":"<uuid>"},"masks":[{"x":0.1,"y":0.2,"w":0.3,"h":0.1,"label":"Aorta"}]}` | Boxes (fractions 0–1) hide labels on a diagram. |

## Interactive modules (graded in quizzes; self-check in study decks)

| Module | Example | Notes |
|---|---|---|
| text_input | `{"type":"text_input","correct_answer":"たべる","accepted_answers":["taberu"],"placeholder":"Type the reading"}` | Comparison ignores case, punctuation, apostrophe style and spaces. `accepted_answers` (≤10) also count: romaji next to kana, synonyms, British/US spelling. Put the question in a `text` module before it. |
| multi_select | `{"type":"multi_select","options":["Paris","Lyon","Nice"],"correct_answers":["Paris"],"allow_multiple":false}` | `correct_answers` repeat option **texts** exactly. 3–4 plausible options. The app shuffles the options ("all/none of the above" stays last), so their written order doesn't matter. |
| cloze | `{"type":"cloze","text":"Water boils at {{c1::100}} °C at {{c2::sea level}}."}` | Double colon. Hints: `{{c1::answer::hint}}`. Only the exact blank text counts (case/punctuation-insensitive) — when learners might type an alternative (romaji, a synonym), use `text_input` with `accepted_answers` instead. |
| true_false | `{"type":"true_false","statement":"Spiders are insects.","correct":false}` | Explain why on the back. |
| matching | `{"type":"matching","pairs":[{"left":"dog","right":"犬"},{"left":"cat","right":"猫"}]}` | 3–6 pairs; the app shuffles. |
| ordering | `{"type":"ordering","items":["Mitosis","Cytokinesis"],"correctOrder":[0,1]}` | `correctOrder` = indices in the right order. |
| dictation | `{"type":"dictation","text":"Where is the station?","lang":"en-US"}` | Spoken and hidden; learner types what they hear. Front only. |
| speak | `{"type":"speak","text":"Good morning","lang":"en-US"}` | Learner says it aloud (speech recognition). Only the four speech languages; skip it unless the user wants speaking practice. |

## Patterns

Study card (recall):
```json
{"front_content":[{"type":"text","content":"What does ATP stand for?"}],
 "back_content":[{"type":"text","content":"Adenosine triphosphate — the cell's energy currency."}],
 "explanation_content":[{"type":"text","content":"Energy is released when the third phosphate bond breaks (ATP → ADP)."}],
 "tags":["biology","cell-energy"]}
```

Quiz card (one interactive module; explanation shown after grading):
```json
{"front_content":[{"type":"text","content":"Which organelle makes most of a cell's ATP?"},
                  {"type":"multi_select","options":["Ribosome","Golgi body","Mitochondrion","Nucleus"],"correct_answers":["Mitochondrion"],"allow_multiple":false}],
 "back_content":[{"type":"text","content":"Mitochondrion"}],
 "explanation_content":[{"type":"text","content":"Ribosomes make proteins; the Golgi packages them."}],
 "tags":["biology"]}
```

Reading note (title on the front, body on the back, key point as explanation):
```json
{"front_content":[{"type":"text","content":"How enzymes speed up reactions"}],
 "back_content":[{"type":"text","content":"Enzymes are proteins that lower the activation energy…\n\nExamples\n• Amylase breaks starch into sugars.\n• Catalase splits hydrogen peroxide."},
                 {"type":"text","content":"Common mistakes\n✗ Enzymes are not used up by the reaction."}],
 "explanation_content":[{"type":"text","content":"Enzymes lower the energy needed to start a reaction; they don't change its result."}],
 "tags":["biology","enzymes"]}
```
In reading notes, a short first line followed by more lines shows as a sub-heading ("Examples"), and lines starting
with `• `, `✓ ` or `✗ ` show as list items. A `✗ ` line states the *wrong* belief or usage (shown in red) —
follow it with the correction, never use it for a true fact.
