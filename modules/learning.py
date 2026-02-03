"""
Learning system module.

This module handles the character learning workflow:
- Learning new characters
- Tracking progress
- Managing learned characters
- Updating learning states

Note: Jupyter-specific UI components (widgets, IPython.display) are excluded
as they are not necessary for the core learning functionality.
"""

import re
from . import config, tree, data

__all__ = [
    'learn_character',
    'mark_as_learned',
    'add_pinyin_rules',
    'get_first_exemple',
    'get_exemple',
    'print_bubbles',
    'characteristics_hanzi',
]


def learn_character(target, builder, learned_chars):
    """
    Initiate learning of a new character.
    
    Args:
        target: Target character to learn
        builder: HanziTreeBuilder instance
        learned_chars: Set of already learned characters
        
    Returns:
        Tuple of (char_to_learn, radicals_string) where char_to_learn is the next
        character ready to learn and radicals_string is a string of its components
    """
    res = tree.analyze_character_v3(target, builder, learned_chars)
    root = res["root"]

    print("CHARACTER:", res["character"])
    print("REQUIRED:", res["required_radicals"])
    print("KNOWN:", res["known_radicals"])

    print("\nDEPENDENCIES:")
    for k, v in res["dependencies"].items():
        print(f"{k} : {v}")

    print("\nTREE:")
    tree.compute_status(root, learned_chars)
    tree.print_tree_with_status(root)

    print("READY FOR learn:", res["ready"])

    char_to_learn = ""
    radicaux = []

    if res["ready"]:
        char_to_learn = res["ready"][0]
        radicaux = res["dependencies"].get(char_to_learn, [])
    radicaux = " + ".join(radicaux)

    return char_to_learn, radicaux


def mark_as_learned(char, learned_chars):
    """
    Mark a character as learned.
    
    Args:
        char: Character to mark as learned
        learned_chars: Set to update with learned character
    """
    learned_chars.add(char)
    data.save_learned_chars(learned_chars)


def add_pinyin_rules(pinyin_rules, actor, scene, initial, final):
    """
    Add mnemonic rules for pinyin.
    
    Args:
        pinyin_rules: Dictionary of pinyin rules
        actor: Actor in the mnemonic
        scene: Scene in the mnemonic
        initial: Pinyin initial
        final: Pinyin final
    """
    pinyin_rules["initials"][initial] = actor
    pinyin_rules['finals'][final] = scene
    data.save_pinyin_rules(pinyin_rules)


def get_first_exemple(text):
    """
    Get the first example sentence from text.
    
    Args:
        text: Text to extract example from
        
    Returns:
        First example sentence or empty string
    """
    pattern = re.compile(
        r"Sentence\s+#1[\s\S]*?\*\*Original sentence \(cleaned\):\*\*\s*([\u4e00-\u9fff，。！？；：「」、]+)"
    )

    match = pattern.search(text)

    if match:
        sentence = match.group(1)
        print(sentence)
        return sentence
    return ""


def get_exemple(char_to_learn, word_to_bubbles, bubbles, build_prompt_context_func, ai_func):
    """
    Get an example sentence for a character.
    
    Args:
        char_to_learn: Character to get example for
        word_to_bubbles: Mapping of words to bubbles
        bubbles: Bubble data
        build_prompt_context_func: Function to build AI prompt
        ai_func: AI function to call
        
    Returns:
        Example sentence string
    """
    sentence = ""
    input_text = print_bubbles(char_to_learn, word_to_bubbles, bubbles)
    if input_text:
        print("Begin")
        context_prompt = build_prompt_context_func(char_to_learn, input_text)
        text = ai_func(context_prompt)
        data.save_hanzi(char_to_learn, text, "context")
        sentence = get_first_exemple(text)
        print(sentence)
    else:
        print("No Input")
    return sentence


def print_bubbles(word, word_to_bulles, bulles):
    """
    Print bubble representations.
    
    Args:
        word: Word to display bubbles for
        word_to_bulles: Mapping of words to bubbles
        bulles: Bubble data
        
    Returns:
        Formatted string with bubble content
    """
    indice_bulles = list(word_to_bulles[word])
    indice_bulles.sort()
    input_text = ""

    for i in indice_bulles:
        for j in bulles[i]:
            input_text += j + "\n"
        input_text += "--- \n"
    return input_text


def characteristics_hanzi(char_to_learn, option, sentence, label, radicals, tonalite, pinyin_rules):
    """
    Extract characteristics of a hanzi based on tonality.
    
    Args:
        char_to_learn: Character being learned
        option: Dictionary with character info (pinyin, definition)
        sentence: Example sentence
        label: Visual/semantic label
        radicals: Component radicals string
        tonalite: Tone number override (or empty string)
        pinyin_rules: Pinyin rules dictionary
        
    Returns:
        List of character attributes for Anki card creation
    """
    from . import pinyin as pinyin_module
    
    hanzi = char_to_learn
    color = char_to_learn
    pinyin = option['pinyin'][0] if option['pinyin'] else ""
    english = option["definition"][0]["definition"] if option['definition'] else ""
    sound = ""
    exemple = sentence
    keyword = label
    components = radicals

    if pinyin:
        pinyin_initial, pinyin_final, tone = pinyin_module.split_pinyin(pinyin, pinyin_rules)
        if tonalite != "":
            tone = tonalite
        actor = pinyin_rules["initials"].get(pinyin_initial, "")
        scene = pinyin_rules["finals"].get(pinyin_final, "")
        scene_tone = pinyin_rules["tones"].get(tone, "")
    else:
        pinyin_initial = ""
        pinyin_final = ""
        tone = ""
        actor = ""
        scene = ""
        scene_tone = ""

    tags = []

    args = [hanzi, color, pinyin, english, sound, exemple, keyword, components,
            actor, scene, scene_tone, pinyin_initial, pinyin_final, tone, tags]
    return args
