#!/usr/bin/env python3
"""Generate audited Suno-ready lyric/style sheets for H001-H045."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from generate_suno_ready_high_lessons import (
    COMMON_SUFFIX,
    PROFILES,
    lyrics_block,
    normalize_sentences,
    topic_from_title,
    word_count,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "taco_course_mockup" / "high_lessons.json"
OUTPUT = HERE / "suno_ready" / "H001-H045"
MASTER = HERE / "SUNO投入用_再生成_H001-H045.md"
INDEX = HERE / "SUNO再生成レッスン一覧_H001-H045.md"
CORRECTION_REPORT = HERE / "高校生編_H001-H045_本文校正一覧.md"
CORRECTED_SOURCE = OUTPUT / "corrected_english_H001-H045.json"
SELECTION_LOG = HERE / "suno_ready" / "generated" / "H001-H045_song_selection_log.json"


PROFILE_BY_LESSON = {
    1: "nature", 2: "nature", 3: "daily", 4: "human", 5: "human",
    6: "nature", 7: "daily", 8: "daily", 9: "daily", 10: "daily",
    11: "human", 12: "arts", 13: "daily", 14: "philosophy", 15: "human",
    16: "human", 17: "history", 18: "action", 19: "human", 20: "daily",
    21: "human", 22: "human", 23: "philosophy", 24: "human", 25: "arts",
    26: "philosophy", 27: "human", 28: "science", 29: "nature", 30: "science",
    31: "science", 32: "history", 33: "philosophy", 34: "arts", 35: "nature",
    36: "philosophy", 37: "arts", 38: "adventure", 39: "science", 40: "science",
    41: "tech", 42: "culture", 43: "nature", 44: "history", 45: "history",
}


STYLE_MODIFIERS = {
    1: " Begin with cool dawn air and open gradually into warm sunlight over the lake.",
    2: " Use light woodwinds and a gentle spring lift; keep the mood fresh rather than sentimental.",
    3: " Add a quiet library pulse and intimate close-miked vocal phrasing.",
    4: " Center the arrangement on felt piano and the emotional weight of a small family keepsake.",
    5: " Keep the puppy scene warm and affectionate without becoming childish or comic.",
    6: " Use soft porch ambience, breeze-like strings, and spacious pauses between observations.",
    7: " Let the rhythm feel like a weekday commute: steady, modest, and quietly purposeful.",
    8: " Use conversational phrasing that clearly distinguishes planned intentions from decisions made at the table.",
    9: " Keep conditional clauses rhythmically clear and leave tiny breaths at commas.",
    10: " Add a subtle clock-like pulse without making the song mechanical.",
    11: " Make the sister's advice intimate and calm, with no melodramatic climax.",
    12: " Let the piano accompaniment mirror steady daily practice and a modest recital breakthrough.",
    13: " Add light station ambience and a gentle forward pulse, never turning the missed train into comedy.",
    14: " Use spacious forward-looking harmony and a quiet sense of possibility.",
    15: " Add restrained winter bells and room for reflection, avoiding festive excess.",
    16: " Keep the missed gift small and human; emphasize honesty and forgiveness rather than tragedy.",
    17: " Suggest old architecture through strings and piano, then brighten subtly as the house is restored.",
    18: " Maintain a clear running pulse while preserving intelligible English and a supportive family tone.",
    19: " Use close felt piano and soft page-turn textures; preserve privacy and restraint.",
    20: " Create an unhurried evening walk with warm street-light color and gentle momentum.",
    21: " Build around farewell, distance, and hope; no airport sound effects or oversized climax.",
    22: " Use warm chamber instrumentation and the quiet intimacy of a teacher's study.",
    23: " Leave reflective pauses after repeated what-clauses so the grammar remains audible.",
    24: " Add distant sea and lighthouse atmosphere with a patient, steady pulse.",
    25: " Let violin and piano suggest a small community concert without becoming virtuoso show music.",
    26: " Keep the verses weightless and imaginative, then return gently to the grounded final lines.",
    27: " Use an intimate letter-song atmosphere, restrained regret, and no sweeping tragedy.",
    28: " Add quiet laboratory curiosity and a gradual sense of discovery; avoid triumphalist medical claims.",
    29: " Use sparse high-mountain textures, patient tempo, and a sense of ancient endurance.",
    30: " Begin with controlled mission tension and expand only at the first-flight-over-the-Moon image.",
    31: " Use precise glassy textures, piano, and restrained strings to suggest laboratory persistence.",
    32: " Keep the protest solemn and courageous, with no marching-band triumph or crowd chants.",
    33: " Let the music alternate between mathematical clarity and a wide, humble oceanic space.",
    34: " Add elegant architectural rhythm and organic curves without imitating Spanish tourist music.",
    35: " Use natural woodwinds and an exploratory pulse, with clear pronunciation of Galapagos and species names.",
    36: " Shape the vocal like questions and answers, leaving short silences after the central questions.",
    37: " Make piano and strings emotionally strong but never suggest that suffering was required for artistic greatness.",
    38: " Build a light mechanical pulse into an expansive sense of first flight; no cartoon airplane effects.",
    39: " Move from telescope-like intimacy to a vast but quiet interstellar soundscape.",
    40: " Use cool laboratory textures and restrained tension, honoring Franklin without turning history into a villain song.",
    41: " Add a precise code-breaking pulse and a sober final section about persecution; no war sound effects.",
    42: " Suggest caravan movement with restrained hand percussion and strings, avoiding cultural caricature.",
    43: " Begin with fragile spring ambience, then add quiet urgency without disaster-movie drama.",
    44: " Use measured walking rhythm and moral resolve, with no militaristic percussion or victory anthem.",
    45: " Use deep spacious percussion and low strings to convey scale and time, not mystery-movie sensationalism.",
}


# Literal replacements are applied after extraction-only normalization.  Every
# source phrase must match exactly once so source drift cannot pass silently.
REPLACEMENTS: dict[int, list[tuple[str, str]]] = {
    1: [
        ("The water lay calm", "The water lay still"),
        ("A slight stream flowed", "A narrow stream flowed"),
        ("From the depth of the forest", "From the depths of the forest"),
    ],
    2: [
        ("Her eyes were remarkable", "Her eyes shone brightly"),
        ("Everything was quietly, and surely, becoming new", "Everything was quietly but surely becoming new"),
    ],
    3: [
        ("The afternoon library held a quiet atmosphere", "The library had a quiet atmosphere that afternoon"),
        ("the desire of his young days", "the desires of his youth"),
        ("strongly attracted my heart and appealed to me", "strongly appealed to me and held my attention"),
        ("The mind that composed these sentences", "The mind that had composed these sentences"),
        ("with a curious feeling", "with curiosity"),
        ("preferred this one book to anything else", "preferred this one book to everything else"),
    ],
    4: [
        ("presented me a small box", "gave me a small box"),
        ("had protected them", "had kept them safe"),
        ("I felt the ordinary box as something precious", "I came to see the ordinary box as something precious"),
        ("taught me the bond and the affection of family", "taught me about the bonds and affection within a family"),
        ("the small occasion carried the respect and honor of long years", "the small gift carried years of respect and memory"),
        ("A gentle wish to give something back", "A gentle desire to give something back"),
    ],
    5: [
        ("Mother considered her a gentle creature", "Mother found her gentle"),
        ("I trusted her as a good companion", "I considered her a good companion"),
        ("the family had made her a content and calm dog", "our care had made her a calm and contented dog"),
        ("Sora became the curious affection of our home", "Sora became the curious, affectionate heart of our home"),
    ],
    6: [
        ("always permits me to read", "always lets me read"),
        ("I could notice petals drift", "I could see petals drift"),
        ("Grandmother often recalls that memory", "Grandmother often recalled that memory"),
        ("I felt she wanted", "I sensed that she wanted"),
    ],
    7: [
        ("attend a small company in the local industry", "work for a small local company"),
        ("Each person carries out his duty", "Each person carries out their duties"),
        ("Inside these quiet days, a small faith lives, and I believe it", "Within these quiet days, a small sense of purpose lives, and I believe in it"),
    ],
    8: [
        ("was finishing her preparation for the meal", "was finishing the meal preparations"),
        ("made up his intend", "made up his mind"),
        ("discuss the travel plan", "discuss the trip"),
        ("Several small decision fell", "Several small decisions fell"),
        ("Sister would approach him with a small nod and confirm the plan", "Sister gave him a small nod and confirmed the plan"),
    ],
    9: [
        ("If the weather was good, we would spend", "If the weather is good, we will spend"),
        (
            "We discussed several conditions and made them into a certain plan",
            "We thought about several conditions and made a clear plan",
        ),
        ("unless the sky is totally black", "unless the forecast turns much worse"),
        (
            "Although mother was tired, she said she would prepare sandwiches",
            "Mother was tired, but she said she would prepare sandwiches",
        ),
        (
            "As the day approached, my sister's face remained calm",
            "As Sunday approaches, my sister's face remains calm",
        ),
        ("gathered our family together in a quiet way", "brought our family quietly together"),
    ],
    10: [
        ("The appointment is something I have waited for a long time", "I have waited a long time for this appointment"),
        ("For more than a month I have made steady progress", "For more than a month, I have been making steady progress"),
        ("I will probably proceed from lunch to the afternoon meeting", "After lunch, I will probably move on to the afternoon meeting"),
        ("where I suppose I will be", "where I will be"),
        ("I too will be attending many more days", "I too will be living through many more days"),
        ("Placing myself in a schedule is a small force that carries the day", "Placing myself within a schedule gives the day a gentle momentum"),
        ("another tomorrow is meanwhile waiting quietly", "another tomorrow is already waiting quietly"),
    ],
    11: [
        ("acknowledge something deeply true", "recognize something deeply true"),
        ("your own emotion", "your own emotions"),
        ("she expresses patience", "she shows patience"),
        ("realize themselves", "understand themselves"),
        ("the calm mature nature", "the calm and mature nature"),
        ("Her distant but steady words", "Her quiet but steady words"),
    ],
    12: [
        ("My effort has slowly been showing progress", "My daily effort has slowly been paying off"),
        ("My pursuit of a single piece of music has been long", "I have been working on a single piece of music for a long time"),
        ("Every day, I have continued constant practice", "Every day, I have continued to practice"),
        ("In my previous days", "In the past"),
        ("I have felt devoted to the work of making sound", "I have become devoted to shaping every sound"),
        ("Practice has gradually been improving, and my ability has been developing", "My playing has gradually been improving, and my ability has been developing"),
        ("I have seen a slow recent growth in myself", "I have noticed slow but steady growth in myself"),
        ("Today, I accomplish something big", "Today, I accomplished something important"),
        ("in a consistent manner", "without stopping"),
        ("That was the small achievement that the long continuing time had been quietly leaving for me", "That small achievement was the quiet result of all the time I had spent practicing"),
    ],
    13: [
        ("had been under repair since previously", "had been under repair for some time"),
        ("had approached the train", "had boarded the train"),
        ("recognize his face", "spot his face"),
        ("I realize now that he has always held this gentle kindness", "I realize now that he has always shown this gentle kindness"),
        ("I remained there, waiting", "I sat waiting"),
    ],
    14: [
        ("contribute quietly to this life", "contribute quietly to the lives of others"),
        ("found a little of my pursuit", "found a clearer sense of purpose"),
        ("many small achievement", "many small achievements"),
        ("My courage will have been growing in small forms", "My courage will have grown through small choices"),
        ("My beyond will likely be opening quietly there", "My future will likely be opening quietly before me"),
    ],
    15: [
        ("stopped by a small shrine", "stopped by a small temple"),
        ("I had visited here", "I had visited it"),
        ("would always consider me quietly in return", "would always respond with quiet patience"),
        ("I joined my hands", "I pressed my hands together"),
        ("short tempered", "short-tempered"),
    ],
    16: [
        ("another customer happened to purchase them", "another customer had bought them"),
        ("Inside that small emotion, her mature nature appeared", "In that small moment, her maturity became clear"),
        ("yet be saved by each other's affection", "yet be saved by another person's affection"),
    ],
    17: [
        ("recognized as something historical", "recognized as historically significant"),
        ("a budget was established by the city", "a restoration budget was allocated by the city"),
        ("the past has been carved", "traces of the past were carved"),
        ("An old building was made to contribute new survival by the hands of its people", "Through the efforts of local people, the old building was given a new life"),
    ],
    18: [
        ("has been continuing her practice for the marathon", "has been training for the marathon"),
        ("Her ability could not catch up with her goal", "Her body could not yet keep up with her goal"),
        ("made effort after effort", "kept making a steady effort"),
        ("has enough sufficient power", "has enough strength"),
        ("the bank of the river", "the riverbank"),
        ("no longer be only an athlete but a mature person who has given her own pursuit a real shape", "be not only a runner but also someone who has turned steady effort into real confidence"),
    ],
    19: [
        ("I discover an old diary", "I discovered an old diary"),
        ("hesitated opening it", "hesitated to open it"),
        ("began remembering each line with my eyes", "began reading each line"),
        ("a feeling of enjoying life", "a joy in life"),
        ("I quietly closed the drawer", "I quietly returned the diary and closed the drawer"),
        ("Reading would mean revealing the inside of my father's heart", "Reading it would mean entering the private world of my father's heart"),
        ("Preserving my father's past filled me with a small respect", "Glimpsing my father's past filled me with a new respect for him"),
    ],
    20: [
        ("I walked gently", "I walked on"),
        ("Leaving the butcher district", "Leaving the butcher's shop behind"),
        ("the small delight of daily life embraced me quietly", "I felt the small delights of daily life quietly embrace me"),
    ],
    21: [
        ("my friend was waiting, going abroad for a new position", "my friend was waiting to leave for a new job abroad"),
        ("Bowing in my heart, I saw him off", "Wishing him well in my heart, I saw him off"),
        ("having spent many years with me", "having shared many years with me"),
        ("keep in contact", "keep in touch"),
        ("leaving for his new pursuit", "leaving to follow a new path"),
        ("We would keep in touch, we had promised", "We had promised to keep in touch"),
        ("The future that was carrying my friend", "The future awaiting my friend"),
    ],
    22: [
        ("in my university years", "during my university years"),
        ("looked much more mature", "looked much older"),
        ("some manuscript", "some manuscripts"),
    ],
    23: [
        ("What matters seems to be only the essential", "What matters most seems to be the essentials"),
        ("What I must not lose is these small things", "What I must not lose are these small things"),
        ("the center of your own value", "the center of your own values"),
        ("I wanted to reveal, once more, what would fulfill me", "I wanted to rediscover what would fulfill me"),
    ],
    24: [
        ("enter the harbor safe", "enter the harbor safely"),
        ("a long correspond that needed no words", "a long bond that needed no words"),
        ("How many sailors his light had saved on stormy nights, I could never imagine", "I could never imagine how many sailors his light had guided on stormy nights"),
    ],
    25: [
        ("however small the note, it reached every heart", "however softly she played, every note reached the listeners"),
        ("people exchanged smile after smile", "people exchanged smile after smile with one another"),
        ("the small heritage that I want to treasure", "a small community tradition that I want to treasure"),
    ],
    26: [
        ("feel the distance of far cities", "feel constrained by the distance to faraway cities"),
        ("travel wherever the wind blew", "travel wherever the wind carried me"),
        ("stand on the earth", "stand on the Earth"),
    ],
    27: [
        ("I had only to tell her a single thank you.", "All I had to do was write a single word of thanks."),
        ("I had hidden my words away", "I hid my words away"),
        ("life can change upon the courage of a single letter", "a life can turn on the courage it takes to send a single letter"),
    ],
    28: [
        ("was the child of an accident", "began with an accident"),
        ("many infection", "many infections"),
        ("lost from wound", "lost because of wounds"),
        ("Modern medicine was born from that one dish", "That one dish helped open the age of antibiotics"),
        ("The quiet care of a single scientist saved millions of lives", "Fleming's careful observation, followed by the work of many other scientists, eventually helped save millions of lives"),
        ("If only that chance had not arrived", "If that chance observation had never been made"),
        ("If Fleming had missed that small observation, what the world would have lost!", "How much the world would have lost if Fleming had missed that small observation!"),
    ],
    29: [
        ("has been surviving", "has survived"),
        ("on the earth", "on Earth"),
        ("what has grown the long life", "what has enabled the long life"),
        ("from the rings within the bark", "from growth rings within the wood"),
        ("four thousand eight hundred fifty five years old", "more than four thousand eight hundred years old"),
        ("older than our history", "older than many civilizations"),
        ("among the most remarkable beings", "among the most remarkable living beings"),
    ],
    30: [
        ("The mission of Apollo 11 was launched", "The Apollo 11 mission began"),
        ("countless engineer", "countless engineers"),
        ("beyond the earth", "beyond Earth"),
        ("set his foot upon the moon", "set foot on the Moon"),
        ("The moonlight shone upon the crew who had returned safely to the earth", "After returning safely to Earth, the crew carried the memory of that distant world home"),
    ],
    31: [
        ("one of the most famous physicist", "one of the most famous physicists"),
        ("was extreme", "was extraordinary"),
        ("Together with her husband Pierre, they gave most of their lives to research", "Together with her husband Pierre, she devoted much of her life to research"),
        ("to draw out the new element radium", "to isolate and study the new element radium"),
        ("Experiment in the laboratory was", "The work in the laboratory involved"),
        ("Her honor of two Nobel prizes could not have come", "Her achievement of winning two Nobel Prizes could not have come"),
        ("showed the path to every generation", "opened a path for later generations"),
    ],
    32: [
        ("a black woman", "a Black woman"),
        ("moved the history of America", "changed the course of American history"),
        ("black people", "Black people"),
        ("the black citizens", "the Black citizens"),
        ("A year later, the Supreme Court would declare that racial separation on the buses was unconstitutional", "The following year, a federal court ruled bus segregation unconstitutional, and the U.S. Supreme Court upheld that decision"),
        ("changed the whole of society", "helped change society"),
    ],
    33: [
        ("spoke of himself in this way: I hardly know anything about what the world is", "described himself as someone who still knew very little compared with the vast unknown"),
        ("the discovery of calculus", "the development of calculus"),
        ("Before Newton, no one could calculate the orbit of a planet with accuracy", "Before Newton, no single theory explained both falling objects and planetary orbits"),
        ("I am like a child on the seashore, picking up a pebble or two", "He compared himself to a child on the seashore, finding only a few interesting stones"),
        ("Before me, the vast ocean of truth lies almost untouched", "Before him, he said, the vast ocean of truth remained largely unexplored"),
    ],
    34: [
        ("Antoni Gaudi", "Antoni Gaudí"),
        ("Gaudi found", "Gaudí found"),
        ("created a unique architecture", "created a unique architectural language"),
        ("found the inspiration for his design", "drew inspiration for his designs"),
        ("the cathedral called La Sagrada Familia", "the basilica known as the Sagrada Família"),
        ("its construction has been continuing", "its construction has continued, with interruptions"),
        ("He once said of his work, I studied beside nature.", "He described nature as his great teacher."),
        ("God's architecture is nature itself.", "For him, nature itself was a form of architecture."),
        ("Gaudi was hit by a tram on the street and died", "Gaudí was struck by a tram and died from his injuries several days later"),
        ("through the donation from around the world", "through donations and support from visitors around the world"),
        ("the fact of being unfinished speaks for itself of the building's historic value", "its unfinished state has itself become part of the building's history"),
    ],
    35: [
        (
            "Charles Darwin, in 1831, set out on a voyage around the world on board H.M.S. Beagle",
            "In 1831, Charles Darwin began a voyage around the world aboard a British survey ship",
        ),
        ("many island", "many islands"),
        ("On the Galapagos, he continued to observe", "On the Galapagos Islands, he carefully observed how animals varied from island to island"),
        ("He noticed that each island held a species of finch with a slightly different beak", "He collected birds that were later identified in England as related finch species with different beaks"),
        ("many specimen", "many specimens"),
    ],
    36: [
        ("Twenty four hundred", "Twenty-four hundred"),
        ("the dialog he held", "the dialogues he held"),
        ("His student Plato reported, The teacher said, 'An unexamined life is not worth living.", "In Plato's account, Socrates said that an unexamined life was not worth living."),
        ("' Socrates kept asking people, What is virtue?", "Socrates kept asking people what virtue was."),
        ("What is justice?", "He asked what justice was."),
        ("he replied, To be ethical is also to die correctly.", "he replied that escaping would betray the laws under which he had lived."),
        ("But his question, over two thousand years, is still turned toward us now: Do you examine your own life?", "But after more than two thousand years, his question still challenges us: do we examine our own lives?"),
    ],
    37: [
        ("his final symphony, the Ninth", "his final completed symphony, the Ninth"),
        ("One of the singer", "One of the soloists"),
        ("Deafness drove him toward despair, yet that very despair changed his music into something deeper", "Deafness drove him toward despair, yet he continued to compose music of extraordinary depth"),
        ("Silence opened him toward humanity", "Through silence, he continued to reach toward humanity"),
        ("The Ninth is the crystal form of suffering that Beethoven had overcome", "The Ninth is a testament to the creativity Beethoven sustained through profound suffering"),
    ],
    38: [
        ("a twelve second flight", "a twelve-second flight"),
        ("kept holding a dream", "kept pursuing a dream"),
        ("never denied their dream", "never abandoned their dream"),
        ("performed its brief flight", "made its brief flight"),
        ("only forty meters", "about thirty-seven meters"),
        ("the triumph of a long battle against gravity, which humanity itself had finally overcome", "the result of a long effort to achieve controlled, powered flight"),
        ("The moment his brother landed, Wilbur quietly took his hand", "When Orville landed, the brothers knew that years of work had finally taken flight"),
    ],
    39: [
        ("These observation", "These observations"),
        ("the earth stood", "the Earth stood"),
        ("launched two probe", "launched two probes"),
        ("Voyager carries a golden disc", "Each Voyager probe carries a Golden Record"),
        ("The sounds of the earth", "The sounds of Earth"),
        ("beyond the millennium", "across the centuries"),
    ],
    40: [
        ("she was taking image of DNA by using the technique of X-ray crystallography", "she was producing images of DNA using X-ray diffraction"),
        ("clearly showed the double helix", "revealed an X-shaped pattern that provided crucial evidence for a helical structure"),
        ("her observation was shown to Watson and Crick without her permission", "her photograph was shown to Watson without her knowledge"),
        ("The Nobel Prize cannot be awarded after death, by its rule", "Under Nobel rules, the prize is not normally awarded posthumously"),
        ("was forgotten for a long time", "was underestimated for a long time"),
    ],
    41: [
        ("the German code Enigma", "the German Enigma cipher"),
        ("the British navy would be sunk one ship after another", "Allied ships could be sunk one after another"),
        ("By its logic, Enigma combinations were cracked one by one", "The machine rapidly eliminated impossible Enigma settings, helping the team read many messages"),
        ("Turing reasoned over the question", "Turing explored the question"),
        ("His theory became the foundation of today's artificial intelligence", "His work became foundational to computer science and later debates about artificial intelligence"),
        ("his private life was treated as illegal", "homosexuality was criminalized"),
        ("A man who had saved so many could not save himself", "The country he had helped defend later punished him for who he was"),
        ("Queen Elizabeth granted", "Queen Elizabeth II granted"),
    ],
    42: [
        ("many route", "many routes"),
        ("Indian spice", "Indian spices"),
        ("Merchant loaded", "Merchants loaded"),
        ("crossed the desert, crossed the mountains", "crossed deserts and mountains"),
        ("would later support the culture of Europe", "later contributed to learning and culture in Europe"),
        ("humanity's first great attempt at connection", "one of history's great networks of exchange"),
        ("over a thousand years", "across many centuries"),
        ("the roots of our civilization", "the roots of many civilizations"),
    ],
    43: [
        ("chemical pesticide was", "chemical pesticides were"),
        ("pesticide did not", "pesticides did not"),
        ("awakened a great awareness in the people", "awakened widespread public concern"),
        ("banned the use of DDT", "banned most uses of DDT"),
        ("became the starting point", "helped inspire the growth"),
        ("Spring may come, and yet no bird may sing.", "Carson warned that spring might come with no birds singing."),
    ],
    44: [
        ("three hundred eighty kilometers", "about three hundred eighty-five kilometers"),
        ("twenty four days", "twenty-four days"),
        ("had forbidden Indian people from making salt themselves, holding it as a British monopoly", "maintained a salt monopoly and prohibited Indians from producing or selling salt independently"),
        ("a thorough, nonviolent protest", "a disciplined, nonviolent protest"),
        ("eventually led to Indian independence", "contributed to the movement for Indian independence"),
        ("Martin Luther King, Nelson Mandela.", "Martin Luther King Jr. later drew deeply from Gandhi's philosophy of nonviolent resistance."),
        ("They, too, began to walk after listening to the footsteps of Gandhi", "Movements around the world adapted its lessons in their own struggles for justice"),
    ],
    45: [
        ("about two and a half million block", "about two point three million stone blocks"),
        ("The strongest theory today is that they carried heavy limestone and built it up using a ramp", "Leading explanations involve ramps and organized teams transporting heavy limestone blocks, though the exact methods remain debated"),
        ("The pyramid was a tomb of the pharaoh and his eternal home", "The pyramid was built as the pharaoh's tomb and part of a larger burial complex"),
        ("they designed it as a stairway for the king's soul to rise toward the sky", "its form and burial complex reflected their beliefs about kingship and the afterlife"),
        ("The ancient civilization vanished long ago", "The ancient kingdom ended long ago"),
        ("seems to speak something to us", "seems to speak to us"),
    ],
}


def normalized_h1_lines(lesson: int, raw: list[str]) -> list[str]:
    lines = normalize_sentences(raw)
    if lesson == 35:
        expected = ["M.", "S.", "Beagle."]
        if lines[1:4] != expected or not lines[0].endswith("H."):
            raise ValueError("H35 H.M.S. Beagle extraction pattern changed")
        lines = [lines[0] + "M.S. Beagle."] + lines[4:]
    return lines


def apply_replacements(lesson: int, lines: list[str]) -> tuple[list[str], list[dict[str, str]]]:
    corrected = list(lines)
    changes: list[dict[str, str]] = []
    for old, new in REPLACEMENTS.get(lesson, []):
        matches = [(i, line.count(old)) for i, line in enumerate(corrected) if old in line]
        total = sum(count for _, count in matches)
        if total != 1:
            raise ValueError(f"H{lesson}: replacement must match once: {old!r} (matched {total})")
        index = matches[0][0]
        before = corrected[index]
        corrected[index] = before.replace(old, new, 1)
        changes.append({"before": before, "after": corrected[index]})
    return corrected, changes


def style_prompt(number: int, profile: str) -> str:
    return f"{PROFILES[profile]['prompt']}{STYLE_MODIFIERS[number]} {COMMON_SUFFIX}"


def build_lesson(lesson: dict) -> tuple[str, dict]:
    number = lesson["src"]["lesson"]
    profile = PROFILE_BY_LESSON[number]
    topic = topic_from_title(lesson["title"])
    lines = normalized_h1_lines(number, lesson["enSentences"])
    lines, corrections = apply_replacements(number, lines)
    lyrics = lyrics_block(lines)
    words = sum(word_count(line) for line in lines)
    duration = words / 82.0
    prompt = style_prompt(number, profile)
    video = lesson.get("video")
    md = [
        f"# H{number:03d} {topic}",
        "",
        f"- レッスン：{lesson['title']}",
        f"- 文法ターゲット：{lesson['grammar']['target']}",
        f"- 既存動画ID：`{video}`" if video else "- 既存動画ID：未登録",
        "- 作業状態：歌詞・推奨スタイル再生成済み／Suno楽曲は未生成",
        f"- 音楽系統：{PROFILES[profile]['ja']}",
        f"- 本文校正：{len(corrections)}件（校正一覧に修正前・修正後を記録）",
        f"- 歌詞語数：{words}語（目安 {int(duration)}分{int((duration-int(duration))*60):02d}秒〜）",
        "",
        "## Suno Title",
        "",
        "```text",
        f"H{number:03d} — {topic}",
        "```",
        "",
        "## Styles",
        "",
        "```text",
        prompt,
        "```",
        "",
        "## Lyrics",
        "",
        "```text",
        lyrics,
        "```",
        "",
        "## 生成・採用ルール",
        "",
        "- Customモードで使用し、本文の各行を1回ずつ歌わせる。",
        "- Sunoが2候補を返した場合も、歌詞一致・脱落・発音・タイミングを比較して1曲だけ採用する。",
        "- 採用曲だけを `../generated/H001-H045_song_selection_log.json` に記録する。",
        "- 誤った語を歌った候補は不採用。3回生成しても同じ誤りが改善しない場合は打ち切りを記録する。",
        "",
    ]
    manifest = {
        "lesson": number,
        "book": lesson["src"]["book"],
        "title": lesson["title"],
        "topic": topic,
        "grammar_target": lesson["grammar"]["target"],
        "existing_video": video,
        "status": "lyrics_ready_song_not_generated",
        "profile": profile,
        "profile_ja": PROFILES[profile]["ja"],
        "style_prompt": prompt,
        "english_lines": lines,
        "lyrics": lyrics,
        "word_count": words,
        "correction_count": len(corrections),
        "corrections": corrections,
        "file": f"H{number:03d}.md",
    }
    return "\n".join(md), manifest


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    lessons = [row for row in json.loads(source_bytes) if 1 <= row["src"]["lesson"] <= 45]
    if len(lessons) != 45:
        raise ValueError(f"expected 45 lessons, got {len(lessons)}")
    if set(PROFILE_BY_LESSON) != set(range(1, 46)):
        raise ValueError("style profile coverage mismatch")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifests: list[dict] = []
    full_sections: list[str] = []
    for lesson in lessons:
        md, manifest = build_lesson(lesson)
        (OUTPUT / manifest["file"]).write_text(md, encoding="utf-8")
        manifests.append(manifest)
        full_sections.append(md)

    source_sha = hashlib.sha256(source_bytes).hexdigest()
    correction_count = sum(item["correction_count"] for item in manifests)
    manifest_payload = {
        "generated_from": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_sha,
        "criteria": "lessons H001-H045",
        "count": len(manifests),
        "correction_count": correction_count,
        "song_selection_policy": "one adopted song per lesson",
        "lessons": manifests,
    }
    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    CORRECTED_SOURCE.write_text(
        json.dumps(
            [
                {
                    "lesson": item["lesson"],
                    "title": item["title"],
                    "grammar_target": item["grammar_target"],
                    "english_lines": item["english_lines"],
                }
                for item in manifests
            ],
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    report = [
        "# 高校生編 H001〜H045 本文校正一覧",
        "",
        "- 対象：高1 H1〜H45のSuno再生成用英文",
        f"- 校正：全{correction_count}件",
        "- 方針：意味と文法ターゲットを保ちながら、文法・語法・自然さ・事実関係・教材上の配慮を修正。",
        "- 元の `taco_course_mockup/high_lessons.json` と既存動画は変更せず、Suno投入用成果物だけに反映。",
        "",
    ]
    for item in manifests:
        if not item["corrections"]:
            continue
        report += [f"## H{item['lesson']:03d} {item['topic']}", ""]
        for change in item["corrections"]:
            report += [f"- 修正前：{change['before']}", f"  修正後：{change['after']}"]
        report.append("")
    CORRECTION_REPORT.write_text("\n".join(report), encoding="utf-8")

    readme = f"""# H001〜H045 Suno再生成用データ

