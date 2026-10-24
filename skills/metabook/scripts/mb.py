#!/usr/bin/env python3
"""mb — a small, dependency-free client for the Metabook API.

Reads the API key from the METABOOK_API_KEY environment variable (never pass it
on the command line) and the base URL from METABOOK_API_URL (default
https://meta.kasibook.com/api).

Commands
  whoami                         check the key; show the account
  ls                             list collections and decks (ids, types, card counts)
  export DECK_ID [-o FILE]       a deck and all its cards as JSON (for auditing / editing)
  export-collection ID [-o FILE] a collection, its decks and all their cards
  lint FILE.json                 check a course or changes file locally (no network)
  push COURSE.json [--dry-run]   lint, then create the collection / decks / cards
  update CHANGES.json            apply card edits from an audit (PATCH by card id)
  api METHOD PATH [JSON|@FILE]   raw call, e.g.  api GET /decks/12   api POST /flashcards/batch @cards.json

Course file format: see references/course-format.md. Exit code 0 = ok, 1 = problems.
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API = os.environ.get("METABOOK_API_URL", "https://meta.kasibook.com/api").rstrip("/")
APP = re.sub(r"/api$", "", API)
BATCH = 100

# ── HTTP ──────────────────────────────────────────────────────────────────────


def _key():
    key = os.environ.get("METABOOK_API_KEY", "").strip()
    if not key:
        sys.exit(
            "METABOOK_API_KEY is not set.\n"
            "Create a key in Metabook (Profile → API keys, all four permissions), then in your shell:\n"
            "  export METABOOK_API_KEY=mb_...\n"
            "Do not paste the key into the chat."
        )
    return key


def call(method, path, body=None, retries=3):
    url = API + (path if path.startswith("/") else "/" + path)
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=data, method=method.upper())
        req.add_header("Authorization", "Bearer " + _key())
        req.add_header("Accept", "application/json")
        req.add_header("User-Agent", "metabook-plugin/0.2")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
                return r.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                payload = json.loads(raw) if raw else None
            except ValueError:
                payload = raw.decode(errors="replace")
            if e.code in (429, 502, 503, 504) and attempt < retries:
                time.sleep(float(e.headers.get("Retry-After") or 2 * (attempt + 1)))
                continue
            return e.code, payload
        except urllib.error.URLError as e:
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
                continue
            sys.exit(f"Cannot reach {API}: {e.reason}")


def must(method, path, body=None):
    status, payload = call(method, path, body)
    if status >= 400:
        detail = payload.get("detail") if isinstance(payload, dict) else payload
        hint = {
            401: " (key missing, wrong, revoked or expired)",
            403: " (the key lacks a permission — give it decks:read/write and cards:read/write)",
        }.get(status, "")
        sys.exit(f"{method} {path} → {status}{hint}: {json.dumps(detail, ensure_ascii=False)[:1500]}")
    return payload


# ── Lint ──────────────────────────────────────────────────────────────────────

TTS_LANGS = {"en-US", "th-TH", "zh-CN", "ja"}
TTS_ALIASES = {"en": "en-US", "en-us": "en-US", "en-gb": "en-US", "th": "th-TH", "th-th": "th-TH",
               "zh": "zh-CN", "zh-cn": "zh-CN", "zh-hans": "zh-CN", "cmn": "zh-CN", "ja": "ja", "ja-jp": "ja"}
INTERACTIVE = {"text_input", "multi_select", "cloze", "true_false", "matching", "ordering", "speak", "dictation"}
DISPLAY = {"text", "tts", "image", "audio", "hint", "image_occlusion"}
REQUIRED = {
    "text": ["content"], "hint": ["content"], "tts": ["text"], "cloze": ["text"], "true_false": ["statement", "correct"],
    "multi_select": ["options", "correct_answers"], "matching": ["pairs"], "ordering": ["items", "correctOrder"],
    "speak": ["text"], "dictation": ["text"], "image": ["media"], "audio": ["media"], "image_occlusion": ["media", "masks"],
    "text_input": [],
}
WRONG_NAMES = {
    "multi_select": {"question", "correctIndices", "correct_indices", "correctIndex", "correct_index", "correctAnswers",
                     "correct_answer", "answer", "answers", "multiple", "allowMultiple"},
    "text_input": {"prompt", "question", "caseSensitive", "case_sensitive", "correctAnswer", "answers"},
    "true_false": {"question", "answer", "is_true"},
    "cloze": {"content", "answer", "answers"},
    "text": {"text"},
    "ordering": {"correct_order"},
    "image": {"url", "src", "media_id"}, "audio": {"url", "src", "media_id"}, "image_occlusion": {"url", "src", "media_id"},
}
DECK_TYPES = {"study", "quiz", "reading"}
LANGS = {"en", "th", "zh", "ja", "ko", "es", "fr", "de", "vi", "other"}
LEVELS = {"beginner", "intermediate", "advanced"}
CLOZE = re.compile(r"\{\{c\d+[:：]{1,2}.+?\}\}")
LATIN_ONLY = re.compile(r"^[A-Za-z0-9\s,.'’!?\-–—/()\"]+$")
UNSUPPORTED_MD = re.compile(r"^\s*\|.*\|\s*$|^\s*```", re.M)


def _words(text):
    latin = len(re.findall(r"[A-Za-z0-9À-ɏ'’-]+", text))
    cjk = len(re.findall(r"[぀-ヿ㐀-鿿가-힯]", text))
    thai = len(re.findall(r"[฀-๿]", text))
    return latin + cjk / 2 + thai / 5


def _module_text(m):
    for k in ("content", "text", "statement"):
        if isinstance(m.get(k), str):
            return m[k]
    return ""


def lint_module(m, where, deck_type, errors, warnings):
    if not isinstance(m, dict) or "type" not in m:
        errors.append(f"{where}: a module must be an object with a 'type'")
        return
    t = m["type"]
    if t not in INTERACTIVE | DISPLAY:
        errors.append(f"{where}: unknown module type '{t}'")
        return
    for f in REQUIRED.get(t, []):
        if f not in m:
            errors.append(f"{where}: {t} needs '{f}'")
    for f in WRONG_NAMES.get(t, set()) & set(m):
        errors.append(f"{where}: '{f}' is not a field of {t} (see references/modules.md)")
    if t in ("text", "hint") and not str(m.get("content", "")).strip():
        errors.append(f"{where}: empty {t}")
    if t in ("text", "hint") and UNSUPPORTED_MD.search(str(m.get("content", ""))):
        warnings.append(f"{where}: tables and code blocks aren't rendered (only light markdown) — use lines and bullets")
    if t == "multi_select":
        opts, ok = m.get("options") or [], m.get("correct_answers") or []
        if not ok:
            errors.append(f"{where}: multi_select needs at least one correct answer")
        for a in ok:
            if a not in opts:
                errors.append(f"{where}: correct answer {a!r} is not exactly one of the options")
        if not m.get("allow_multiple") and len(ok) > 1:
            errors.append(f"{where}: several correct answers need \"allow_multiple\": true")
        if len(opts) < 2:
            errors.append(f"{where}: multi_select needs 2+ options")
    if t == "cloze" and not CLOZE.search(str(m.get("text", ""))):
        errors.append(f"{where}: cloze text has no {{{{c1::answer}}}} blank")
    if t == "text_input" and deck_type == "quiz" and not (m.get("correct_answer") or m.get("answer")):
        errors.append(f"{where}: text_input in a quiz needs correct_answer")
    if t == "ordering":
        items, order = m.get("items") or [], m.get("correctOrder") or []
        if len(items) < 2 or sorted(order) != list(range(len(items))):
            errors.append(f"{where}: correctOrder must list each item index 0..{len(items) - 1} once")
    if t == "matching" and any(not (isinstance(p, dict) and p.get("left") and p.get("right")) for p in m.get("pairs") or []):
        errors.append(f"{where}: every matching pair needs left and right")
    if t in ("tts", "speak", "dictation"):
        lang = m.get("lang")
        if lang is not None:
            canon = TTS_ALIASES.get(str(lang).lower(), lang)
            if canon not in TTS_LANGS:
                errors.append(f"{where}: speech language {lang!r} unsupported — use one of {sorted(TTS_LANGS)} or a text module")
            elif canon in ("ja", "zh-CN", "th-TH") and LATIN_ONLY.match(str(m.get("text", ""))):
                errors.append(f"{where}: {canon} speech reads Latin letters {m.get('text')!r} — use the native script")
    if t in ("image", "audio", "image_occlusion") and not (isinstance(m.get("media"), dict) and m["media"].get("id")):
        errors.append(f"{where}: media must be {{\"id\": \"<uuid from POST /api/uploads/>\"}} (no URLs)")


def lint_course(course):
    errors, warnings = [], []
    if not isinstance(course, dict) or not isinstance(course.get("decks"), list) or not course["decks"]:
        return ["course file needs a non-empty \"decks\" list"], []
    coll = course.get("collection")
    if coll is not None:
        if not str(coll.get("name", "")).strip():
            errors.append("collection.name is required")
        if coll.get("language") and coll["language"] not in LANGS:
            errors.append(f"collection.language must be one of {sorted(LANGS)}")
        if coll.get("level") and coll["level"] not in LEVELS:
            errors.append(f"collection.level must be one of {sorted(LEVELS)}")
        if not coll.get("description"):
            warnings.append("collection has no description (say what it teaches and the order to use the decks)")
    fronts = {}
    for di, deck in enumerate(course["decks"]):
        dw = f"decks[{di}]"
        dt = deck.get("deck_type", "study")
        if "deck_id" not in deck:
            if not str(deck.get("name", "")).strip():
                errors.append(f"{dw}: name is required")
            if dt not in DECK_TYPES:
                errors.append(f"{dw}: deck_type must be study, quiz or reading")
            if not deck.get("description"):
                warnings.append(f"{dw} ({deck.get('name')}): no description")
        cards = deck.get("cards") or []
        if not cards and "deck_id" not in deck:
            warnings.append(f"{dw} ({deck.get('name')}): no cards")
        explained = 0
        for ci, card in enumerate(cards):
            cw = f"{dw}.cards[{ci}]"
            for bad in ("front", "back", "explanation", "modules"):
                if bad in card:
                    errors.append(f"{cw}: use front_content/back_content/explanation_content, not '{bad}'")
            faces = {}
            for face in ("front_content", "back_content", "explanation_content"):
                mods = card.get(face)
                if mods is None:
                    if face != "explanation_content":
                        errors.append(f"{cw}: {face} is required")
                    continue
                if not isinstance(mods, list) or (face != "explanation_content" and not mods) or len(mods) > 50:
                    errors.append(f"{cw}: {face} must be a list of 1–50 modules")
                    continue
                faces[face] = mods
                for mi, m in enumerate(mods):
                    lint_module(m, f"{cw}.{face}[{mi}]", dt, errors, warnings)
            mods_all = [m for f in faces.values() for m in f if isinstance(m, dict)]
            types = {m.get("type") for m in mods_all}
            if dt == "quiz" and not types & INTERACTIVE:
                errors.append(f"{cw}: quiz card without an interactive module is never graded")
            if dt == "reading" and types & INTERACTIVE:
                warnings.append(f"{cw}: reading notes are read, not answered — interactive modules belong in study/quiz decks")
            if dt == "reading":
                words = _words(" ".join(_module_text(m) for m in mods_all))
                if words > 300:
                    warnings.append(f"{cw}: note is ~{int(words)} words — split it (keep notes ≤ ~200 words)")
            if card.get("explanation_content"):
                explained += 1
            front = json.dumps(card.get("front_content"), sort_keys=True, ensure_ascii=False)
            if front in fronts:
                warnings.append(f"{cw}: same front as {fronts[front]} (duplicate?)")
            fronts.setdefault(front, cw)
            if not card.get("tags"):
                warnings.append(f"{cw}: no tags")
        if dt == "study" and len(cards) >= 5 and explained / len(cards) < 0.3:
            warnings.append(f"{dw} ({deck.get('name')}): only {explained}/{len(cards)} cards explain anything — add explanation_content to tricky ones")
    return errors, warnings


def _print_lint(errors, warnings, limit=60):
    for w in warnings[:limit]:
        print("warning:", w)
    if len(warnings) > limit:
        print(f"... and {len(warnings) - limit} more warnings")
    for e in errors[:limit]:
        print("ERROR:", e)
    if len(errors) > limit:
        print(f"... and {len(errors) - limit} more errors")
    print(f"lint: {len(errors)} errors, {len(warnings)} warnings")


# ── Commands ──────────────────────────────────────────────────────────────────


def cmd_whoami(_):
    me = must("GET", "/auth/me")
    print(f"OK — signed in as {me.get('username')} (timezone {me.get('timezone') or 'UTC'}) at {API}")
    for path, scope in (("/decks?limit=1", "decks:read"), ("/flashcards?limit=1", "cards:read")):
        status, _ = call("GET", path)
        print(f"  {scope}: {'yes' if status < 400 else 'NO (' + str(status) + ')'}")
    print("  (write permissions are checked when you create something)")


def cmd_ls(_):
    colls = must("GET", "/collections")
    decks = must("GET", "/decks?limit=500")
    by_coll = {}
    for d in decks:
        by_coll.setdefault(d.get("collection_id"), []).append(d)
    for c in colls:
        print(f"collection {c['id']}: {c['name']}  ({c.get('deck_count', 0)} decks, {c.get('card_count', 0)} cards)")
        for d in sorted(by_coll.get(c["id"], []), key=lambda d: d.get("collection_position") or 0):
            print(f"  deck {d['id']}: [{d['deck_type']}] {d['name']}  ({d.get('card_count', 0)} cards)")
    loose = by_coll.get(None, [])
    if loose:
        print("ungrouped decks:")
        for d in loose:
            print(f"  deck {d['id']}: [{d['deck_type']}] {d['name']}  ({d.get('card_count', 0)} cards)")


def _deck_with_cards(deck_id):
    deck = must("GET", f"/decks/{deck_id}")
    cards = must("GET", f"/flashcards?deck_id={deck_id}&limit=500")
    keep = ("id", "front_content", "back_content", "explanation_content", "tags", "reps", "lapses", "state", "due", "last_review")
    return {"deck": {k: deck.get(k) for k in ("id", "name", "description", "deck_type", "daily_new_cards",
                                               "daily_reading_goal", "quiz_config", "language", "level",
                                               "collection_id", "card_count")},
            "cards": [{k: c.get(k) for k in keep} for c in cards]}


def _out(data, args):
    text = json.dumps(data, ensure_ascii=False, indent=1)
    if "-o" in args:
        path = args[args.index("-o") + 1]
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"wrote {path}")
    else:
        print(text)


def cmd_export(args):
    _out(_deck_with_cards(int(args[0])), args)


def cmd_export_collection(args):
    coll = must("GET", f"/collections/{int(args[0])}")
    decks = [_deck_with_cards(d["id"]) for d in coll.get("decks", [])]
    meta = {k: coll.get(k) for k in ("id", "name", "description", "emoji", "language", "level")}
    _out({"collection": meta, "decks": decks}, args)


def _load(path):
    if path.startswith("@"):
        path = path[1:]
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def changes_as_course(changes):
    """A changes file (mb.py update) as a course, so the same checks apply."""
    filler = {"front_content": [{"type": "text", "content": "x"}],
              "back_content": [{"type": "text", "content": "x"}], "tags": ["x"]}
    cards = [dict(filler, **c) for c in changes.get("cards", []) + changes.get("new_cards", [])]
    return {"decks": [{"deck_id": 0, "deck_type": changes.get("deck_type", "study"), "cards": cards}]}


def cmd_lint(args):
    data = _load(args[0])
    if "decks" not in data and ("cards" in data or "new_cards" in data):
        data = changes_as_course(data)
    errors, warnings = lint_course(data)
    _print_lint(errors, warnings)
    sys.exit(1 if errors else 0)


def cmd_push(args):
    path = args[0]
    dry = "--dry-run" in args
    course = _load(path)
    errors, warnings = lint_course(course)
    _print_lint(errors, warnings, limit=20)
    if errors:
        sys.exit("Fix the errors above, then push again.")
    if dry:
        n = sum(len(d.get("cards") or []) for d in course["decks"])
        print(f"dry run OK: {len(course['decks'])} decks, {n} cards would be created")
        return
    # Progress is saved next to the course file so a failed push can resume
    # without creating duplicates.
    state_path = path + ".state.json"
    state = _load(state_path) if os.path.exists(state_path) else {"decks": {}}

    def save():
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=1)

    coll_id = course.get("collection_id") or state.get("collection_id")
    if course.get("collection") and not coll_id:
        c = course["collection"]
        body = {k: c[k] for k in ("name", "description", "emoji", "color", "language", "level") if c.get(k)}
        coll_id = must("POST", "/collections", body)["id"]
        state["collection_id"] = coll_id
        save()
        print(f"created collection {coll_id}: {c['name']}")

    created_total, failed_total = 0, 0
    for di, deck in enumerate(course["decks"]):
        key = str(di)
        ds = state["decks"].setdefault(key, {"done": 0})
        deck_id = deck.get("deck_id") or ds.get("deck_id")
        if not deck_id:
            body = {"name": deck["name"], "deck_type": deck.get("deck_type", "study")}
            for k in ("description", "language", "level", "quiz_config", "daily_new_cards", "daily_reading_goal"):
                if deck.get(k) is not None:
                    body[k] = deck[k]
            if coll_id:
                body["collection_id"] = coll_id
            deck_id = must("POST", "/decks", body)["id"]
            ds["deck_id"] = deck_id
            save()
            print(f"created {body['deck_type']} deck {deck_id}: {deck['name']}")
        cards = deck.get("cards") or []
        start = ds.get("done", 0)
        for i in range(start, len(cards), BATCH):
            chunk = cards[i:i + BATCH]
            body = {"cards": [{"deck_id": deck_id, **{k: c[k] for k in
                               ("front_content", "back_content", "explanation_content", "tags") if k in c}}
                              for c in chunk]}
            res = must("POST", "/flashcards/batch", body)
            created_total += res.get("created", 0)
            for r in res.get("results", []):
                if not r.get("success"):
                    failed_total += 1
                    errs = "; ".join(f"{e.get('path') or e.get('loc')}: {e.get('msg')}" for e in r.get("errors", []))
                    print(f"  card {i + r['index']} of deck {deck_id} failed: {errs}")
            ds["done"] = i + len(chunk)
            save()
        if cards:
            print(f"  deck {deck_id}: {ds['done']} cards processed")
    print(f"done: {created_total} cards created, {failed_total} failed")
    if coll_id:
        print(f"open: {APP}/app/collection/{coll_id}")
    else:
        for ds in state["decks"].values():
            if ds.get("deck_id"):
                print(f"open: {APP}/app/deck/{ds['deck_id']}")
    if failed_total:
        print("Fix the failed cards and add them with:  mb.py api POST /flashcards/batch @fixed.json")
        sys.exit(1)


def cmd_update(args):
    """CHANGES.json: {"cards": [{"id": 12, "front_content": …, "back_content": …, "explanation_content": …, "tags": …}],
                      "new_cards": [{"deck_id": 3, …}]}  — only the fields given are changed."""
    changes = _load(args[0])
    errors, _ = lint_course(changes_as_course(changes))
    if errors:
        _print_lint(errors, [])
        sys.exit("Fix the errors above first.")
    ok = 0
    for c in changes.get("cards", []):
        body = {k: c[k] for k in ("front_content", "back_content", "explanation_content", "tags", "deck_id") if k in c}
        status, payload = call("PATCH", f"/flashcards/{c['id']}", body)
        if status >= 400:
            print(f"card {c['id']}: {status} {json.dumps(payload, ensure_ascii=False)[:400]}")
        else:
            ok += 1
    new = changes.get("new_cards", [])
    for i in range(0, len(new), BATCH):
        res = must("POST", "/flashcards/batch", {"cards": new[i:i + BATCH]})
        ok += res.get("created", 0)
        for r in res.get("results", []):
            if not r.get("success"):
                print(f"new card {i + r['index']} failed: {r.get('errors')}")
    print(f"done: {ok} cards updated/created")


def cmd_api(args):
    method, path = args[0], args[1]
    body = None
    if len(args) > 2:
        body = _load(args[2]) if args[2].startswith("@") else json.loads(args[2])
    status, payload = call(method, path, body)
    print(json.dumps({"status": status, "body": payload}, ensure_ascii=False, indent=1))
    sys.exit(1 if status >= 400 else 0)


COMMANDS = {"whoami": cmd_whoami, "ls": cmd_ls, "export": cmd_export, "export-collection": cmd_export_collection,
            "lint": cmd_lint, "push": cmd_push, "update": cmd_update, "api": cmd_api}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(2)
    COMMANDS[sys.argv[1]](sys.argv[2:])
