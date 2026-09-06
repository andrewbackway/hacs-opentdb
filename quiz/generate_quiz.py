# -*- coding: utf-8 -*-
"""
Generate a Science & Nature quiz for 7-year-old kids in Australia.
- 1000 unique multiple-choice questions (4 short options each)
- Correct answer stored as text
- Options shuffled so the answer isn't always in the same spot
Run:  python generate_quiz.py
"""
import json
import random

random.seed(7)

questions = []
seen = set()

# ---- option pools (short text) -------------------------------------------
CLASS_POOL  = ["mammal", "bird", "fish", "reptile", "amphibian", "insect"]
COVER_POOL  = ["fur", "feathers", "scales", "smooth skin", "a hard shell"]
LEGS_POOL   = ["0 legs", "2 legs", "4 legs", "6 legs", "8 legs"]
COLOUR_POOL = ["red", "orange", "yellow", "green", "blue",
               "purple", "pink", "brown", "black", "white", "grey"]
HOME_POOL   = ["a nest", "a barn", "a burrow", "a den", "a hive", "a web",
               "a pond", "the ocean", "a cave", "a tree", "a stable",
               "underground", "the forest", "a river", "the desert", "a pouch"]
EAT_POOL    = ["grass and plants", "meat", "insects", "fish", "leaves",
               "seeds and nuts", "fruit", "both plants and meat",
               "nectar", "worms"]
SOUND_POOL  = ["bark", "meow", "moo", "oink", "baa", "neigh", "quack",
               "cluck", "tweet", "hiss", "roar", "growl", "buzz", "croak",
               "hoot", "squeak", "chirp", "howl", "trumpet", "ribbit"]
BABY_POOL   = ["puppy", "kitten", "calf", "piglet", "lamb", "foal",
               "duckling", "chick", "joey", "cub", "kid", "fawn",
               "tadpole", "gosling", "owlet", "hatchling", "pup", "colt"]


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


