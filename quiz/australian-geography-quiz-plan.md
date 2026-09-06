# Plan — Australian Geography & Places Quiz (kids under 10)

Status: **AWAITING APPROVAL** — no quiz will be generated until you reply "approved".

See `quiz-structure-guide.md` for the reusable JSON format and generator pattern this
plan follows.

---

## 1. Goal

Produce a quiz of **at least 1000** unique multiple-choice questions about Australian
geography and places, aimed at **kids under 10**, in the same JSON format as
`science-nature-quiz.json`.

## 2. Metadata header

```json
{
  "topic": "Australian Geography",
  "audience": "kids under 10 in Australia",
  "difficulty": "easy",
  "count": 1000,
  "questions": [ ... ]
}
```

- Reading level: **easy (ages 5–7, very simple wording)** — chosen in setup.
- Australian spelling throughout.

## 3. Output files

| File | Purpose |
|------|---------|
| `generate_australian_geography_quiz.py` | Python generator (templates + facts + comparisons). |
| `australian-geography-quiz.json` | The generated 1000-question quiz. |
| `quiz-structure-guide.md` | Reusable format/authoring guide (already created). |

## 4. Subtopics & question templates

All nine subtopics below were selected. Each lists the data tables and example
question templates. Every template feeds the shared `add()` helper (4 shuffled
options, unique questions).

### 4.1 States & territories (names, capitals)
Data: 6 states + 2 territories with capitals, nicknames, rough location.
- "What is the capital city of {state}?" → capital, distractors = other capitals
- "Which of these is a state or territory of Australia?" → name, distractors = made-up/overseas
- "In which state is the city of {city}?" → state
- "What is the capital of Australia?" → Canberra
- Direction facts: "Is {state} in the north or south of Australia?" (very simple)

### 4.2 Major cities & towns
Data: capital cities + well-known towns (Cairns, Alice Springs, Gold Coast, Broome,
Ballarat, Byron Bay, Darwin, Hobart, etc.) each tagged with state and a fun fact.
- "Which state is {city} in?" → state
- "Which city is by the beach / near Uluru / etc.?" (simple landmark links)
- "Which is Australia's biggest city?" → Sydney
- "Which city has the Opera House?" → Sydney

### 4.3 Landmarks
Data: Uluru, Sydney Opera House, Sydney Harbour Bridge, Great Barrier Reef, Twelve
Apostles, Bondi Beach, Kakadu, Blue Mountains, MCG, Kangaroo Island, etc., each with
its state and a one-line description.
- "Where is {landmark}?" → state
- "What is the big red rock in the middle of Australia called?" → Uluru
- "Which famous building is in Sydney?" → Opera House
- "Which is a famous coral reef in Australia?" → Great Barrier Reef

### 4.4 Rivers, lakes & mountains
Data: Murray River, Darling River, Lake Eyre, Snowy Mountains, Mount Kosciuszko,
Blue Mountains, Grampians, etc.
- "Which is Australia's longest river?" → Murray
- "What is the tallest mountain in Australia?" → Mount Kosciuszko
- "Is {feature} a river, a lake or a mountain?" → type

### 4.5 Beaches, oceans & reefs
Data: Bondi, Surfers Paradise, Cable Beach, Whitehaven; oceans/seas around Australia
(Indian Ocean, Pacific Ocean, Coral Sea, Tasman Sea); Great Barrier Reef.
- "Which ocean is on the {east/west} side of Australia?" (simple)
- "What do we call the huge reef off Queensland?" → Great Barrier Reef
- "Which of these is a famous Australian beach?" → beach

### 4.6 Deserts & the outback
Data: Simpson Desert, Great Victoria Desert, the Outback, Alice Springs, red sand.
- "What do we call the dry, red middle part of Australia?" → the Outback
- "Is the desert wet or dry?" → dry (very easy)
- "Which town is in the middle of the Outback?" → Alice Springs

### 4.7 Flags, symbols & map directions
Data: colours of the Australian flag, Southern Cross, national colours (green & gold),
compass directions.
- "What colours are on the Australian flag?" → red, white and blue
- "What are Australia's sporting colours?" → green and gold
- "Which way is up on a map?" → north
- "If Perth is on the {west} and Sydney is on the {east}, which is on the west?" → Perth

### 4.8 Weather & climate by region
Data: hot north (Darwin), cold south (Hobart/snow in the Alps), seasons reversed vs
northern hemisphere.
- "Which Australian city is hot and tropical?" → Darwin
- "Where in Australia can you see snow?" → the Snowy Mountains
- "In Australia, which month is usually hottest?" → January (or "summer")

