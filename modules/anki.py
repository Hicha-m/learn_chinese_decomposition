"""
Anki flashcard system module.

This module handles all Anki-related functionality:
- Creating note objects
- Building decks
- Exporting to Anki format
- Managing flashcard content
"""

import genanki
import random
from tqdm import tqdm

from . import data
from .config import CHINESE_MODEL_ID
from .constants import ANKI_FILE

__all__ = [
    'get_chinese_model',
    'create_chinese_note',
    'note_anki_chinese',
    'notes_append',
    'save_note_anki',
    'remove_last_note_anki',
    'modify_learned_char_characteristics',
    'add_learned_char_characteristics',
    'print_learned_char_characteristics',
    'export_anki',
    'export_chars_learn_to_anki',
    # Note: export_to_anki is not used and excluded
]


def get_chinese_model():
    """
    Get or create the Chinese Anki model.
    
    Returns:
        genanki.Model configured for Chinese character learning
    """
    return genanki.Model(
        CHINESE_MODEL_ID,
        "Chinese (Basic)",
        fields=[
            {"name": "Hanzi"},
            {"name": "Color"},
            {"name": "Pinyin"},
            {"name": "English"},
            {"name": "Sound"},
            {"name": "Exemple"},
            {"name": "Keyword"},
            {"name": "Components"},
            {"name": "Actor"},
            {"name": "Scene"},
            {"name": "Scene_tone"},
            {"name": "Pinyin_initial"},
            {"name": "Pinyin_final"},
            {"name": "Tone"}
        ],
        templates=[
            # CARD 1: KEYWORD
            {
                "name": "KEYWORD",
                "qfmt": """
<div class=tags>{{Card}} {{#Tags}} -- {{/Tags}}{{Tags}}</div>
<div class=reading>{{Keyword}}</div>
""",
                "afmt": """
{{FrontSide}}
<hr id="answer">
<div class=chinese>{{Hanzi}}</div>
<div class=reading>Pinyin: {{Pinyin}}</div>
""",
            },
            # CARD 2: COMPONENTS
            {
                "name": "COMPONENTS",
                "qfmt": """
<div class=tags>{{Card}} {{#Tags}} -- {{/Tags}}{{Tags}}</div>
<div>{{Components}}</div>
""",
                "afmt": """
{{FrontSide}}
<hr id="answer">
<div class=chinese>{{Hanzi}}</div>
""",
            },
            # CARD 3: VISUAL
            {
                "name": "VISUAL",
                "qfmt": """
<div class=tags>{{Card}} {{#Tags}} -- {{/Tags}}{{Tags}}</div>
<div class=chinese>{{Hanzi}}</div>
<div class=chinese>{{Exemple}}</div>
""",
                "afmt": """
{{FrontSide}}
<hr id="answer">
<div class=chinese>{{Color}}</div>
<div>{{English}}</div>
<div class=reading>{{Keyword}}</div>
<div class=reading>{{Components}}</div>
""",
            },
            # CARD 4: MOVIE / PHONETIC
            {
                "name": "MOVIE",
                "qfmt": """
<div class=tags>{{Card}} {{#Tags}} -- {{/Tags}}{{Tags}}</div>

{{#Pinyin}}
<div class=chinese>{{Hanzi}}</div>
{{/Pinyin}}
""",
                "afmt": """
{{FrontSide}}
<hr id="answer">

<div class=reading>Actor: {{Actor}}</div>
<div class=reading>Scene: {{Scene}}</div>
<div class=reading>Tone: {{Scene_tone}}</div>

<div class=reading>Pinyin Initial: {{Pinyin_initial}}</div>
<div class=reading>Pinyin Final: {{Pinyin_final}}</div>
<div class=reading>Pinyin: {{Pinyin}}</div>

<div class="chinese-support-sound">{{Sound}}</div>
""",
            },
            # CARD 5: SOUND
            {
                "name": "SOUND",
                "qfmt": """
<div class=tags>{{Card}} {{#Tags}} -- {{/Tags}}{{Tags}}</div>
<div class="chinese-support-sound">{{Sound}}</div>
""",
                "afmt": """
{{FrontSide}}
<hr id="answer">
<div class=chinese>{{Color}}</div>
<div>{{English}}</div>
<div class=reading>{{Components}}</div>
<div class=reading>{{Keyword}}</div>
<div class=reading>Pinyin: {{Pinyin}}</div>
""",
            },
        ],
        css="""
.card {
    font-family: arial;
    font-size: 20px;
    line-height: 1.5;
    text-align: center;
    color: black;
    background-color: white;
}
.card { word-wrap: break-word; }

.win .chinese { font-family: "MS Mincho", "ＭＳ 明朝"; }
.linux .chinese { font-family: "Kochi Mincho", "東風明朝"; }
.mobile .chinese { font-family: "Hiragino Mincho ProN"; }

.chinese { font-size: 30px; }
.reading { font-size: 16px; }
.tags { color: gray; text-align: right; font-size: 10pt; }
.chinese-support-sound { display: none; }

.tone1 { color: red; }
.tone2 { color: orange; }
.tone3 { color: green; }
.tone4 { color: blue; }
.tone5 { color: gray; }
"""
    )