# ---- master animal table --------------------------------------------------
# keys: class, legs, baby, sound, cover, home, eats  (only where sensible)
ANIMALS = [
    {"name": "dog", "class": "mammal", "legs": "4 legs", "baby": "puppy", "sound": "bark", "cover": "fur", "home": "a kennel", "eats": "meat"},
    {"name": "cat", "class": "mammal", "legs": "4 legs", "baby": "kitten", "sound": "meow", "cover": "fur", "home": "a house", "eats": "meat"},
    {"name": "cow", "class": "mammal", "legs": "4 legs", "baby": "calf", "sound": "moo", "cover": "fur", "home": "a barn", "eats": "grass and plants"},
    {"name": "pig", "class": "mammal", "legs": "4 legs", "baby": "piglet", "sound": "oink", "cover": "fur", "home": "a farm", "eats": "both plants and meat"},
    {"name": "sheep", "class": "mammal", "legs": "4 legs", "baby": "lamb", "sound": "baa", "cover": "fur", "home": "a farm", "eats": "grass and plants"},
    {"name": "horse", "class": "mammal", "legs": "4 legs", "baby": "foal", "sound": "neigh", "cover": "fur", "home": "a stable", "eats": "grass and plants"},
    {"name": "duck", "class": "bird", "legs": "2 legs", "baby": "duckling", "sound": "quack", "cover": "feathers", "home": "a pond", "eats": "seeds and nuts"},
    {"name": "chicken", "class": "bird", "legs": "2 legs", "baby": "chick", "sound": "cluck", "cover": "feathers", "home": "a farm", "eats": "seeds and nuts"},
    {"name": "kangaroo", "class": "mammal", "legs": "2 legs", "baby": "joey", "cover": "fur", "home": "the bush", "eats": "grass and plants"},
    {"name": "koala", "class": "mammal", "legs": "4 legs", "baby": "joey", "cover": "fur", "home": "a tree", "eats": "leaves"},
    {"name": "lion", "class": "mammal", "legs": "4 legs", "baby": "cub", "sound": "roar", "cover": "fur", "home": "the grasslands", "eats": "meat"},
    {"name": "goat", "class": "mammal", "legs": "4 legs", "baby": "kid", "cover": "fur", "home": "a farm", "eats": "grass and plants"},
    {"name": "frog", "class": "amphibian", "legs": "4 legs", "baby": "tadpole", "sound": "croak", "cover": "smooth skin", "home": "a pond", "eats": "insects"},
    {"name": "owl", "class": "bird", "legs": "2 legs", "baby": "owlet", "sound": "hoot", "cover": "feathers", "home": "a tree", "eats": "meat"},
    {"name": "mouse", "class": "mammal", "legs": "4 legs", "baby": "pup", "sound": "squeak", "cover": "fur", "home": "a burrow", "eats": "seeds and nuts"},
    {"name": "wolf", "class": "mammal", "legs": "4 legs", "baby": "pup", "sound": "howl", "cover": "fur", "home": "a den", "eats": "meat"},
    {"name": "elephant", "class": "mammal", "legs": "4 legs", "baby": "calf", "sound": "trumpet", "cover": "smooth skin", "home": "the grasslands", "eats": "grass and plants"},
    {"name": "bee", "class": "insect", "legs": "6 legs", "sound": "buzz", "home": "a hive", "eats": "nectar"},
    {"name": "spider", "class": "insect", "legs": "8 legs", "home": "a web", "eats": "insects"},
    {"name": "fish", "class": "fish", "legs": "0 legs", "cover": "scales", "home": "the ocean", "eats": "insects"},
    {"name": "shark", "class": "fish", "legs": "0 legs", "cover": "smooth skin", "home": "the ocean", "eats": "fish"},
    {"name": "snake", "class": "reptile", "legs": "0 legs", "sound": "hiss", "cover": "scales", "home": "the grass", "eats": "meat"},
    {"name": "crocodile", "class": "reptile", "legs": "4 legs", "cover": "scales", "home": "a river", "eats": "meat"},
    {"name": "turtle", "class": "reptile", "legs": "4 legs", "baby": "hatchling", "cover": "a hard shell", "home": "the ocean", "eats": "both plants and meat"},
    {"name": "lizard", "class": "reptile", "legs": "4 legs", "cover": "scales", "home": "the desert", "eats": "insects"},
    {"name": "rabbit", "class": "mammal", "legs": "4 legs", "baby": "kit", "cover": "fur", "home": "a burrow", "eats": "grass and plants"},
    {"name": "bear", "class": "mammal", "legs": "4 legs", "baby": "cub", "sound": "growl", "cover": "fur", "home": "a cave", "eats": "both plants and meat"},
    {"name": "penguin", "class": "bird", "legs": "2 legs", "baby": "chick", "cover": "feathers", "home": "the ice", "eats": "fish"},
    {"name": "eagle", "class": "bird", "legs": "2 legs", "baby": "chick", "cover": "feathers", "home": "a nest", "eats": "meat"},
    {"name": "parrot", "class": "bird", "legs": "2 legs", "baby": "chick", "sound": "squawk", "cover": "feathers", "home": "a tree", "eats": "seeds and nuts"},
    {"name": "goose", "class": "bird", "legs": "2 legs", "baby": "gosling", "cover": "feathers", "home": "a pond", "eats": "grass and plants"},
    {"name": "cricket", "class": "insect", "legs": "6 legs", "sound": "chirp", "home": "the grass", "eats": "leaves"},
    {"name": "ant", "class": "insect", "legs": "6 legs", "home": "underground", "eats": "seeds and nuts"},
    {"name": "butterfly", "class": "insect", "legs": "6 legs", "home": "a garden", "eats": "nectar"},
    {"name": "ladybird", "class": "insect", "legs": "6 legs", "home": "a garden", "eats": "insects"},
    {"name": "octopus", "class": "sea animal", "legs": "8 legs", "cover": "smooth skin", "home": "the ocean", "eats": "fish"},
    {"name": "whale", "class": "mammal", "legs": "0 legs", "baby": "calf", "cover": "smooth skin", "home": "the ocean", "eats": "fish"},
    {"name": "dolphin", "class": "mammal", "legs": "0 legs", "baby": "calf", "cover": "smooth skin", "home": "the ocean", "eats": "fish"},
    {"name": "camel", "class": "mammal", "legs": "4 legs", "baby": "calf", "cover": "fur", "home": "the desert", "eats": "grass and plants"},
    {"name": "giraffe", "class": "mammal", "legs": "4 legs", "baby": "calf", "cover": "fur", "home": "the grasslands", "eats": "leaves"},
    {"name": "monkey", "class": "mammal", "legs": "4 legs", "baby": "infant", "cover": "fur", "home": "a tree", "eats": "fruit"},
    {"name": "tiger", "class": "mammal", "legs": "4 legs", "baby": "cub", "sound": "roar", "cover": "fur", "home": "the jungle", "eats": "meat"},
    {"name": "kookaburra", "class": "bird", "legs": "2 legs", "cover": "feathers", "home": "a tree", "eats": "insects"},
    {"name": "emu", "class": "bird", "legs": "2 legs", "cover": "feathers", "home": "the bush", "eats": "seeds and nuts"},
    {"name": "platypus", "class": "mammal", "legs": "4 legs", "cover": "fur", "home": "a river", "eats": "worms"},
    {"name": "echidna", "class": "mammal", "legs": "4 legs", "cover": "spikes", "home": "the bush", "eats": "insects"},
    {"name": "wombat", "class": "mammal", "legs": "4 legs", "cover": "fur", "home": "a burrow", "eats": "grass and plants"},
    {"name": "possum", "class": "mammal", "legs": "4 legs", "cover": "fur", "home": "a tree", "eats": "fruit"},
    {"name": "crab", "class": "sea animal", "legs": "8 legs", "cover": "a hard shell", "home": "the beach", "eats": "both plants and meat"},
    {"name": "seahorse", "class": "fish", "legs": "0 legs", "cover": "smooth skin", "home": "the ocean", "eats": "insects"},
    {"name": "bat", "class": "mammal", "legs": "2 legs", "cover": "fur", "home": "a cave", "eats": "insects"},
    {"name": "deer", "class": "mammal", "legs": "4 legs", "baby": "fawn", "cover": "fur", "home": "the forest", "eats": "grass and plants"},
    {"name": "fox", "class": "mammal", "legs": "4 legs", "baby": "cub", "cover": "fur", "home": "a den", "eats": "meat"},
    {"name": "swan", "class": "bird", "legs": "2 legs", "cover": "feathers", "home": "a lake", "eats": "grass and plants"},
    {"name": "peacock", "class": "bird", "legs": "2 legs", "cover": "feathers", "home": "a garden", "eats": "seeds and nuts"},
    {"name": "snail", "class": "bug", "legs": "0 legs", "cover": "a hard shell", "home": "a garden", "eats": "leaves"},
    {"name": "worm", "class": "bug", "legs": "0 legs", "cover": "smooth skin", "home": "underground", "eats": "leaves"},
    {"name": "grasshopper", "class": "insect", "legs": "6 legs", "home": "the grass", "eats": "leaves"},
    {"name": "starfish", "class": "sea animal", "legs": "0 legs", "cover": "smooth skin", "home": "the ocean", "eats": "both plants and meat"},
    {"name": "seal", "class": "mammal", "legs": "0 legs", "baby": "pup", "cover": "fur", "home": "the beach", "eats": "fish"},
    {"name": "hen", "class": "bird", "legs": "2 legs", "baby": "chick", "sound": "cluck", "cover": "feathers", "home": "a farm", "eats": "seeds and nuts"},
    {"name": "rooster", "class": "bird", "legs": "2 legs", "sound": "crow", "cover": "feathers", "home": "a farm", "eats": "seeds and nuts"},
    {"name": "donkey", "class": "mammal", "legs": "4 legs", "baby": "foal", "cover": "fur", "home": "a farm", "eats": "grass and plants"},
    {"name": "hippo", "class": "mammal", "legs": "4 legs", "baby": "calf", "cover": "smooth skin", "home": "a river", "eats": "grass and plants"},
    {"name": "zebra", "class": "mammal", "legs": "4 legs", "baby": "foal", "cover": "fur", "home": "the grasslands", "eats": "grass and plants"},
    {"name": "gorilla", "class": "mammal", "legs": "4 legs", "baby": "infant", "cover": "fur", "home": "the jungle", "eats": "fruit"},
    {"name": "kitten", "class": "mammal", "legs": "4 legs", "cover": "fur", "home": "a house", "eats": "meat"},
    {"name": "jellyfish", "class": "sea animal", "legs": "0 legs", "cover": "smooth skin", "home": "the ocean", "eats": "fish"},
    {"name": "beetle", "class": "insect", "legs": "6 legs", "home": "the garden", "eats": "leaves"},
    {"name": "moth", "class": "insect", "legs": "6 legs", "home": "the garden", "eats": "nectar"},
    {"name": "caterpillar", "class": "bug", "legs": "many legs", "home": "a leaf", "eats": "leaves"},
    {"name": "pelican", "class": "bird", "legs": "2 legs", "cover": "feathers", "home": "the beach", "eats": "fish"},
    {"name": "cockatoo", "class": "bird", "legs": "2 legs", "cover": "feathers", "home": "a tree", "eats": "seeds and nuts"},
]