### 4.9 Animals tied to places
Data: koala/kangaroo (bush), saltwater crocodile (northern rivers), little penguins
(Phillip Island), quokka (Rottnest Island), clownfish (Great Barrier Reef), Tasmanian
devil (Tasmania).
- "Where do you find a Tasmanian devil?" → Tasmania
- "On which island can you see quokkas?" → Rottnest Island
- "Where do lots of colourful fish live?" → the Great Barrier Reef

## 5. Reaching 1000+ unique questions

Combine:
1. **Templated questions** from the data tables above (many per record).
2. **Direct fact tuples** for one-off facts.
3. **Comparison generators**, e.g.:
   - "Which is bigger, {stateA} or {stateB}?" (by area)
   - "Which city is further north, {cityA} or {cityB}?"
   - "Which is closer to the beach / the Outback...?"

The script asserts `len(questions) >= 1000` and exits with an error if short, so we
add more data tables/facts until the target is met. Uses `random.seed(7)` for
reproducible output and shuffles the correct-answer slot.

## 6. Accuracy & safety notes

- All facts verified against well-known references (capitals, landmarks, states).
- Wording kept very simple; distractors plausible but clearly wrong.
- Australian spelling and local context throughout.

## 7. Validation before delivery

Run the quality checklist from `quiz-structure-guide.md`:
- `count` == number of questions
- every `answer` present in its `options`
- exactly 4 unique options each
- no duplicate questions
- answer positions spread across all slots

## 8. Deliverables on approval

1. `generate_australian_geography_quiz.py`
2. `australian-geography-quiz.json` (1000 questions)
3. Confirmation output showing unique-question count and validation results.

---

## Appendix A — Core data tables

Concrete data the generator will draw from. These are the "master tables"; each row
produces several templated questions.

### A.1 States & territories

| Name | Abbrev | Capital | Location (simple) | Fun fact |
|------|--------|---------|-------------------|----------|
| New South Wales | NSW | Sydney | south-east | Home to the Opera House |
| Victoria | VIC | Melbourne | south-east | Smallest mainland state |
| Queensland | QLD | Brisbane | north-east | Home of the Great Barrier Reef |
| South Australia | SA | Adelaide | south | Known for wine and festivals |
| Western Australia | WA | Perth | west | The biggest state |
| Tasmania | TAS | Hobart | south (island) | An island state |
| Northern Territory | NT | Darwin | north | Home to Uluru and Kakadu |
| Australian Capital Territory | ACT | Canberra | south-east | Contains the nation's capital |

- National capital: **Canberra** (in the ACT).
- Biggest state by area: **Western Australia**.
- Smallest state by area: **Tasmania**.
- Only island state: **Tasmania**.

### A.2 Cities & towns

| City/Town | State | Note |
|-----------|-------|------|
| Sydney | NSW | Biggest city; Opera House & Harbour Bridge |
| Melbourne | VIC | Trams; MCG |
| Brisbane | QLD | Warm; Story Bridge |
| Perth | WA | On the west coast |
| Adelaide | SA | City of churches |
| Hobart | TAS | On the Derwent River |
| Darwin | NT | Hot and tropical |
| Canberra | ACT | The capital |
| Cairns | QLD | Gateway to the Reef |
| Gold Coast | QLD | Theme parks & surf beaches |
| Alice Springs | NT | In the middle of the Outback |
| Broome | WA | Cable Beach & camels |
| Byron Bay | NSW | Most easterly town; lighthouse |
| Ballarat | VIC | Old goldfields |
| Newcastle | NSW | Coal & beaches |
| Townsville | QLD | Tropical north |
| Geelong | VIC | Bayside city |
| Wollongong | NSW | Beaches south of Sydney |
| Launceston | TAS | Northern Tasmania |
| Katherine | NT | Gorge country |

- Biggest city: **Sydney**. Most easterly town: **Byron Bay**.

### A.3 Landmarks