- 個別ファイル：`H001.md`〜`H045.md`
- 機械可読データ：`manifest.json`
- 校正済み英文：`corrected_english_H001-H045.json`
- 本文校正：全{correction_count}件（`../../高校生編_H001-H045_本文校正一覧.md`）
- 元データSHA-256：`{source_sha}`

既存動画と元JSONは上書きしていない。Suno生成時は2候補が出ても教材として採用する曲を1曲に絞り、`../generated/H001-H045_song_selection_log.json` に共有URL・曲ID・長さ・選定理由・歌詞QAを記録する。
"""
    (OUTPUT / "README.md").write_text(readme, encoding="utf-8")

    index = [
        "# 高校生編 H1〜H45 Suno再生成一覧",
        "",
        f"全45曲。本文校正は全{correction_count}件。Suno楽曲はまだ生成していない。",
        "",
        "| Lesson | 主題 | 文法ターゲット | 推奨音楽系統 | 状態 |",
        "|---|---|---|---|---|",
    ]
    for item in manifests:
        link = f"suno_ready/H001-H045/{item['file']}"
        index.append(
            f"| [H{item['lesson']:03d}]({link}) | {item['topic']} | {item['grammar_target']} | {item['profile_ja']} | 歌詞準備済み・曲未生成 |"
        )
    INDEX.write_text("\n".join(index) + "\n", encoding="utf-8")

    master_header = """# 高校生編 H001〜H045 Suno投入用・歌詞再生成統合版

## 共通方針

- 校正済み英文本文を省略せず、各行を1回ずつ歌う通作形式。
- 自動反復サビ、誤った語、意味を変える脱落は不採用。
- 2候補が生成されても、教材として採用するのは1曲だけ。
- 3回生成しても同じ歌詞誤りが改善しない場合は打ち切りを記録する。
- 既存動画・元JSONは上書きしない。

---

"""
    MASTER.write_text(master_header + "\n---\n\n".join(full_sections), encoding="utf-8")

    SELECTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    selection_payload = {
        "range": "H001-H045",
        "policy": "If Suno returns two candidates, compare them and record only one adopted song per lesson.",
        "required_fields": [
            "lesson", "share_url", "song_id", "duration_seconds", "generation_attempt",
            "lyrics_match", "omissions", "pronunciation_notes", "timing_notes", "selection_reason",
        ],
        "songs": [],
    }
    SELECTION_LOG.write_text(
        json.dumps(selection_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"generated {len(manifests)} lesson files; corrections={correction_count}")


if __name__ == "__main__":
    main()