for a in ANIMALS:
    n = a["name"]
    if "class" in a and a["class"] in CLASS_POOL:
        add(f"What kind of animal is a {n}?", a["class"], CLASS_POOL)
    if "legs" in a:
        add(f"How many legs does a {n} have?", a["legs"], LEGS_POOL)
    if "baby" in a:
        add(f"What do we call a baby {n}?", a["baby"], BABY_POOL)
    if "sound" in a and a["sound"] in SOUND_POOL:
        add(f"What sound does a {n} make?", a["sound"], SOUND_POOL)
    if "cover" in a and a["cover"] in COVER_POOL:
        add(f"What covers a {n}'s body?", a["cover"], COVER_POOL)
    if "home" in a:
        add(f"Where does a {n} like to live?", a["home"],
            HOME_POOL + [a["home"]])
    if "eats" in a:
        add(f"What does a {n} mostly eat?", a["eats"], EAT_POOL)

# ---- colours of things in nature -----------------------------------------
COLOURS = {
    "a banana": "yellow", "grass": "green", "the daytime sky": "blue",
    "snow": "white", "a lump of coal": "black", "a ripe tomato": "red",
    "a carrot": "orange", "a lemon": "yellow", "a strawberry": "red",
    "the sun": "yellow", "milk": "white", "a leaf": "green",
    "a red apple": "red", "a blueberry": "blue", "an eggplant": "purple",
    "a pumpkin": "orange", "a flamingo": "pink", "a polar bear": "white",
    "a ladybird": "red", "a sunflower": "yellow", "a cucumber": "green",
    "a lime": "green", "chocolate": "brown", "a tree trunk": "brown",
    "beach sand": "yellow", "a crow": "black", "a swan": "white",
    "peas": "green", "corn": "yellow", "a cherry": "red",
    "a plum": "purple", "broccoli": "green", "mud": "brown",
    "an orange": "orange", "a frog": "green", "coal": "black",
    "an emu's feathers": "black", "a kangaroo": "brown", "a koala": "grey",
    "a lettuce leaf": "green", "a fire truck": "red", "the night sky": "black",
    "a bee's stripes": "yellow", "a raspberry": "red", "a pea pod": "green",
    "a daffodil": "yellow", "a violet flower": "purple", "an olive": "green",
    "a watermelon skin": "green", "a peach": "orange", "a grape": "purple",
    "clean water": "clear", "a rose": "red", "a lettuce": "green",
    "a pineapple skin": "brown", "a mushroom": "white", "a zebra's stripes": "black",
    "a robin's chest": "red", "the moon at night": "white",
}
for obj, col in COLOURS.items():
    add(f"What colour is {obj}?", col, COLOUR_POOL)

