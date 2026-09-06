# -*- coding: utf-8 -*-
"""
Generate an Australian Geography quiz for kids under 10.
- 1000 unique multiple-choice questions (4 short options each)
- Correct answer stored as text
- Options shuffled so the answer isn't always in the same spot
Run:  python generate_australian_geography_quiz.py
"""
import json
import random

random.seed(7)

questions = []
seen = set()


def add(question, correct, distractor_pool):
    """Build one shuffled 4-option question; skip if question already used."""
    q = question.strip()
    key = q.lower()
    if key in seen:
        return
    pool = [d for d in dict.fromkeys(distractor_pool) if d != correct]
    if len(pool) < 3:
        return
    options = [correct] + random.sample(pool, 3)
    random.shuffle(options)
    seen.add(key)
    questions.append({"question": q, "options": options, "answer": correct})


# ==========================================================================
# A.1  STATES & TERRITORIES
# ==========================================================================
STATES = [
    {"name": "New South Wales", "capital": "Sydney", "loc": "south-east"},
    {"name": "Victoria", "capital": "Melbourne", "loc": "south-east"},
    {"name": "Queensland", "capital": "Brisbane", "loc": "north-east"},
    {"name": "South Australia", "capital": "Adelaide", "loc": "south"},
    {"name": "Western Australia", "capital": "Perth", "loc": "west"},
    {"name": "Tasmania", "capital": "Hobart", "loc": "south"},
    {"name": "Northern Territory", "capital": "Darwin", "loc": "north"},
    {"name": "Australian Capital Territory", "capital": "Canberra", "loc": "south-east"},
]
CAPITAL_POOL = [s["capital"] for s in STATES]
STATE_POOL = [s["name"] for s in STATES]
NOT_STATES = ["California", "London", "Fiji", "New Zealand", "Texas", "Bali"]
DIRECTION_POOL = ["north", "south", "east", "west",
                  "north-east", "south-east", "north-west", "south-west"]

for s in STATES:
    add(f"What is the capital city of {s['name']}?", s["capital"], CAPITAL_POOL)
    add(f"{s['capital']} is the capital of which state or territory?",
        s["name"], STATE_POOL)
    add(f"In which part of Australia is {s['name']}?", s["loc"], DIRECTION_POOL)

for ns in NOT_STATES:
    add(f"Is {ns} a state of Australia?", "no", ["yes", "only in winter", "sometimes"])

add("Which of these is a state of Australia?", "Queensland",
    ["Fiji", "California", "London"])
add("Which of these is a state of Australia?", "Victoria",
    ["Texas", "Bali", "New Zealand"])
add("Which of these is an Australian territory?", "Northern Territory",
    ["London", "Hawaii", "Fiji"])
add("What is the capital city of Australia?", "Canberra",
    ["Sydney", "Melbourne", "Perth"])
add("How many states does Australia have?", "6", ["3", "5", "8"])
add("Which is the biggest state in Australia?", "Western Australia",
    ["Tasmania", "Victoria", "New South Wales"])
add("Which is the smallest state in Australia?", "Tasmania",
    ["Western Australia", "Queensland", "New South Wales"])
add("Which state is an island?", "Tasmania",
    ["Queensland", "Victoria", "South Australia"])
add("Which state is home to the Great Barrier Reef?", "Queensland",
    ["Tasmania", "Victoria", "South Australia"])
add("In which territory is Uluru?", "Northern Territory",
    ["Tasmania", "Victoria", "Queensland"])