def create_chinese_note(
    model,
    hanzi,
    color="",
    pinyin="",
    english="",
    sound="",
    exemple="",
    keyword="",
    components="",
    actor="",
    scene="",
    scene_tone="",
    pinyin_initial="",
    pinyin_final="",
    tone="",
    tags=None,
):
    """
    Create a Chinese language Anki note.
    
    Args:
        model: Anki model to use
        hanzi: Character
        color: Color-coded character
        pinyin: Pinyin with tone
        english: English definition
        sound: Sound file reference
        exemple: Example sentence
        keyword: Mnemonic keyword
        components: Component radicals
        actor: Actor for pinyin initial
        scene: Scene for pinyin final
        scene_tone: Scene for tone
        pinyin_initial: Initial consonant
        pinyin_final: Final vowel sound
        tone: Tone number
        tags: List of tags
        
    Returns:
        genanki.Note object
    """
    return genanki.Note(
        model=model,
        fields=[
            hanzi or "",
            color or "",
            pinyin or "",
            english or "",
            sound or "",
            exemple or "",
            keyword or "",
            components or "",
            actor or "",
            scene or "",
            scene_tone or "",
            pinyin_initial or "",
            pinyin_final or "",
            tone or ""
        ],
        tags=tags or [],
    )


def notes_append(notes, note, easy_note):
    """
    Append a note to the notes collection.
    
    Args:
        notes: Existing notes collection
        note: Note to add
        easy_note: Whether it's an easy note
    """
    d = {"note": note, "easy_note": easy_note}
    notes.append(d)


def save_note_anki(note, easy_note=False):
    """
    Save a note to Anki notes file.
    
    Args:
        note: Note to save
        easy_note: Whether it's an easy note
    """
    notes = data.autoload_anki()
    notes_append(notes, note, easy_note)
    data.autosave_anki(notes)
    n = len(notes)
    print(n, note.fields, easy_note)


def note_anki_chinese(model, args, easy_note=False):
    """
    Create a Chinese Anki note and determine its difficulty level.
    
    Args:
        model: Anki model
        args: Note arguments list
        easy_note: Initial easy note flag
        
    Returns:
        tuple: (note, final_easy_note_flag)
    """
    hanzi, color, pinyin, english, sound, exemple, keyword, components, actor, scene, scene_tone, pinyin_initial, pinyin_final, tone, tags = args
    if exemple == "":
        note = create_chinese_note(model, hanzi, color, keyword=keyword)
        easy_note = True
    elif easy_note:
        note = create_chinese_note(model, hanzi, color, pinyin, exemple=exemple, keyword=keyword)
    else:
        note = create_chinese_note(model, *args)
    
    return note, easy_note


def remove_last_note_anki():
    """Remove the last added Anki note."""
    notes = data.autoload_anki()
    n = len(notes)
    if n > 0:
        print(n - 1, notes.pop()["note"].fields)
        data.autosave_anki(notes)