| Landmark | State/Territory | What it is |
|----------|-----------------|-----------|
| Uluru (Ayers Rock) | NT | Giant red rock |
| Sydney Opera House | NSW | Famous white sail-shaped building |
| Sydney Harbour Bridge | NSW | Big steel arch bridge ("the Coathanger") |
| Great Barrier Reef | QLD | World's biggest coral reef |
| Twelve Apostles | VIC | Rock stacks by the ocean |
| Bondi Beach | NSW | Famous surf beach |
| Kakadu National Park | NT | Wetlands & rock art |
| Blue Mountains | NSW | Blue-hazed mountains; Three Sisters |
| Melbourne Cricket Ground (MCG) | VIC | Huge sports stadium |
| Kangaroo Island | SA | Wildlife island |
| Great Ocean Road | VIC | Coastal road |
| Daintree Rainforest | QLD | Ancient rainforest |
| Wave Rock | WA | Rock shaped like a wave |
| Fraser Island (K'gari) | QLD | Biggest sand island |
| Port Arthur | TAS | Historic site |

### A.4 Rivers, lakes & mountains

| Feature | Type | Note |
|---------|------|------|
| Murray River | river | Australia's longest river |
| Darling River | river | Long inland river |
| Murrumbidgee River | river | Feeds the Murray |
| Lake Eyre (Kati Thanda) | lake | Biggest lake; often dry |
| Mount Kosciuszko | mountain | Tallest mountain on the mainland |
| Snowy Mountains | mountains | Snow in winter |
| Blue Mountains | mountains | Near Sydney |
| Grampians | mountains | In Victoria |
| MacDonnell Ranges | mountains | Near Alice Springs |

- Longest river: **Murray**. Tallest mountain: **Mount Kosciuszko**. Biggest lake: **Lake Eyre**.

### A.5 Beaches, oceans & reefs

| Water/Beach | Where | Note |
|-------------|-------|------|
| Indian Ocean | west | On Australia's west side |
| Pacific Ocean | east | On Australia's east side |
| Southern Ocean | south | Below Australia |
| Coral Sea | north-east | By the Great Barrier Reef |
| Tasman Sea | south-east | Between Australia and New Zealand |
| Bass Strait | south | Between the mainland and Tasmania |
| Bondi Beach | NSW | Famous surf beach |
| Surfers Paradise | QLD | Gold Coast beach |
| Cable Beach | WA | Broome; camel rides |
| Whitehaven Beach | QLD | White sand, Whitsundays |

### A.6 Deserts & the Outback

| Place | Note |
|-------|------|
| The Outback | Dry red centre of Australia |
| Simpson Desert | Red sand dunes |
| Great Victoria Desert | Biggest desert |
| Nullarbor Plain | Flat, treeless; long road & train |
| Alice Springs | Main Outback town |

### A.7 Flags, symbols & directions

- Australian flag colours: **red, white and blue**.
- Flag features: **Union Jack**, the big **Commonwealth Star**, and the **Southern Cross** stars.
- Sporting colours: **green and gold**.
- National floral emblem: **golden wattle**.
- Coat of arms animals: **kangaroo and emu** (they can't easily walk backwards).
- Map directions: up = **north**, down = **south**, right = **east**, left = **west**.

### A.8 Weather & climate

- Hot, tropical north: **Darwin, Cairns** (wet season & dry season).
- Cooler south: **Hobart, Melbourne**.
- Snow: **Snowy Mountains / Australian Alps** in winter.
- Seasons are opposite to the northern hemisphere: **Christmas is in summer**.
- Hottest months: **December–February (summer)**; coldest: **June–August (winter)**.

### A.9 Animals tied to places

| Animal | Place | Note |
|--------|-------|------|
| Koala | eucalyptus/bush (east coast) | Eats gum leaves |
| Kangaroo | bush & grasslands | On the coat of arms |
| Saltwater crocodile | northern rivers (NT/QLD) | Lives in warm north |
| Little penguin | Phillip Island (VIC) | Famous penguin parade |
| Quokka | Rottnest Island (WA) | The "happiest" animal |
| Tasmanian devil | Tasmania | Only found in Tasmania |
| Clownfish/coral fish | Great Barrier Reef (QLD) | Colourful reef fish |
| Emu | across the Outback | Big bird that can't fly |
| Dingo | Fraser Island & Outback | Wild dog |
| Wombat | southern bush | Digs burrows |

---

## Appendix B — Comparison generators (for volume)

These produce many unique questions from ordered lists (correct answer + 2 fixed
distractors like "they are the same" / "you cannot tell"):

- **Bigger by area:** ordered states/territories → "Which is bigger, {A} or {B}?"
- **Further north:** ordered cities by latitude → "Which city is further north, {A} or {B}?"
- **Hotter/cooler:** north-to-south cities → "Which is usually hotter, {A} or {B}?"
- **Capital matching:** "Is {city} the capital of {state}?" style paired facts.

A `+N` gap between list indices keeps each pair clearly different (as in the science
quiz), avoiding near-ties that could confuse young kids.

---

## Appendix C — Estimated question yield

| Source | Rough count |
|--------|-------------|
| States/territories templates | ~120 |
| Cities & towns templates | ~180 |
| Landmarks templates | ~120 |
| Rivers/lakes/mountains templates | ~90 |
| Beaches/oceans/reefs templates | ~90 |
| Deserts/Outback templates | ~60 |
| Flags/symbols/directions facts | ~70 |
| Weather/climate facts | ~70 |
| Animals-in-places templates | ~120 |
| Comparison generators | ~250+ |
| **Total available** | **~1170+** (trimmed to 1000) |

If the total falls short at build time, the script errors out and we add more rows
until it comfortably exceeds 1000.

---

**Reply "approved" to generate the quiz, or tell me what to change in this plan.**
