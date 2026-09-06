# Kids Quiz — Structure & Authoring Guide

A reusable reference for creating large (1000+ question) multiple-choice quizzes for
kids, following the same format as `science-nature-quiz.json`. Use this document as
the template when starting any future quiz.

---

## 1. JSON output structure

Every quiz is a single JSON object with a metadata header plus a `questions` array.

```json
{
  "topic": "Science and Nature",
  "audience": "7-year-old kids in Australia",
  "difficulty": "easy",
  "count": 1000,
  "questions": [
    {
      "question": "Which is bigger, a cat or a hippo?",
      "options": [
        "a hippo",
        "they are the same size",
        "you cannot tell",
        "a cat"
      ],
      "answer": "a hippo"
    }
  ]
}
```

### Top-level fields

| Field       | Type    | Notes |
|-------------|---------|-------|
| `topic`     | string  | Human-readable subject, e.g. `"Australian Geography"`. |
| `audience`  | string  | Who it's for, e.g. `"kids under 10 in Australia"`. |
| `difficulty`| string  | `"easy"`, `"medium"`, or `"mixed"`. |
| `count`     | integer | Number of questions actually written to the file. Must equal `questions.length`. |
| `questions` | array   | The list of question objects (see below). |

### Question object

| Field      | Type            | Rules |
|------------|-----------------|-------|
| `question` | string          | The prompt. Ends with `?`. Unique across the whole file (case-insensitive). |
| `options`  | array of 4 strings | Exactly 4 short options. Includes the correct answer plus 3 distractors. Order is shuffled. All 4 must be unique. |
| `answer`   | string          | Must match one of the `options` strings **exactly** (same casing/spelling). |

---

## 2. Content rules for kids

- **Short, simple wording.** One idea per question. Avoid long sentences.
- **Age-appropriate reading level.** For "easy" (ages 5–7) use very common words.
- **Short options.** A few words each; no full sentences where avoidable.
- **One clearly correct answer.** No trick questions or ambiguous options.
- **Plausible distractors.** Wrong options should be believable but clearly wrong,
  not silly to the point of giving the answer away every time (a little humour is OK).
- **No negatives/gotchas** like "Which is NOT..." for the youngest ages.
- **Answer position is randomised**, so the correct option is not always first.
- **Local relevance.** Use Australian spelling (colour, centre) and local context.

---

## 3. Generator script pattern (recommended for 1000+)

Hand-writing 1000 unique questions is error-prone. Instead use a Python generator
(`generate_*.py`) that combines **templated questions** from data tables with a set
of **hand-written direct facts**, guaranteeing uniqueness and a shuffled answer slot.

### Core helper

```python
import json, random
random.seed(7)                 # reproducible output

questions, seen = [], set()

def add(question, correct, distractor_pool):
    """Build one shuffled 4-option question; skip duplicates."""
    q = question.strip()
    key = q.lower()
    if key in seen:
        return
    pool = [d for d in dict.fromkeys(distractor_pool) if d != correct]
    if len(pool) < 3:
        return                 # not enough distractors -> skip
    options = [correct] + random.sample(pool, 3)
    random.shuffle(options)
    seen.add(key)
    questions.append({"question": q, "options": options, "answer": correct})
```

### Three ways to feed `add()`

1. **Data-table templates** — loop over a list of records and emit several
   questions per record.
   ```python
   for city in CITIES:
       add(f"What state is {city['name']} in?", city["state"], STATE_POOL)
   ```

2. **Direct fact tuples** — `(question, correct, [distractor1, distractor2, distractor3])`.
   ```python
   FACTS = [
       ("What is the capital city of Australia?", "Canberra",
        ["Sydney", "Melbourne", "Perth"]),
   ]
   for q, correct, distractors in FACTS:
       add(q, correct, distractors)
   ```

3. **Comparison generators** — ordered lists produce many unique pairwise
   questions (e.g. "Which is bigger/closer/further...").
   ```python
   for i in range(len(ORDER)):
       for j in range(i + 4, len(ORDER)):   # +4 gap keeps pairs sensible
           add(f"Which is bigger, {ORDER[i]} or {ORDER[j]}?", ORDER[j],
               [ORDER[i], "they are the same", "you cannot tell"])
   ```

### Assemble & write

```python
if len(questions) < 1000:
    raise SystemExit(f"Only produced {len(questions)} unique questions — add more.")

random.shuffle(questions)
final = questions[:1000]

output = {
    "topic": "…",
    "audience": "…",
    "difficulty": "easy",
    "count": len(final),
    "questions": final,
}
with open("my-quiz.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Unique available: {len(questions)}; wrote {len(final)}.")
```

---

## 4. Quality checklist before shipping

- [ ] `count` equals `len(questions)`.
- [ ] Every `answer` appears verbatim in its `options`.
- [ ] Every question has exactly 4 options, all unique.
- [ ] No duplicate questions (case-insensitive).
- [ ] Correct-answer position is spread across all 4 slots (not always first).
- [ ] Avoid true/false scenarios we want a mutliple choice experince.
- [ ] Wording and spelling suit the target age and locale.
- [ ] Facts are accurate.
- [ ] Questions are concisely worded.
- [ ] Don't duplicate information between the question and answer.

---

## 5. Reuse workflow for a new quiz

1. Copy this guide's generator pattern into `generate_<topic>.py`.
2. Decide subtopics and build the data tables + fact lists.
3. Set the metadata header (`topic`, `audience`, `difficulty`).
4. Run the script; confirm it reports 1000+ unique questions.
5. Run the quality checklist.
6. Commit the `.py` generator and the produced `.json`.