def modify_learned_char_characteristics(hanzi, key, value):
    """
    Modify learned character characteristics.
    
    Args:
        hanzi: Character to modify
        key: Characteristic key
        value: New value
    """
    learned_chars_characteristic = data.load_learned_chars_characteristic()
    if hanzi in learned_chars_characteristic:
        learned_chars_characteristic[hanzi][key] = value
        data.save_learned_chars_characteristic(learned_chars_characteristic)


def add_learned_char_characteristics(args, easy_note=False):
    """
    Add characteristics to a learned character.
    
    Args:
        args: Characteristics arguments list
        easy_note: Whether it's an easy note
    """
    d = data.load_learned_chars_characteristic()
    hanzi, color, pinyin, english, sound, exemple, keyword, components, actor, scene, scene_tone, pinyin_initial, pinyin_final, tone = args[:14]
    
    d[hanzi] = {}
    d[hanzi]["pinyin"] = pinyin
    d[hanzi]["english"] = english
    d[hanzi]["exemple"] = exemple
    d[hanzi]["keyword"] = keyword
    d[hanzi]["components"] = components
    d[hanzi]["pinyin_initial"] = pinyin_initial
    d[hanzi]["pinyin_final"] = pinyin_final
    d[hanzi]["tone"] = tone
    d[hanzi]["easy_note"] = easy_note
    data.save_learned_chars_characteristic(d)


def print_learned_char_characteristics():
    """Print all learned character characteristics."""
    d = data.load_learned_chars_characteristic()
    for hanzi in d.keys():
        print(hanzi)
        print(d[hanzi])


def export_anki():
    """
    Export current learning data to Anki deck.
    
    Returns:
        Success status
    """
    notes = data.autoload_anki()
    deck = genanki.Deck(
        random.randrange(1 << 30, 1 << 31),
        "Chinese"
    )

    pbar = tqdm(notes, desc="Export notes")
    for d in pbar:
        note = d["note"]
        easy_note = d["easy_note"]
        deck.add_note(note)
        add_learned_char_characteristics(note.fields, easy_note)
        pbar.set_postfix({
            "hanzi": note.fields[0]
        })
    notes.clear()
    data.autosave_anki(notes)

    genanki.Package(deck).write_to_file(
        ANKI_FILE
    )

    print("✅ Deck exporté avec succès")


def export_chars_learn_to_anki():
    """Export characters being learned to Anki."""
    deck = genanki.Deck(
        random.randrange(1 << 30, 1 << 31),
        "Chinese"
    )
    d = data.load_learned_chars_characteristic()
    learned_chars = d.keys()
    pbar = tqdm(learned_chars, desc="Format notes")

    model = get_chinese_model()
    pinyin_rules = data.load_pinyin_rules()

    for learned_char in pbar:
        hanzi = learned_char
        color = learned_char
        pinyin = d[learned_char]["pinyin"]
        english = d[learned_char]["english"]
        sound = ""
        exemple = d[learned_char]["exemple"]
        keyword = d[learned_char]["keyword"]
        components = d[learned_char]["components"]
        pinyin_initial = d[learned_char]["pinyin_initial"]
        pinyin_final = d[learned_char]["pinyin_final"]
        tone = d[learned_char]["tone"]
        easy_note = d[learned_char]["easy_note"]
        
        if not easy_note:
            actor = pinyin_rules["initials"].get(pinyin_initial, "")
            scene = pinyin_rules["finals"].get(pinyin_final, "")
            scene_tone = pinyin_rules["tones"].get(tone, "")
        else:
            actor = ""
            scene = ""
            scene_tone = ""

        tags = []
        args = [hanzi, color, pinyin, english, sound, exemple, keyword, components,
                actor, scene, scene_tone, pinyin_initial, pinyin_final, tone, tags]
        note, _ = note_anki_chinese(model, args, easy_note)

        deck.add_note(note)

        pbar.set_postfix({
            "hanzi": hanzi
        })

    genanki.Package(deck).write_to_file(
        ANKI_FILE
    )
    print("✅ Deck exporté avec succès")