# ---- direct topic facts: (question, correct, [distractors]) --------------
FACTS = [
    # human body
    ("What do we use our eyes for?", "seeing", ["hearing", "smelling", "tasting"]),
    ("What do we use our ears for?", "hearing", ["seeing", "smelling", "walking"]),
    ("What do we use our nose for?", "smelling", ["seeing", "hearing", "hopping"]),
    ("What do we use our tongue for?", "tasting", ["seeing", "hearing", "smelling"]),
    ("What do we use our legs for?", "walking", ["seeing", "smelling", "tasting"]),
    ("What do we use our hands for?", "holding things", ["seeing", "smelling", "hearing"]),
    ("What do we use our teeth for?", "chewing food", ["seeing", "hearing", "smelling"]),
    ("What do we use our lungs for?", "breathing", ["thinking", "chewing", "hopping"]),
    ("What part of your body helps you think?", "your brain", ["your foot", "your ear", "your knee"]),
    ("What pumps blood around your body?", "your heart", ["your nose", "your ear", "your toe"]),
    ("How many eyes does a person usually have?", "2", ["1", "3", "4"]),
    ("How many ears does a person usually have?", "2", ["1", "3", "5"]),
    ("How many fingers are on one hand?", "5", ["3", "4", "6"]),
    ("How many toes do we usually have in total?", "10", ["5", "8", "12"]),
    ("How many legs does a person have?", "2", ["1", "3", "4"]),
    ("How many noses does a person have?", "1", ["2", "3", "4"]),
    ("Which body part do you use to smell a flower?", "your nose", ["your ear", "your knee", "your elbow"]),
    ("Which body part helps you taste ice cream?", "your tongue", ["your ear", "your nose", "your foot"]),
    ("How many senses do people have?", "5", ["2", "3", "7"]),
    ("What do teeth help us do to our food?", "chew it", ["see it", "hear it", "smell it"]),
    # senses list
    ("Which of these is one of our five senses?", "smell", ["running", "jumping", "sleeping"]),
    ("Seeing is done with your...", "eyes", ["ears", "nose", "hands"]),
    ("Hearing is done with your...", "ears", ["eyes", "nose", "feet"]),
    ("Touching is done with your...", "hands", ["ears", "eyes", "nose"]),
    # weather / sky
    ("What falls from the sky when it rains?", "water", ["sand", "milk", "juice"]),
    ("What do we call frozen rain that is white and cold?", "snow", ["sand", "grass", "steam"]),
    ("What do you see in the sky on a sunny day?", "the sun", ["the moon", "stars", "snow"]),
    ("What might you see in the sky after rain and sunshine?", "a rainbow", ["a snowman", "a fish", "a car"]),
    ("What do we call the loud sound in a storm?", "thunder", ["a bark", "a moo", "a splash"]),
    ("What do we call the bright flash in a storm?", "lightning", ["a rainbow", "a cloud", "a star"]),
    ("What are the fluffy white things in the sky called?", "clouds", ["rocks", "leaves", "birds"]),
    ("When it is very windy, what moves the leaves on trees?", "the wind", ["the sun", "the moon", "the rain"]),
    ("What do we call water drops on the grass in the morning?", "dew", ["snow", "sand", "milk"]),
    ("Which is warmer, summer or winter?", "summer", ["winter", "they are the same", "neither"]),
    ("On a hot sunny day you should wear a...", "hat", ["scarf", "raincoat", "snow boots"]),
    ("What do we use to stay dry in the rain?", "an umbrella", ["a fan", "a towel", "a hat"]),
    # seasons
    ("Which season is the hottest?", "summer", ["winter", "autumn", "spring"]),
    ("Which season is the coldest?", "winter", ["summer", "spring", "autumn"]),
    ("In which season do many leaves fall from trees?", "autumn", ["summer", "spring", "winter"]),
    ("In which season do many flowers start to bloom?", "spring", ["winter", "autumn", "summer"]),
    ("How many seasons are there in a year?", "4", ["2", "3", "5"]),
    ("Which season comes after summer in Australia?", "autumn", ["winter", "spring", "summer"]),
    ("Which season comes after winter?", "spring", ["summer", "autumn", "winter"]),
    # space
    ("What is the sun?", "a star", ["a planet", "a cloud", "a moon"]),
    ("What planet do we live on?", "Earth", ["Mars", "the Moon", "the Sun"]),
    ("What do we see in the sky at night that is round and glows?", "the moon", ["the sun", "a rainbow", "a cloud"]),
    ("What tiny bright lights do we see in the night sky?", "stars", ["clouds", "rocks", "birds"]),
    ("The sun gives us light and...", "heat", ["rain", "snow", "wind"]),
    ("When can we see the moon and stars best?", "at night", ["at lunchtime", "in the morning", "at noon"]),
    ("What shape does the Earth look like?", "round like a ball", ["flat like paper", "square", "a triangle"]),
    ("How many suns are in our sky?", "1", ["2", "3", "many"]),
    ("Is the sun hot or cold?", "hot", ["cold", "wet", "soft"]),
    ("What do we call the day star that lights up the sky?", "the sun", ["the moon", "a cloud", "a comet"]),
    # plants
    ("What part of a plant is under the ground?", "the roots", ["the flower", "the leaf", "the fruit"]),
    ("What do plants need from the sky to grow?", "sunlight", ["darkness", "toys", "sand"]),
    ("What do we give plants to drink so they grow?", "water", ["milk", "juice", "soda"]),
    ("What part of a plant is often green and flat?", "the leaf", ["the root", "the seed", "the trunk"]),
    ("What grows into a new plant when you put it in soil?", "a seed", ["a rock", "a leaf", "a stick"]),
    ("Where do most plants grow their roots?", "in the soil", ["in the sky", "in the fire", "in the wind"]),
    ("What colour are most leaves?", "green", ["blue", "purple", "black"]),
    ("What do bees collect from flowers?", "nectar", ["water", "rocks", "leaves"]),
    ("A baby plant grows from a...", "seed", ["stone", "leaf", "cloud"]),
    ("Trees are very big plants that have a...", "trunk", ["tail", "wing", "fin"]),
    ("What do plants make that helps us breathe?", "clean air", ["smoke", "dust", "noise"]),
    ("Which of these grows on a tree?", "an apple", ["a fish", "a rock", "a car"]),
    # water and states
    ("What do we call water when it is frozen hard?", "ice", ["steam", "rain", "mud"]),
    ("Is ice hot or cold?", "cold", ["hot", "warm", "spicy"]),
    ("What do we call the cloud of gas when water boils?", "steam", ["ice", "sand", "smoke"]),
    ("What does water feel like?", "wet", ["dry", "fluffy", "hard"]),
    ("Where do fish live?", "in water", ["in trees", "in the sky", "under rocks in the desert"]),
    ("The sea water tastes...", "salty", ["sweet", "sour", "spicy"]),
    ("What happens to ice when it gets warm?", "it melts", ["it grows", "it flies", "it barks"]),
    ("Which of these is a drink of water?", "a glass of water", ["a rock", "a leaf", "a shoe"]),
    # materials
    ("What is paper mostly made from?", "trees", ["rocks", "water", "glass"]),
    ("What do we get from sheep to make warm jumpers?", "wool", ["milk", "eggs", "honey"]),
    ("What do bees make that is sweet and sticky?", "honey", ["milk", "juice", "jam"]),
    ("Which of these can you see through?", "glass", ["wood", "a brick", "a rock"]),
    ("What is a chair often made from?", "wood", ["water", "cloud", "smoke"]),
    ("What sticks to a magnet?", "metal", ["paper", "water", "grass"]),
    ("Which of these floats on water?", "a boat", ["a rock", "a brick", "a coin"]),
    ("Which of these usually sinks in water?", "a rock", ["a leaf", "a cork", "a duck"]),
    # farm / food
    ("What do we get from a cow to drink?", "milk", ["eggs", "wool", "honey"]),
    ("What do we get from a chicken to eat for breakfast?", "eggs", ["milk", "wool", "honey"]),
    ("Which of these is a fruit?", "an apple", ["a carrot", "a potato", "a rock"]),
    ("Which of these is a vegetable?", "a carrot", ["an apple", "a banana", "a grape"]),
    ("Where does a carrot grow?", "under the ground", ["on a tree", "in the sky", "in the sea"]),
    ("Which food is good for strong teeth and bones?", "milk", ["lollies", "chips", "cake"]),
    ("Bread is made from a plant called...", "wheat", ["metal", "plastic", "glass"]),
    # ocean / beach
    ("What do we call the big blue water at the beach?", "the ocean", ["a puddle", "a cup", "a lake of milk"]),
    ("Which animal has a hard shell and lives at the beach?", "a crab", ["a dog", "a cow", "a horse"]),
    ("Which big fish has lots of sharp teeth?", "a shark", ["a goldfish", "a duck", "a frog"]),
    ("What do we build at the beach with a bucket and sand?", "a sandcastle", ["a snowman", "a treehouse", "a boat"]),
    ("What do fish use to breathe under water?", "gills", ["lungs", "noses", "ears"]),
    ("What do fish have to help them swim?", "fins", ["legs", "wings", "hands"]),
    ("Which of these lives in the ocean?", "a dolphin", ["a cow", "a chicken", "a sheep"]),
    # day / night
    ("When is it dark outside?", "at night", ["at lunchtime", "in the morning", "at noon"]),
    ("When do most people sleep?", "at night", ["in the morning", "at lunch", "at play time"]),
    ("What is up in the sky during the day?", "the sun", ["the moon", "the stars", "a lamp"]),
    ("Roosters often make noise at...", "sunrise", ["midnight", "lunchtime", "dinner"]),
    # Australian nature
    ("Which Australian animal hops on two strong back legs?", "a kangaroo", ["a koala", "a wombat", "a fish"]),
    ("Which Australian animal sleeps in gum trees and eats leaves?", "a koala", ["a shark", "a horse", "a frog"]),
    ("Which Australian bird sounds like it is laughing?", "a kookaburra", ["a penguin", "an owl", "a duck"]),
    ("Which big Australian bird cannot fly?", "an emu", ["an eagle", "a parrot", "a duck"]),
    ("Which Australian animal has a bill like a duck and lays eggs?", "a platypus", ["a kangaroo", "a koala", "a lion"]),
    ("Which spiky Australian animal rolls into a ball?", "an echidna", ["a wombat", "a possum", "a swan"]),
    ("What do koalas mainly eat?", "gum leaves", ["fish", "meat", "grass seeds"]),
    ("Where does a baby kangaroo (joey) ride?", "in its mum's pouch", ["on its dad's back", "in a nest", "in the sea"]),
    ("The Great Barrier Reef in Australia is full of colourful...", "coral and fish", ["cars", "rocks", "snow"]),
    ("Which animal carries its baby in a pouch?", "a kangaroo", ["a dog", "a fish", "a bird"]),
    # bugs / insects
    ("How many legs does an insect have?", "6", ["2", "4", "8"]),
    ("How many legs does a spider have?", "8", ["4", "6", "10"]),
    ("What does a caterpillar turn into?", "a butterfly", ["a bird", "a frog", "a fish"]),
    ("Which insect makes honey?", "a bee", ["an ant", "a fly", "a spider"]),
    ("Which tiny insects work together and live in a nest in the ground?", "ants", ["fish", "cows", "birds"]),
    ("What does a spider spin to catch food?", "a web", ["a nest", "a shell", "a wing"]),
    ("Which insect glows in the dark?", "a firefly", ["a cow", "a fish", "a frog"]),
    # dinosaurs
    ("Dinosaurs lived on Earth...", "a very long time ago", ["yesterday", "last week", "tomorrow"]),
    ("Are there any real live dinosaurs walking around today?", "no", ["yes", "sometimes", "only at night"]),
    ("Which is a famous big meat-eating dinosaur?", "T. rex", ["a puppy", "a goldfish", "a rabbit"]),
    ("What do we call animals that lived long ago and are all gone now?", "extinct", ["asleep", "hiding", "swimming"]),
    # misc nature
    ("What do we call baby frogs before they grow legs?", "tadpoles", ["puppies", "chicks", "kittens"]),
    ("Which animal is known for being very slow and carries its home?", "a snail", ["a cheetah", "a horse", "a dog"]),
    ("What do birds build to lay their eggs in?", "a nest", ["a web", "a hive", "a den"]),
    ("What comes out of a bird's egg?", "a baby bird", ["a fish", "a puppy", "a flower"]),
    ("Butterflies have colourful...", "wings", ["fins", "shells", "horns"]),
    ("Which animal is the biggest on land?", "an elephant", ["a mouse", "a cat", "a rabbit"]),
    ("Which animal has a very long neck?", "a giraffe", ["a pig", "a duck", "a frog"]),
    ("Which animal is known as the king of the jungle?", "a lion", ["a sheep", "a mouse", "a fish"]),
    ("What do we call a very young dog?", "a puppy", ["a kitten", "a calf", "a chick"]),
    ("What do we call a very young cat?", "a kitten", ["a puppy", "a foal", "a joey"]),
    ("Which of these can fly?", "a bird", ["a fish", "a cow", "a snake"]),
    ("Which of these lives in water?", "a fish", ["a lion", "a cow", "a chicken"]),
    ("Which of these is a reptile?", "a snake", ["a dog", "a bird", "a bee"]),
    ("Which of these is a mammal?", "a dog", ["a fish", "a bee", "a frog"]),
    ("Which of these is a bird?", "an owl", ["a shark", "a frog", "a spider"]),
    ("What helps a fish move through the water?", "its tail and fins", ["its legs", "its wings", "its arms"]),
    ("Snakes move by...", "slithering", ["hopping", "flying", "swimming only"]),
    ("What do we call the outside of an egg?", "the shell", ["the fur", "the feather", "the scale"]),
    ("What grows on a bird to help it keep warm and fly?", "feathers", ["fur", "scales", "leaves"]),
    ("A group of trees together is called a...", "forest", ["desert", "beach", "river"]),
    ("A dry, sandy place with little water is a...", "desert", ["forest", "ocean", "swamp"]),
    ("Where do polar bears live?", "in cold, snowy places", ["in the hot desert", "in the jungle", "in the ocean"]),
    ("What do we call the water that falls in tiny drops from clouds?", "rain", ["snowballs", "sand", "leaves"]),
    ("What do you need to make a shadow?", "light", ["water", "wind", "sound"]),
    ("Which is bigger, an ant or an elephant?", "an elephant", ["an ant", "they are the same", "neither"]),
    ("Which is faster, a snail or a cheetah?", "a cheetah", ["a snail", "they are the same", "neither"]),
    ("What do caterpillars mostly eat?", "leaves", ["meat", "rocks", "metal"]),
    ("Which sea animal has eight arms?", "an octopus", ["a fish", "a crab", "a whale"]),
    ("What is the biggest animal in the ocean?", "a whale", ["a goldfish", "a crab", "a shrimp"]),
    ("Bats sleep during the day and come out at...", "night", ["lunchtime", "breakfast", "noon"]),
    ("What do we call it when a bear sleeps all winter?", "hibernation", ["swimming", "flying", "hopping"]),
    ("What part of a tree do birds often build nests in?", "the branches", ["the roots", "the soil", "the water"]),
    ("What do we call rain that is frozen into little balls?", "hail", ["dew", "steam", "smoke"]),
    ("Which animal changes colour to hide?", "a chameleon", ["a cow", "a horse", "a duck"]),
    ("What do plants take in from the air?", "carbon dioxide", ["milk", "sand", "juice"]),
    ("Which animal is famous for a very long jump and lives in Australia?", "a kangaroo", ["a snail", "a turtle", "a cow"]),
    ("What do we call a doctor for animals?", "a vet", ["a chef", "a pilot", "a teacher"]),
    ("What do plants grow from that we plant in the ground?", "seeds", ["rocks", "coins", "leaves"]),
    ("Which of these is a baby sheep?", "a lamb", ["a calf", "a foal", "a chick"]),
    ("Which of these is a baby cow?", "a calf", ["a lamb", "a piglet", "a puppy"]),
    ("Which of these is a baby horse?", "a foal", ["a chick", "a kitten", "a joey"]),
    ("Which season do we often go swimming because it is hot?", "summer", ["winter", "autumn", "spring"]),
    ("What do we call the ground that plants grow in?", "soil", ["glass", "metal", "plastic"]),
    ("What do worms help make healthy for plants?", "the soil", ["the sky", "the sun", "the moon"]),
    ("Which of these keeps you warm and comes from a sheep?", "wool", ["glass", "sand", "water"]),
    ("What do we call a baby kangaroo?", "a joey", ["a puppy", "a calf", "a chick"]),
    ("What colour do we often mix to get green?", "blue and yellow", ["red and black", "white and grey", "pink and brown"]),
    ("Rainbows appear when there is rain and...", "sunshine", ["snow", "wind", "thunder only"]),
    ("What do we call animals that only eat plants?", "herbivores", ["carnivores", "builders", "swimmers"]),
    ("What do we call animals that only eat meat?", "carnivores", ["herbivores", "planters", "flyers"]),
    ("Which body part protects your brain?", "your skull", ["your foot", "your hand", "your knee"]),
    ("What covers most of the Earth's surface?", "water", ["sand", "grass", "ice cream"]),
    ("What do leaves use from the sun to make food?", "sunlight", ["moonlight", "wind", "rain only"]),
    ("Which animal says 'moo'?", "a cow", ["a dog", "a cat", "a duck"]),
    ("Which animal says 'baa'?", "a sheep", ["a pig", "a horse", "a hen"]),
    ("Which animal says 'quack'?", "a duck", ["a cow", "a lion", "a cat"]),
    ("Which animal purrs when it is happy?", "a cat", ["a fish", "a snake", "a frog"]),
    ("What do you call the tall plant that gum leaves grow on?", "a gum tree", ["a rose bush", "a carrot", "a mushroom"]),
    ("Which of these helps flowers grow into fruit?", "bees", ["cars", "rocks", "clouds"]),
]
for q, correct, distractors in FACTS:
    add(q, correct, distractors)