# ==========================================================================
# A.2  CITIES & TOWNS
# ==========================================================================
CITIES = [
    {"name": "Sydney", "state": "New South Wales"},
    {"name": "Melbourne", "state": "Victoria"},
    {"name": "Brisbane", "state": "Queensland"},
    {"name": "Perth", "state": "Western Australia"},
    {"name": "Adelaide", "state": "South Australia"},
    {"name": "Hobart", "state": "Tasmania"},
    {"name": "Darwin", "state": "Northern Territory"},
    {"name": "Canberra", "state": "Australian Capital Territory"},
    {"name": "Cairns", "state": "Queensland"},
    {"name": "Gold Coast", "state": "Queensland"},
    {"name": "Alice Springs", "state": "Northern Territory"},
    {"name": "Broome", "state": "Western Australia"},
    {"name": "Byron Bay", "state": "New South Wales"},
    {"name": "Ballarat", "state": "Victoria"},
    {"name": "Newcastle", "state": "New South Wales"},
    {"name": "Townsville", "state": "Queensland"},
    {"name": "Geelong", "state": "Victoria"},
    {"name": "Wollongong", "state": "New South Wales"},
    {"name": "Launceston", "state": "Tasmania"},
    {"name": "Katherine", "state": "Northern Territory"},
]
for c in CITIES:
    add(f"In which state or territory is {c['name']}?", c["state"], STATE_POOL)

add("Which is Australia's biggest city?", "Sydney",
    ["Hobart", "Darwin", "Canberra"])
add("Which city has the Sydney Opera House?", "Sydney",
    ["Melbourne", "Perth", "Adelaide"])
add("Which city is famous for its trams?", "Melbourne",
    ["Darwin", "Cairns", "Broome"])
add("Which town sits in the middle of the Outback?", "Alice Springs",
    ["Bondi", "Byron Bay", "Cairns"])
add("Which town is the most easterly in Australia?", "Byron Bay",
    ["Perth", "Broome", "Darwin"])
add("Which city is the gateway to the Great Barrier Reef?", "Cairns",
    ["Adelaide", "Hobart", "Canberra"])
add("Which place is famous for theme parks and surf beaches?", "Gold Coast",
    ["Alice Springs", "Canberra", "Ballarat"])
add("Which city is Australia's capital?", "Canberra",
    ["Sydney", "Melbourne", "Brisbane"])
add("Which city is hot and tropical in the far north?", "Darwin",
    ["Hobart", "Melbourne", "Adelaide"])
add("Which town is famous for Cable Beach and camels?", "Broome",
    ["Geelong", "Newcastle", "Ballarat"])

# ==========================================================================
# A.3  LANDMARKS
# ==========================================================================
LANDMARKS = [
    {"name": "Uluru", "state": "Northern Territory", "what": "a giant red rock"},
    {"name": "the Sydney Opera House", "state": "New South Wales", "what": "a famous building"},
    {"name": "the Sydney Harbour Bridge", "state": "New South Wales", "what": "a big steel bridge"},
    {"name": "the Great Barrier Reef", "state": "Queensland", "what": "a coral reef"},
    {"name": "the Twelve Apostles", "state": "Victoria", "what": "rocks by the ocean"},
    {"name": "Bondi Beach", "state": "New South Wales", "what": "a famous beach"},
    {"name": "Kakadu National Park", "state": "Northern Territory", "what": "a national park"},
    {"name": "the Blue Mountains", "state": "New South Wales", "what": "mountains"},
    {"name": "the Melbourne Cricket Ground", "state": "Victoria", "what": "a sports stadium"},
    {"name": "Kangaroo Island", "state": "South Australia", "what": "a wildlife island"},
    {"name": "the Great Ocean Road", "state": "Victoria", "what": "a coastal road"},
    {"name": "the Daintree Rainforest", "state": "Queensland", "what": "a rainforest"},
    {"name": "Wave Rock", "state": "Western Australia", "what": "a wave-shaped rock"},
    {"name": "Fraser Island", "state": "Queensland", "what": "a big sand island"},
    {"name": "Port Arthur", "state": "Tasmania", "what": "a historic site"},
]
WHAT_POOL = ["a giant red rock", "a famous building", "a big steel bridge",
             "a coral reef", "rocks by the ocean", "a famous beach",
             "a national park", "mountains", "a sports stadium",
             "a wildlife island", "a coastal road", "a rainforest",
             "a wave-shaped rock", "a big sand island", "a historic site"]
for lm in LANDMARKS:
    add(f"In which state or territory is {lm['name']}?", lm["state"], STATE_POOL)
    add(f"What is {lm['name']}?", lm["what"], WHAT_POOL)

