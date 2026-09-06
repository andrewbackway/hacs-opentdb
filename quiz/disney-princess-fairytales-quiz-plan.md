# Plan — Disney Princess & Fairy Tales Quiz (5-year-olds)

Status: **AWAITING APPROVAL** — no quiz will be generated until you reply "approved".

Follows the reusable format and generator pattern in `quiz-structure-guide.md`, the same
as `australian-geography-quiz.json` and `science-nature-quiz.json`.

---

## 1. Goal

Produce a quiz of **at least 1000** unique multiple-choice questions about Disney
princesses and fairy tales, aimed at **5-year-olds**, in the same JSON format as the
other quizzes.

## 2. Metadata header

```json
{
  "topic": "Disney Princesses and Fairy Tales",
  "audience": "5-year-old kids",
  "difficulty": "easy",
  "count": 1000,
  "questions": [ ... ]
}
```

- Reading level: **very easy (age 5, very simple wording, short options)**.
- Scope: **both Disney princess versions and classic fairy tales** (chosen in setup).

## 3. Output files

| File | Purpose |
|------|---------|
| `generate_disney_princess_quiz.py` | Python generator (templates + facts + comparisons). |
| `disney-princess-fairytales-quiz.json` | The generated 1000-question quiz. |
| `quiz-structure-guide.md` | Reusable format/authoring guide (already exists). |

## 4. Copyright & safety approach

- Questions are **short, factual trivia** only (character names, colours, simple story
  facts like "Which princess has long magic hair?").
- **No song lyrics, no long verbatim story text, no images** — nothing copied from the
  films or books. Just simple general-knowledge facts, the same as a kids' quiz book.
- Kind, gentle wording suitable for age 5; nothing scary or upsetting.

## 5. Subtopics & question templates

Seven subtopics selected. Each lists its data tables and example templates that feed the
shared `add()` helper (4 shuffled options, unique questions).

### 5.1 Disney princesses — who's who
Data: princess + film + hair colour + dress colour + a simple signature trait.
- "Which princess has long magic golden hair?" → Rapunzel
- "Which princess is a mermaid?" → Ariel
- "Which princess can make ice and snow?" → Elsa
- "Which princess has a pet tiger called Rajah?" → Jasmine
- "What colour is {princess}'s hair?" → colour
- "What colour dress is {princess} best known for?" → colour

### 5.2 Princess home / kingdom & setting
Data: princess + where she lives (under the sea, a big castle, a snowy kingdom, a
tropical island, a French village, an Arabian palace, the forest).
- "Where does Ariel live?" → under the sea
- "Which princess lives on a tropical island?" → Moana
- "Which princess rules a kingdom of ice and snow?" → Elsa
- "Which princess lives in the forest with animals?" → Snow White

### 5.3 Classic fairy tales
Data: tale + one core fact each (Cinderella's glass slipper, Snow White's apple,
Sleeping Beauty's long sleep, Jack's beanstalk, the three little pigs, Goldilocks,
Little Red Riding Hood, the Gingerbread Man, the Ugly Duckling, the Frog Prince,
Hansel and Gretel, Rumpelstiltskin, the Princess and the Pea).
- "In which story does a girl lose a glass slipper?" → Cinderella
- "Who ate the three bears' porridge?" → Goldilocks
- "What did Jack climb up?" → a beanstalk
- "How many little pigs are there?" → three

### 5.4 Fairy tale characters & creatures
Data: dwarfs, fairy godmother, big bad wolf, witch, giant, troll, prince, genie,
talking animals.
- "How many dwarfs live with Snow White?" → seven
- "Who helps Cinderella get to the ball?" → her fairy godmother
- "Who huffs and puffs to blow houses down?" → the big bad wolf
- "Who grants three wishes to Aladdin?" → the Genie

### 5.5 Magic objects
Data: glass slipper, magic mirror, spinning wheel, magic wand, magic lamp, magic
carpet, poisoned apple, golden key, magic beans.
- "What did Cinderella leave behind at the ball?" → a glass slipper
- "What does the evil queen talk to on the wall?" → a magic mirror
- "What comes out of Aladdin's lamp?" → a genie
- "What can a magic carpet do?" → fly

### 5.6 Animals & sidekicks
Data: princess/tale + animal friend (Ariel & Flounder/Sebastian, Cinderella & mice,
Jasmine & Rajah/Abu, Moana & Pua/Heihei, Aurora's forest animals, Mulan's Mushu).
- "Who is Ariel's little fish friend?" → Flounder
- "What kind of animal is Sebastian?" → a crab
- "What pet does Jasmine have?" → a tiger
- "What kind of bird is Heihei in Moana?" → a chicken

### 5.7 Story endings & 'happily ever after'
Data: gentle, universal story-shape facts.
- "How do many fairy tales end?" → happily ever after
- "What do a prince and princess often do at the end?" → get married and dance
- "In fairy tales, do the kind characters usually win?" → yes
- "What breaks the sleeping spell in Sleeping Beauty?" → true love's kiss

## 6. Reaching 1000+ unique questions

Combine, exactly like the geography quiz:
1. **Templated questions** from the data tables (several per record).
2. **Direct fact tuples** for one-off facts.
3. **Comparison / matching generators** for volume, e.g.:
   - "Which princess has {colour} hair, {A} or {B}?"
   - "Who lives {place}, {A} or {B}?"
   - "Which story has {object}, {A} or {B}?"
   - Princess ↔ film matching in both directions.

The script asserts `len(questions) >= 1000` and errors out if short, so we add more
data rows/facts until it comfortably exceeds 1000. Uses `random.seed(7)` for
reproducible output and shuffles the correct-answer slot.