# ---- extra colour-mixing / counting fillers to guarantee 1000 ------------
MIX = {
    "red and yellow": "orange", "blue and yellow": "green",
    "red and white": "pink", "red and blue": "purple",
    "black and white": "grey", "yellow and green": "lime green",
}
for mix, col in MIX.items():
    add(f"What colour do you get when you mix {mix}?", col,
        COLOUR_POOL + ["lime green"])

# ---- more colours of natural things --------------------------------------
MORE_COLOURS = {
    "a fresh green apple": "green", "a bunch of bananas": "yellow",
    "a stop sign": "red", "a tree's leaves in summer": "green",
    "an orange carrot top's carrot": "orange", "a cloudy sky": "grey",
    "a chocolate biscuit": "brown", "a dandelion flower": "yellow",
    "a blue whale": "blue", "a black cat": "black", "a white swan": "white",
    "a red rose": "red", "a green frog": "green", "a pink pig": "pink",
    "a brown bear": "brown", "a grey elephant": "grey", "a yellow chick": "yellow",
    "a red ladybird": "red", "a green cucumber": "green", "a purple grape": "purple",
    "an orange goldfish": "orange", "a white polar bear": "white",
    "a green lettuce": "green", "a red cherry": "red", "a yellow banana": "yellow",
    "a brown coconut": "brown", "a green pea": "green", "a red apple's skin": "red",
    "the green leaves of a gum tree": "green", "a golden beach": "yellow",
    "a blue ocean": "blue", "a white cloud": "white", "a red fire truck": "red",
    "green grass in a paddock": "green", "a brown tree branch": "brown",
    "a yellow sunflower": "yellow", "a red tomato": "red",
    "a purple eggplant": "purple", "an orange pumpkin": "orange",
}
for obj, col in MORE_COLOURS.items():
    add(f"What colour is {obj}?", col, COLOUR_POOL)