add("What is the big red rock in the middle of Australia called?", "Uluru",
    ["Wave Rock", "the Twelve Apostles", "Bondi Beach"])
add("Which famous white building looks like sails in Sydney?",
    "the Sydney Opera House",
    ["the MCG", "Wave Rock", "Kakadu"])
add("What is the world's biggest coral reef, found in Australia?",
    "the Great Barrier Reef",
    ["the Blue Mountains", "Uluru", "the Twelve Apostles"])
add("What is Sydney's famous steel arch bridge called?",
    "the Sydney Harbour Bridge",
    ["the Great Ocean Road", "Wave Rock", "Port Arthur"])

# ==========================================================================
# A.4  RIVERS, LAKES & MOUNTAINS
# ==========================================================================
FEATURES = [
    {"name": "the Murray River", "type": "a river"},
    {"name": "the Darling River", "type": "a river"},
    {"name": "the Murrumbidgee River", "type": "a river"},
    {"name": "Lake Eyre", "type": "a lake"},
    {"name": "Mount Kosciuszko", "type": "a mountain"},
    {"name": "the Snowy Mountains", "type": "mountains"},
    {"name": "the Blue Mountains", "type": "mountains"},
    {"name": "the Grampians", "type": "mountains"},
    {"name": "the MacDonnell Ranges", "type": "mountains"},
]
TYPE_POOL = ["a river", "a lake", "a mountain", "mountains"]
for f in FEATURES:
    add(f"Is {f['name']} a river, a lake or a mountain?", f["type"], TYPE_POOL)

add("What is Australia's longest river?", "the Murray River",
    ["the Darling River", "the Snowy River", "the Yarra River"])
add("What is the tallest mountain on the Australian mainland?",
    "Mount Kosciuszko",
    ["Uluru", "the Blue Mountains", "Wave Rock"])
add("What is Australia's biggest lake, which is often dry?", "Lake Eyre",
    ["Lake Eyre is always full", "the Murray River", "Bondi Beach"])
add("Where in Australia can you often see snow in winter?",
    "the Snowy Mountains",
    ["the Simpson Desert", "Bondi Beach", "Darwin"])

# ==========================================================================
# A.5  BEACHES, OCEANS & REEFS
# ==========================================================================
WATERS = [
    {"name": "the Indian Ocean", "side": "west"},
    {"name": "the Pacific Ocean", "side": "east"},
    {"name": "the Southern Ocean", "side": "south"},
    {"name": "the Coral Sea", "side": "north-east"},
    {"name": "the Tasman Sea", "side": "south-east"},
]
SIDE_POOL = ["west", "east", "south", "north", "north-east", "south-east"]
for w in WATERS:
    add(f"On which side of Australia is {w['name']}?", w["side"], SIDE_POOL)

add("What do we call the huge reef off the coast of Queensland?",
    "the Great Barrier Reef",
    ["the Indian Ocean", "Lake Eyre", "the Murray River"])
add("Which sea is between Australia and New Zealand?", "the Tasman Sea",
    ["the Indian Ocean", "the Coral Sea", "the Southern Ocean"])
add("Which water is between the mainland and Tasmania?", "Bass Strait",
    ["the Coral Sea", "the Indian Ocean", "the Pacific Ocean"])
add("Which is a famous surf beach in Sydney?", "Bondi Beach",
    ["Cable Beach", "Whitehaven Beach", "Surfers Paradise"])
add("Which beach has bright white sand in the Whitsundays?",
    "Whitehaven Beach",
    ["Bondi Beach", "Cable Beach", "Surfers Paradise"])
add("On which side of Australia is the sun over the ocean at sunset?",
    "west", ["east", "north", "south"])

# ==========================================================================
# A.6  DESERTS & THE OUTBACK
# ==========================================================================
add("What do we call the dry, red middle part of Australia?", "the Outback",
    ["the Great Barrier Reef", "the Snowy Mountains", "the Gold Coast"])
add("Is the desert usually wet or dry?", "dry", ["wet", "snowy", "muddy"])
add("What colour is the sand in much of the Australian Outback?", "red",
    ["blue", "green", "purple"])
