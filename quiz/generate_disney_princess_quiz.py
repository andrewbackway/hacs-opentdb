# -*- coding: utf-8 -*-
"""
Generate a Disney Princess & Fairy Tales quiz for 5-year-old kids.
- 1000 unique multiple-choice questions (4 short options each)
- Correct answer stored as text
- Options shuffled so the answer isn't always in the same spot
- Only simple factual trivia; no song lyrics or verbatim story text.
Run:  python generate_disney_princess_quiz.py
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
# CORE DATA — princesses
# ==========================================================================
PRINCESSES = [
    {"name": "Cinderella", "film": "Cinderella", "hair": "blonde", "dress": "blue",
     "home": "a big castle", "trait": "lost a glass slipper"},
    {"name": "Snow White", "film": "Snow White", "hair": "black", "dress": "blue and yellow",
     "home": "a cottage in the forest", "trait": "is friends with seven dwarfs"},
    {"name": "Aurora", "film": "Sleeping Beauty", "hair": "blonde", "dress": "pink",
     "home": "a royal castle", "trait": "slept under a magic spell"},
    {"name": "Ariel", "film": "The Little Mermaid", "hair": "red", "dress": "green",
     "home": "under the sea", "trait": "is a mermaid"},
    {"name": "Belle", "film": "Beauty and the Beast", "hair": "brown", "dress": "yellow",
     "home": "a French village", "trait": "loves reading books"},
    {"name": "Jasmine", "film": "Aladdin", "hair": "black", "dress": "teal",
     "home": "a desert palace", "trait": "has a pet tiger"},
    {"name": "Rapunzel", "film": "Tangled", "hair": "long blonde", "dress": "purple",
     "home": "a tall tower", "trait": "has very long magic hair"},
    {"name": "Elsa", "film": "Frozen", "hair": "white-blonde", "dress": "ice blue",
     "home": "a snowy kingdom", "trait": "can make ice and snow"},
    {"name": "Anna", "film": "Frozen", "hair": "red-brown", "dress": "green and blue",
     "home": "a snowy kingdom", "trait": "is Elsa's brave sister"},
    {"name": "Moana", "film": "Moana", "hair": "wavy brown", "dress": "red and cream",
     "home": "a tropical island", "trait": "sails across the ocean"},
    {"name": "Tiana", "film": "The Princess and the Frog", "hair": "black", "dress": "green",
     "home": "the city of New Orleans", "trait": "dreams of a restaurant"},
    {"name": "Mulan", "film": "Mulan", "hair": "dark", "dress": "pink",
     "home": "a village in China", "trait": "is a brave warrior"},
    {"name": "Merida", "film": "Brave", "hair": "curly red", "dress": "green",
     "home": "a Scottish castle", "trait": "is great at archery"},
    {"name": "Pocahontas", "film": "Pocahontas", "hair": "long black", "dress": "tan",
     "home": "the forest by a river", "trait": "is friends with nature"},
]
NAME_POOL = [p["name"] for p in PRINCESSES]
FILM_POOL = list(dict.fromkeys(p["film"] for p in PRINCESSES))
HAIR_POOL = list(dict.fromkeys(p["hair"] for p in PRINCESSES))
DRESS_POOL = list(dict.fromkeys(p["dress"] for p in PRINCESSES))
HOME_POOL = list(dict.fromkeys(p["home"] for p in PRINCESSES))
PAIR_EXTRAS = ["both of them", "neither of them"]

# ---- base per-princess questions -----------------------------------------
for p in PRINCESSES:
    add(f"Which film is {p['name']} in?", p["film"], FILM_POOL)
    add(f"What colour is {p['name']}'s hair?", p["hair"], HAIR_POOL)
    add(f"What colour dress is {p['name']} best known for?", p["dress"], DRESS_POOL)
    add(f"Where does {p['name']} live?", p["home"], HOME_POOL)
    add(f"Which princess {p['trait']}?", p["name"], NAME_POOL)

# ==========================================================================
# MATCHING / COMPARISON GENERATORS (volume)
# ==========================================================================
def pairwise(field, question_tmpl):
    """For every princess pair with different `field`, ask which one has it."""
    for i in range(len(PRINCESSES)):
        for j in range(i + 1, len(PRINCESSES)):
            a, b = PRINCESSES[i], PRINCESSES[j]
            if a[field] == b[field]:
                continue
            add(question_tmpl(a, b, a), a["name"], [b["name"]] + PAIR_EXTRAS)
            add(question_tmpl(b, a, b), b["name"], [a["name"]] + PAIR_EXTRAS)


pairwise("hair", lambda a, b, who:
         f"Which princess has {who['hair']} hair, {a['name']} or {b['name']}?")
pairwise("dress", lambda a, b, who:
         f"Which princess is known for a {who['dress']} dress, {a['name']} or {b['name']}?")
pairwise("home", lambda a, b, who:
         f"Which princess lives in {who['home']}, {a['name']} or {b['name']}?")
pairwise("film", lambda a, b, who:
         f"Which princess is in the film {who['film']}, {a['name']} or {b['name']}?")

# ---- trait pairwise: "Which princess {trait}, A or B?" -------------------
for t in PRINCESSES:
    for o in PRINCESSES:
        if o["name"] == t["name"]:
            continue
        add(f"Which princess {t['trait']}, {t['name']} or {o['name']}?",
            t["name"], [o["name"]] + PAIR_EXTRAS)

# ==========================================================================
# CLASSIC FAIRY TALES — direct facts
# ==========================================================================
FAIRY_FACTS = [
    ("In which story does a girl lose a glass slipper at midnight?", "Cinderella",
     ["Snow White", "Aladdin", "Mulan"]),
    ("Who bites a poisoned apple and falls fast asleep?", "Snow White",
     ["Cinderella", "Ariel", "Moana"]),
    ("In which story does a princess prick her finger and sleep for years?",
     "Sleeping Beauty", ["Cinderella", "Aladdin", "Brave"]),
    ("What did Jack climb up in the fairy tale?", "a beanstalk",
     ["a mountain", "a ladder", "a big tree"]),
    ("How many little pigs are in the story?", "three", ["two", "four", "five"]),
    ("Who ate the three bears' porridge?", "Goldilocks",
     ["Cinderella", "Snow White", "Belle"]),
    ("Who did Little Red Riding Hood meet in the woods?", "a wolf",
     ["a bear", "a lion", "a dragon"]),
    ("Who runs away shouting 'you can't catch me'?", "the Gingerbread Man",
     ["the Frog Prince", "Pinocchio", "Peter Pan"]),
    ("What does the Ugly Duckling grow up to be?", "a beautiful swan",
     ["a big dog", "a horse", "a fish"]),
    ("What does the frog turn into when the princess is kind to it?", "a prince",
     ["a bird", "a dragon", "a fish"]),
    ("Which two children find a house made of sweets?", "Hansel and Gretel",
     ["the three pigs", "Jack and Jill", "the seven dwarfs"]),
    ("Who can spin straw into gold in the fairy tale?", "Rumpelstiltskin",
     ["the fairy godmother", "the genie", "the wolf"]),
    ("In which story is a pea hidden under lots of mattresses?",
     "the Princess and the Pea", ["Cinderella", "Rapunzel", "Frozen"]),
    ("Who lets down her long hair from a tall tower?", "Rapunzel",
     ["Ariel", "Belle", "Moana"]),
    ("In which story does a beast turn into a prince?", "Beauty and the Beast",
     ["Aladdin", "Mulan", "Brave"]),
    ("How many dwarfs live with Snow White?", "seven", ["three", "five", "ten"]),
    ("Who helps Cinderella get ready for the ball?", "her fairy godmother",
     ["a dragon", "a wizard", "a pirate"]),
    ("Who huffs and puffs to blow the little pigs' houses down?",
     "the big bad wolf", ["a giant", "a troll", "a bear"]),
    ("Who might live under a bridge in a fairy tale?", "a troll",
     ["a mermaid", "a fairy", "a prince"]),
    ("What did the wolf pretend to be in Little Red Riding Hood?", "Grandma",
     ["a prince", "a fairy", "a farmer"]),
    ("Who climbs the beanstalk to a giant's castle?", "Jack",
     ["Goldilocks", "Hansel", "Peter"]),
    ("How many bears live in the house Goldilocks visits?", "three",
     ["one", "two", "four"]),
    ("Who is very small and was found in a flower?", "Thumbelina",
     ["Cinderella", "Belle", "Aurora"]),
    ("Which boy's nose grows when he tells a lie?", "Pinocchio",
     ["Peter Pan", "Aladdin", "Jack"]),
    ("Who leaves a trail of breadcrumbs in the woods?", "Hansel and Gretel",
     ["Goldilocks", "Red Riding Hood", "the three pigs"]),
    ("What is the wolf's plan for the three little pigs?", "to blow their houses down",
     ["to help them build", "to sell them hats", "to teach them to swim"]),
    ("Which house did the wolf fail to blow down?", "the brick house",
     ["the straw house", "the stick house", "the paper house"]),
    ("What did the princess feel through all the mattresses?", "a tiny pea",
     ["a rock", "a coin", "a marble"]),
    ("In Beauty and the Beast, what does Belle love to do?", "read books",
     ["ride horses", "bake bread", "paint pictures"]),
    ("What does Rapunzel use to help someone climb the tower?", "her long hair",
     ["a rope", "a ladder", "a magic broom"]),
]
for q, correct, distractors in FAIRY_FACTS:
    add(q, correct, distractors)

# ==========================================================================
# CHARACTERS & CREATURES
# ==========================================================================
CHARACTER_FACTS = [
    ("What do we call the tiny magic helpers with wings in fairy tales?", "fairies",
     ["giants", "trolls", "wolves"]),
    ("What do we call a very big, tall make-believe person?", "a giant",
     ["a fairy", "a dwarf", "a mouse"]),
    ("What do we call the short, bearded miners in Snow White?", "dwarfs",
     ["giants", "elves", "knights"]),
    ("Who often casts wicked spells in fairy tales?", "a witch",
     ["a fairy godmother", "a puppy", "a baker"]),
    ("Who usually saves the princess in fairy tales?", "a prince",
     ["a wolf", "a witch", "a troll"]),
    ("What magical helper grants wishes from a lamp?", "a genie",
     ["a fairy", "a dwarf", "a giant"]),
    ("Which fairy tale creature can be big, green and scary?", "an ogre",
     ["a kitten", "a duckling", "a lamb"]),
    ("Who waves a wand to help Cinderella?", "the fairy godmother",
     ["the wicked stepmother", "the wolf", "the giant"]),
    ("Which character is very kind and helps with magic?", "a fairy godmother",
     ["a big bad wolf", "a wicked witch", "a hungry giant"]),
    ("What do dwarfs in Snow White dig for in their mine?", "gems and gold",
     ["carrots", "water", "shoes"]),
]
for q, correct, distractors in CHARACTER_FACTS:
    add(q, correct, distractors)

# ==========================================================================
# MAGIC OBJECTS
# ==========================================================================
OBJECT_FACTS = [
    ("What did Cinderella leave behind at the ball?", "a glass slipper",
     ["a glove", "a crown", "a ring"]),
    ("What does the wicked queen talk to on the wall?", "a magic mirror",
     ["a clock", "a painting", "a window"]),
    ("What comes out of Aladdin's magic lamp?", "a genie",
     ["a bird", "a fairy", "a puff of rain"]),
    ("What can Aladdin's magic carpet do?", "fly", ["cook", "sing", "swim"]),
    ("What did Sleeping Beauty prick her finger on?", "a spinning wheel",
     ["a rose", "a sword", "a fork"]),
    ("What kind of apple does the queen give Snow White?", "a poisoned apple",
     ["a green apple", "a golden apple", "a candy apple"]),
    ("What did Jack sell the cow for?", "magic beans",
     ["gold coins", "a horse", "a hat"]),
    ("What turns into Cinderella's coach?", "a pumpkin",
     ["a rock", "a barrel", "a box"]),
    ("How many wishes does the genie grant?", "three", ["one", "two", "five"]),
    ("What does a fairy godmother use to make magic?", "a magic wand",
     ["a hammer", "a spoon", "a broom"]),
    ("What does Cinderella's coach turn back into at midnight?", "a pumpkin",
     ["a cake", "a boat", "a house"]),
    ("What magic thing helps the princess in Aladdin travel the sky?",
     "a magic carpet", ["a magic boat", "a magic bike", "a magic sled"]),
]
for q, correct, distractors in OBJECT_FACTS:
    add(q, correct, distractors)

# ---- object -> story pairwise for volume ---------------------------------
OBJECTS = [
    ("a glass slipper", "Cinderella"),
    ("a magic mirror", "Snow White"),
    ("a spinning wheel", "Sleeping Beauty"),
    ("a magic lamp", "Aladdin"),
    ("a magic carpet", "Aladdin"),
    ("a poisoned apple", "Snow White"),
    ("magic beans", "Jack and the Beanstalk"),
    ("a pumpkin coach", "Cinderella"),
    ("a very long braid of hair", "Rapunzel"),
    ("seven dwarfs", "Snow White"),
]
STORY_POOL = list(dict.fromkeys(s for _, s in OBJECTS)) + [
    "Moana", "Brave", "Mulan", "Frozen"]
for obj, story in OBJECTS:
    add(f"In which story would you find {obj}?", story, STORY_POOL)

# ==========================================================================
# ANIMALS & SIDEKICKS
# ==========================================================================
SIDEKICKS = [
    {"name": "Flounder", "kind": "a fish", "owner": "Ariel"},
    {"name": "Sebastian", "kind": "a crab", "owner": "Ariel"},
    {"name": "Rajah", "kind": "a tiger", "owner": "Jasmine"},
    {"name": "Abu", "kind": "a monkey", "owner": "Aladdin"},
    {"name": "Pua", "kind": "a pig", "owner": "Moana"},
    {"name": "Heihei", "kind": "a chicken", "owner": "Moana"},
    {"name": "Olaf", "kind": "a snowman", "owner": "Elsa and Anna"},
    {"name": "Sven", "kind": "a reindeer", "owner": "Kristoff"},
    {"name": "Mushu", "kind": "a little dragon", "owner": "Mulan"},
    {"name": "Pascal", "kind": "a chameleon", "owner": "Rapunzel"},
    {"name": "Maximus", "kind": "a horse", "owner": "Rapunzel"},
]
KIND_POOL = list(dict.fromkeys(s["kind"] for s in SIDEKICKS))
OWNER_POOL = list(dict.fromkeys(s["owner"] for s in SIDEKICKS))
SIDEKICK_NAME_POOL = [s["name"] for s in SIDEKICKS]
for s in SIDEKICKS:
    add(f"What kind of animal is {s['name']}?", s["kind"], KIND_POOL)
    add(f"Who is {s['name']} a friend of?", s["owner"], OWNER_POOL)

add("Who is Ariel's cheerful little fish friend?", "Flounder",
    ["Sebastian", "Pua", "Abu"])
add("What is Jasmine's pet tiger called?", "Rajah",
    ["Abu", "Mushu", "Pascal"])
add("What is Moana's pet pig called?", "Pua",
    ["Heihei", "Sven", "Olaf"])
add("What is the friendly snowman in Frozen called?", "Olaf",
    ["Sven", "Mushu", "Pascal"])
add("What kind of animal is Sven in Frozen?", "a reindeer",
    ["a horse", "a dog", "a moose"])
add("What is Rapunzel's little chameleon friend called?", "Pascal",
    ["Maximus", "Mushu", "Abu"])

# ==========================================================================
# STORY ENDINGS & 'HAPPILY EVER AFTER'
# ==========================================================================
ENDING_FACTS = [
    ("How do many fairy tales end?", "happily ever after",
     ["with a big storm", "sadly", "with a running race"]),
    ("What do a prince and princess often do at the end of a fairy tale?",
     "get married", ["go to school", "build a boat", "plant a tree"]),
    ("In fairy tales, do the kind characters usually win in the end?", "yes",
     ["no", "never", "only at night"]),
    ("What often breaks a magic spell in fairy tales?", "true love's kiss",
     ["a loud sneeze", "a cup of tea", "a long nap"]),
    ("Many fairy tales begin with the words...", "once upon a time",
     ["the end", "good night", "see you soon"]),
    ("Many fairy tales finish with the words...", "happily ever after",
     ["once upon a time", "goodbye forever", "the beginning"]),
    ("At a royal ball, what do the prince and princess do?", "dance",
     ["do homework", "wash dishes", "mow the lawn"]),
    ("What wakes Sleeping Beauty from her long sleep?", "true love's kiss",
     ["a loud alarm", "a splash of water", "a bright torch"]),
    ("What kind of ending do fairy tales usually have?", "a happy ending",
     ["a scary ending", "a boring ending", "no ending"]),
    ("Who often becomes king and queen at the end?", "the prince and princess",
     ["the wolf and the witch", "the dwarfs", "the mice"]),
]
for q, correct, distractors in ENDING_FACTS:
    add(q, correct, distractors)

# ==========================================================================
# ASSEMBLE OUTPUT
# ==========================================================================
if len(questions) < 1000:
    raise SystemExit(
        f"Only produced {len(questions)} unique questions - add more facts.")

random.shuffle(questions)
final = questions[:1000]

output = {
    "topic": "Disney Princesses and Fairy Tales",
    "audience": "5-year-old kids",
    "difficulty": "easy",
    "count": len(final),
    "questions": final,
}

with open("disney-princess-fairytales-quiz.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Total unique questions available: {len(questions)}")
print(f"Wrote {len(final)} questions to disney-princess-fairytales-quiz.json")