# ---- "which is bigger" comparisons (each pair is a unique question) -------
SIZE_ORDER = [
    "an ant", "a bee", "a ladybird", "a mouse", "a frog", "a fish",
    "a rabbit", "a cat", "a duck", "a chicken", "a dog", "a koala",
    "a fox", "a kangaroo", "a sheep", "a pig", "a dolphin", "a horse",
    "a cow", "a camel", "a shark", "a lion", "a tiger", "a bear",
    "a hippo", "a giraffe", "an elephant", "a whale",
]
for i in range(len(SIZE_ORDER)):
    for j in range(i + 4, len(SIZE_ORDER)):
        small, big = SIZE_ORDER[i], SIZE_ORDER[j]
        add(f"Which is bigger, {small} or {big}?", big,
            [small, "they are the same size", "you cannot tell"])

# ---- "which is faster" comparisons ---------------------------------------
SPEED_ORDER = [
    "a snail", "a worm", "a turtle", "a koala", "a sheep", "a pig",
    "a cow", "a dog", "a cat", "a rabbit", "a horse", "a kangaroo",
    "a dolphin", "a cheetah", "an eagle",
]
for i in range(len(SPEED_ORDER)):
    for j in range(i + 4, len(SPEED_ORDER)):
        slow, fast = SPEED_ORDER[i], SPEED_ORDER[j]
        add(f"Which is faster, {slow} or {fast}?", fast,
            [slow, "they are the same speed", "you cannot tell"])