add("Which is Australia's biggest desert?", "the Great Victoria Desert",
    ["the Simpson Desert", "the Sahara Desert", "the Gobi Desert"])
add("Which desert is famous for its long red sand dunes?",
    "the Simpson Desert",
    ["the Great Barrier Reef", "the Blue Mountains", "Kakadu"])
add("What is the flat, treeless plain in southern Australia called?",
    "the Nullarbor Plain",
    ["the Blue Mountains", "the Snowy Mountains", "the Daintree"])
add("Which town is the main stop in the middle of the Outback?",
    "Alice Springs",
    ["Sydney", "Hobart", "Cairns"])

# ==========================================================================
# A.7  FLAGS, SYMBOLS & DIRECTIONS
# ==========================================================================
add("What colours are on the Australian flag?", "red, white and blue",
    ["green and gold", "black and orange", "pink and purple"])
add("Which group of stars is on the Australian flag?", "the Southern Cross",
    ["the Big Dipper", "the North Star", "the Sun"])
add("What are Australia's sporting colours?", "green and gold",
    ["red and blue", "black and white", "pink and grey"])
add("Which two animals are on the Australian coat of arms?",
    "the kangaroo and the emu",
    ["the koala and the wombat", "the shark and the crab", "the dog and the cat"])
add("What is Australia's flower emblem?", "the golden wattle",
    ["the rose", "the tulip", "the daisy"])
add("On a map, which way is up?", "north", ["south", "east", "west"])
add("On a map, which way is down?", "south", ["north", "east", "west"])
add("On a map, which way is to the right?", "east", ["west", "north", "south"])
add("On a map, which way is to the left?", "west", ["east", "north", "south"])
add("If Perth is in the west and Sydney is in the east, which is in the west?",
    "Perth", ["Sydney", "both", "neither"])

# ==========================================================================
# A.8  WEATHER & CLIMATE
# ==========================================================================
add("Which Australian city is hot and tropical?", "Darwin",
    ["Hobart", "Canberra", "Melbourne"])
add("Which Australian city is one of the coolest?", "Hobart",
    ["Darwin", "Cairns", "Broome"])
add("In Australia, Christmas comes in which season?", "summer",
    ["winter", "autumn", "spring"])
add("Which months are usually the hottest in Australia?",
    "December, January and February",
    ["June, July and August", "March, April and May", "September and October"])
add("Which months are usually the coldest in Australia?",
    "June, July and August",
    ["December, January and February", "March and April", "October and November"])
add("Where in Australia can you go skiing in the snow?",
    "the Snowy Mountains",
    ["Darwin", "the Simpson Desert", "Bondi Beach"])
add("The far north of Australia has a wet season and a...", "dry season",
    ["snow season", "leaf season", "sand season"])
add("Are Australia's seasons the same as or opposite to Europe's?",
    "opposite", ["exactly the same", "there are no seasons", "always winter"])

# ==========================================================================
# A.9  ANIMALS TIED TO PLACES
# ==========================================================================
PLACE_ANIMALS = [
    {"animal": "a Tasmanian devil", "place": "Tasmania"},
    {"animal": "a quokka", "place": "Rottnest Island"},
    {"animal": "a little penguin", "place": "Phillip Island"},
    {"animal": "a saltwater crocodile", "place": "the northern rivers"},
    {"animal": "a koala", "place": "the gum trees"},
    {"animal": "a dingo", "place": "Fraser Island"},
]
PLACE_POOL = ["Tasmania", "Rottnest Island", "Phillip Island",
              "the northern rivers", "the gum trees", "Fraser Island",
              "the Great Barrier Reef", "the Snowy Mountains"]
for pa in PLACE_ANIMALS:
    add(f"Where would you find {pa['animal']}?", pa["place"], PLACE_POOL)

add("Which animal is only found in the wild in Tasmania?",
    "the Tasmanian devil",
    ["the koala", "the emu", "the dingo"])
add("On which island can you see happy little quokkas?", "Rottnest Island",
    ["Kangaroo Island", "Fraser Island", "Phillip Island"])