## 7. Validation before delivery

Run the quality checklist from `quiz-structure-guide.md`:
- `count` == number of questions
- every `answer` present in its `options`
- exactly 4 unique options each
- no duplicate questions
- answer positions spread across all slots

## 8. Deliverables on approval

1. `generate_disney_princess_quiz.py`
2. `disney-princess-fairytales-quiz.json` (1000 questions)
3. Confirmation output showing unique-question count and validation results.

---

## Appendix A — Core data tables

### A.1 Disney princesses

| Princess | Film | Hair | Dress | Signature trait |
|----------|------|------|-------|-----------------|
| Cinderella | Cinderella | blonde | blue | lost a glass slipper |
| Snow White | Snow White | black | blue and yellow | friends with seven dwarfs |
| Aurora | Sleeping Beauty | blonde | pink | slept for a long time |
| Ariel | The Little Mermaid | red | green (tail) | a mermaid |
| Belle | Beauty and the Beast | brown | yellow | loves reading books |
| Jasmine | Aladdin | black | blue/teal | has a pet tiger, Rajah |
| Rapunzel | Tangled | very long blonde | purple | long magic hair |
| Elsa | Frozen | white-blonde | ice blue | makes ice and snow |
| Anna | Frozen | red-brown | green/blue | Elsa's brave sister |
| Moana | Moana | brown, wavy | red and cream | sails the ocean |
| Tiana | The Princess and the Frog | black | green | wants to open a restaurant |
| Mulan | Mulan | black | (soldier) | brave and clever |
| Merida | Brave | curly red | blue/green | great at archery |
| Pocahontas | Pocahontas | long black | tan | friends with nature |

### A.2 Homes / kingdoms

| Princess | Lives / setting |
|----------|-----------------|
| Ariel | under the sea |
| Elsa & Anna | a snowy kingdom (Arendelle) |
| Jasmine | a desert palace (Agrabah) |
| Moana | a tropical island |
| Belle | a French village |
| Snow White | a cottage in the forest |
| Rapunzel | a tall tower |
| Cinderella | a big house, then a castle |
| Pocahontas | the forest by a river |

### A.3 Classic fairy tales (core fact)

| Tale | Core fact |
|------|-----------|
| Cinderella | leaves a glass slipper at midnight |
| Snow White | bites a poisoned apple |
| Sleeping Beauty | pricks a finger and sleeps |
| Jack and the Beanstalk | climbs a giant beanstalk |
| The Three Little Pigs | wolf blows houses down |
| Goldilocks and the Three Bears | eats the bears' porridge |
| Little Red Riding Hood | visits Grandma; meets a wolf |
| The Gingerbread Man | runs away from everyone |
| The Ugly Duckling | grows into a beautiful swan |
| The Frog Prince | a frog turns into a prince |
| Hansel and Gretel | find a house made of sweets |
| Rumpelstiltskin | spins straw into gold |
| The Princess and the Pea | a pea under many mattresses |
| Rapunzel | lets down her long hair |
| Beauty and the Beast | a beast turns into a prince |

### A.4 Magic objects

| Object | Story |
|--------|-------|
| a glass slipper | Cinderella |
| a magic mirror | Snow White |
| a spinning wheel | Sleeping Beauty |
| a magic lamp | Aladdin |
| a magic carpet | Aladdin |
| a poisoned apple | Snow White |
| magic beans | Jack and the Beanstalk |
| a fairy wand | Cinderella (fairy godmother) |
| a pumpkin coach | Cinderella |

### A.5 Animals & sidekicks

| Sidekick | Who / what |
|----------|-----------|
| Flounder | Ariel's fish friend |
| Sebastian | a crab, Ariel's friend |
| Rajah | Jasmine's pet tiger |
| Abu | Aladdin's monkey |
| Pua | Moana's pet pig |
| Heihei | a chicken in Moana |
| Olaf | a snowman in Frozen |
| Mushu | a little dragon in Mulan |
| Pascal | Rapunzel's chameleon |
| Maximus | a horse in Tangled |

### A.6 Colours (for very-easy matching)

- Cinderella's dress: **blue**
- Aurora's dress: **pink**
- Belle's dress: **yellow**
- Snow White's bow: **red**
- Elsa's dress: **ice blue**
- Ariel's tail: **green**
- Rapunzel's hair: **golden/blonde**

---

## Appendix B — Matching generators (for volume)

Pairwise/matching questions that naturally have 4 valid options
(A, B, plus "both" / "neither" or two more names):

- Princess ↔ film: "Which film is {princess} in?" and "Which princess is in {film}?"
- Hair colour: "Which princess has {colour} hair, {A} or {B}?"
- Home: "Who lives {place}, {A} or {B}?"
- Object ↔ story: "In which story is there {object}?"
- Sidekick ↔ owner: "Whose friend is {sidekick}?"
- "Which princess is a mermaid / makes snow / has long hair / loves books?" style.

## Appendix C — Estimated question yield

| Source | Rough count |
|--------|-------------|
| Princess who's-who + colours templates | ~140 |
| Princess ↔ film matching (both ways) | ~120 |
| Homes / settings templates | ~110 |
| Classic fairy tale facts | ~130 |
| Characters & creatures facts | ~90 |
| Magic objects templates | ~110 |
| Animals & sidekicks templates | ~120 |
| Story endings facts | ~60 |
| Matching / comparison generators | ~180+ |
| **Total available** | **~1060+** (trimmed to 1000) |

If the total falls short at build time, the script errors out and we add more rows
until it comfortably exceeds 1000.

---

**Reply "approved" to generate the quiz, or tell me what to change in this plan.**