# ---- a few more easy nature facts ----------------------------------------
MORE_FACTS = [
    ("Which of these is a baby chicken?", "a chick", ["a lamb", "a calf", "a joey"]),
    ("Which of these is a baby duck?", "a duckling", ["a puppy", "a foal", "a kid"]),
    ("Which of these is a baby pig?", "a piglet", ["a chick", "a calf", "a fawn"]),
    ("Which of these is a baby goat?", "a kid", ["a joey", "a puppy", "a calf"]),
    ("Which of these is a baby deer?", "a fawn", ["a lamb", "a chick", "a piglet"]),
    ("Which animal has a trunk?", "an elephant", ["a horse", "a sheep", "a duck"]),
    ("Which animal has a long tail and swings in trees?", "a monkey", ["a cow", "a pig", "a duck"]),
    ("Which animal has black and white stripes?", "a zebra", ["a lion", "a bear", "a frog"]),
    ("Which animal has a very long neck to reach tall leaves?", "a giraffe", ["a mouse", "a duck", "a cat"]),
    ("Which animal can squirt water from its blowhole?", "a whale", ["a dog", "a cat", "a hen"]),
    ("Which animal hops and has webbed feet?", "a frog", ["a horse", "a lion", "a cow"]),
    ("Which animal has spikes to keep it safe?", "an echidna", ["a rabbit", "a duck", "a swan"]),
    ("Which animal wags its tail when happy?", "a dog", ["a fish", "a snake", "a spider"]),
    ("Which animal lays eggs and has feathers?", "a bird", ["a dog", "a cow", "a cat"]),
    ("Which of these can swim in the sea?", "a fish", ["a chicken", "a cow", "a horse"]),
    ("Which of these is a flying insect?", "a butterfly", ["a snail", "a worm", "a crab"]),
    ("Which of these is very cold?", "ice", ["fire", "the sun", "hot soup"]),
    ("Which of these is very hot?", "fire", ["ice", "snow", "a cold drink"]),
    ("Where do apples grow?", "on trees", ["under the ground", "in the sea", "in the sky"]),
    ("Where do potatoes grow?", "under the ground", ["on trees", "in the sky", "in the sea"]),
    ("What do we call frozen water we skate on?", "ice", ["steam", "sand", "mud"]),
    ("What do plants make when the sun shines on their leaves?", "food", ["toys", "rocks", "cars"]),
    ("Which animal gives us wool?", "a sheep", ["a cow", "a hen", "a fish"]),
    ("Which animal gives us milk on a farm?", "a cow", ["a hen", "a fish", "a bee"]),
    ("Which animal gives us eggs on a farm?", "a hen", ["a cow", "a sheep", "a horse"]),
    ("What do bees live in?", "a hive", ["a nest", "a den", "a web"]),
    ("What do birds live in?", "a nest", ["a hive", "a shell", "a web"]),
    ("What do spiders make to catch flies?", "a web", ["a nest", "a hive", "a shell"]),
    ("Which season has the shortest, coldest days?", "winter", ["summer", "spring", "autumn"]),
    ("Which of these do we breathe in to stay alive?", "air", ["sand", "water", "mud"]),
    ("What do fish breathe with?", "gills", ["lungs", "noses", "ears"]),
    ("What do people breathe with?", "lungs", ["gills", "fins", "wings"]),
    ("Which is a wild animal, not a pet?", "a lion", ["a pet dog", "a pet cat", "a goldfish"]),
    ("Which is a pet you might keep at home?", "a dog", ["a lion", "a shark", "a whale"]),
    ("What do we call the star closest to Earth?", "the sun", ["the moon", "a cloud", "Mars"]),
    ("What do turtles carry on their backs?", "a shell", ["a nest", "a web", "a hive"]),
    ("What do we call a group of fish swimming together?", "a school", ["a herd", "a flock", "a pack"]),
    ("Which of these makes light at night in the sky?", "the moon and stars", ["the sun", "a rock", "the grass"]),
    ("Which of these can you hear?", "thunder", ["a colour", "a shadow", "a smell"]),
    ("Which of these can you smell?", "a flower", ["a sound", "a shadow", "the wind's colour"]),
]
for q, correct, distractors in MORE_FACTS:
    add(q, correct, distractors)

# ---- assemble output ------------------------------------------------------
if len(questions) < 1000:
    raise SystemExit(
        f"Only produced {len(questions)} unique questions - add more facts.")

random.shuffle(questions)
final = questions[:1000]

output = {
    "topic": "Science and Nature",
    "audience": "7-year-old kids in Australia",
    "difficulty": "easy",
    "count": len(final),
    "questions": final,
}

with open("science-nature-quiz.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Total unique questions available: {len(questions)}")
print(f"Wrote {len(final)} questions to science-nature-quiz.json")