add("Where do lots of colourful fish live in Australia?",
    "the Great Barrier Reef",
    ["the Simpson Desert", "the Snowy Mountains", "the Nullarbor Plain"])
add("Which big bird that cannot fly lives across the Outback?", "the emu",
    ["the penguin", "the parrot", "the duck"])
add("Which Australian animal hops and carries its baby in a pouch?",
    "the kangaroo",
    ["the crocodile", "the quokka", "the dingo"])

# ==========================================================================
# B. COMPARISON GENERATORS (volume)
# ==========================================================================
# States/territories ordered smallest -> biggest by area (all pairs)
AREA_ORDER = [
    "the Australian Capital Territory", "Tasmania", "Victoria",
    "New South Wales", "South Australia", "Queensland",
    "the Northern Territory", "Western Australia",
]
for i in range(len(AREA_ORDER)):
    for j in range(i + 1, len(AREA_ORDER)):
        small, big = AREA_ORDER[i], AREA_ORDER[j]
        add(f"Which is bigger, {small} or {big}?", big,
            [small, "they are the same size", "you cannot tell"])
        add(f"Which is smaller, {small} or {big}?", small,
            [big, "they are the same size", "you cannot tell"])

# Cities ordered north -> south (roughly by latitude)
NORTH_SOUTH = [
    "Darwin", "Katherine", "Cairns", "Broome", "Townsville",
    "Alice Springs", "Brisbane", "Gold Coast", "Byron Bay", "Perth",
    "Newcastle", "Sydney", "Wollongong", "Adelaide", "Canberra",
    "Ballarat", "Melbourne", "Geelong", "Launceston", "Hobart",
]
# North/south direction: skip nearby pairs (+2) to keep it clear
for i in range(len(NORTH_SOUTH)):
    for j in range(i + 2, len(NORTH_SOUTH)):
        north, south = NORTH_SOUTH[i], NORTH_SOUTH[j]
        add(f"Which city is further north, {north} or {south}?", north,
            [south, "they are the same", "you cannot tell"])
        add(f"Which city is further south, {north} or {south}?", south,
            [north, "they are the same", "you cannot tell"])
# Warmer/cooler: bigger gap (+3) so the temperature difference is clear
for i in range(len(NORTH_SOUTH)):
    for j in range(i + 3, len(NORTH_SOUTH)):
        north, south = NORTH_SOUTH[i], NORTH_SOUTH[j]
        add(f"Which city is usually warmer, {north} or {south}?", north,
            [south, "they are exactly the same", "you cannot tell"])
        add(f"Which city is usually cooler, {north} or {south}?", south,
            [north, "they are exactly the same", "you cannot tell"])

# Landmarks ordered north -> south (roughly by latitude)
LANDMARK_NS = [
    "Kakadu National Park", "the Daintree Rainforest", "the Great Barrier Reef",
    "Fraser Island", "Uluru", "Wave Rock", "the Blue Mountains",
    "the Sydney Harbour Bridge", "the Sydney Opera House", "Bondi Beach",
    "Kangaroo Island", "the Melbourne Cricket Ground", "the Great Ocean Road",
    "the Twelve Apostles", "Port Arthur",
]
for i in range(len(LANDMARK_NS)):
    for j in range(i + 2, len(LANDMARK_NS)):
        north, south = LANDMARK_NS[i], LANDMARK_NS[j]
        add(f"Which is further north, {north} or {south}?", north,
            [south, "they are the same", "you cannot tell"])
        add(f"Which is further south, {north} or {south}?", south,
            [north, "they are the same", "you cannot tell"])

# ==========================================================================
# ASSEMBLE OUTPUT
# ==========================================================================
if len(questions) < 1000:
    raise SystemExit(
        f"Only produced {len(questions)} unique questions - add more facts.")

random.shuffle(questions)
final = questions[:1000]

output = {
    "topic": "Australian Geography",
    "audience": "kids under 10 in Australia",
    "difficulty": "easy",
    "count": len(final),
    "questions": final,
}

with open("australian-geography-quiz.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Total unique questions available: {len(questions)}")
print(f"Wrote {len(final)} questions to australian-geography-quiz.json")
