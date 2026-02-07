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
    'select_pinyin',
    'build_dictionary_result',
    'collect_pinyin_mnemonics',
]


def learn_character(target, builder, learned_chars):
    """
    Initiate learning of a new character.
    
    Args:
        target: Target character to learn
        builder: HanziTreeBuilder instance
        learned_chars: Set of already learned characters
        
    Returns:
        Tuple of (char_to_learn, radicals_string, status) where status is one of
        'ok', 'complete', or 'blocked'
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
    status = "blocked"

    if res["ready"]:
        char_to_learn = res["ready"][0]
        radicaux = res["dependencies"].get(char_to_learn, [])
        status = "ok"
    elif not res["required_radicals"] and target in learned_chars:
        print("Congratulations! You have learned all the characters in this tree!")
        status = "complete"
    elif not res["required_radicals"] and target not in learned_chars:
        # No dependencies and not learned -> target is the next character.
        char_to_learn = target
        radicaux = res["dependencies"].get(char_to_learn, [])
        status = "ok"
    else:
        print("❌ Cannot determine next character to learn")
    radicaux = " + ".join(radicaux)

    return char_to_learn, radicaux, status


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
    # be careful it can create new keys.
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
    if char_to_learn in word_to_bubbles:
        input_text = print_bubbles(char_to_learn, word_to_bubbles, bubbles)
        context_prompt = build_prompt_context_func(char_to_learn, input_text)
        text = ai_func(context_prompt)
        data.save_hanzi(char_to_learn, text, "context")
        sentence = get_first_exemple(text)
        #print(sentence)
        print("✅ Example sentence extracted")
    else:
        print("⚠️ (No corpus entries found for this character)")
    return sentence


def print_bubbles(word, word_to_bubbles, bubbles):
    """
    Print bubble representations.
    
    Args:
        word: Word to display bubbles for
        word_to_bubbles: Mapping of words to bubbles
        bulles: Bubble data
        
    Returns:
        Formatted string with bubble content
    """
    indice_bubbles = list(word_to_bubbles[word])
    indice_bubbles.sort()
    input_text = ""

    for i in indice_bubbles:
        for j in bubbles[i]:
            input_text += j + "\n"
        input_text += "--- \n"
    return input_text


def characteristics_hanzi(char_to_learn, option, sentence, label, radicals, tonalite, pinyin_rules=None):
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
        rules = pinyin_rules or data.load_pinyin_rules()
        pinyin_initial, pinyin_final, tone = pinyin_module.split_pinyin(pinyin, rules)
        if tonalite != "":
            tone = tonalite
        actor = pinyin_module.get_pinyin_rules("initials", pinyin_initial)
        scene = pinyin_module.get_pinyin_rules("finals", pinyin_final)
        scene_tone = pinyin_module.get_pinyin_rules("tones", tone)
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


def select_pinyin(option):
    """
    Select a pinyin pronunciation from multiple options.
    
    If option contains multiple pinyin entries, prompts user to choose one.
    Updates the option dict in-place to contain only the selected pinyin.
    
    Args:
        option: Dictionary with 'pinyin' key containing list of pronunciations
        
    Returns:
        The selected pinyin string, or empty string if no pinyin available
    """
    selected_pinyin = ""
    print(option)
    if option.get('pinyin'): ## erreur car option none voir v1_app
        if len(option['pinyin']) > 1:
            print("   Multiple pronunciations found:")
            for i, p in enumerate(option['pinyin'], 1):
                print(f"     {i}. {p}")
            choice = input("Select pronunciation (number, default 1): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(option['pinyin']):
                selected_pinyin = option['pinyin'][int(choice) - 1]
            else:
                selected_pinyin = option['pinyin'][0]
        else:
            selected_pinyin = option['pinyin'][0]
        option['pinyin'] = [selected_pinyin]
    
    return selected_pinyin


def build_dictionary_result(char_to_learn, dictionary=None):
    """
    Build a normalized dictionary result for a character using HanziDictionary.
    
    Queries the dictionary for pinyin, definitions, and search results for the given character.
    Handles missing or empty data gracefully.
    
    Args:
        char_to_learn: Character to look up
        dictionary: Optional HanziDictionary instance. If None, uses get_dictionary() from tree module
        
    Returns:
        Dictionary with keys:
            - 'character': The character being looked up
            - 'pinyin': List of pinyin pronunciations (or empty list if none found)
            - 'definition': List of definition entries (or empty list if none found)
            - 'search': Search result data (or None if no search result)
    """
    
    # Use provided dictionary or get the singleton
    if dictionary is None:
        dictionary = tree.get_dictionary()
    
    result = {
        'character': char_to_learn,
        'pinyin': [],
        'definition': [],
        'search': None
    }
    
    try:
        # Get pinyin pronunciation(s)
        pinyin_result = dictionary.get_pinyin(char_to_learn)
        if pinyin_result:
            result['pinyin'] = pinyin_result if isinstance(pinyin_result, list) else [pinyin_result]
    except (AttributeError, Exception):
        print(f"⚠️  Could not retrieve pinyin for '{char_to_learn}'")
    
    try:
        # Get definition(s)
        definition_result = dictionary.definition_lookup(char_to_learn)
        if definition_result:
            result['definition'] = definition_result if isinstance(definition_result, list) else [definition_result]
    except (AttributeError, Exception):
        print(f"⚠️  Could not retrieve definition for '{char_to_learn}'")
    
    try:
        # Perform dictionary search
        search_result = dictionary.dictionary_search(char_to_learn)
        if search_result:
            result['search'] = search_result
            result['definition'] = search_result if isinstance(search_result, list) else [search_result]
            print(f"📖 Dictionary search result for '{char_to_learn}':")
            #print(search_result)
        else:
            print(f"ℹ️  No dictionary search results found for '{char_to_learn}'")
    except (AttributeError, Exception):
        print(f"⚠️  Dictionary search unavailable for '{char_to_learn}'")
    
    return result


def collect_pinyin_mnemonics(selected_pinyin, easy_note=False):
    """
    Collect pinyin mnemonic information from user input.
    
    Prompts for label, and if not easy_note and pinyin exists, prompts for
    actor and scene for missing pinyin components.
    
    Args:
        selected_pinyin: The pinyin pronunciation string
        easy_note: Whether this is an easy note (skips actor/scene prompts)
        
    Returns:
        Tuple of (label, actor, scene, tone_override, pinyin_rules)
        where tone_override is an empty string by default
    """
    from . import pinyin as pinyin_module
    
    label = ""
    while not label:
        label = input("Enter keyword/label: ").strip()
    tone_override = ""  # Default tone override
    actor = ""
    scene = ""
    
    if selected_pinyin and not easy_note:
        pinyin_rules = data.load_pinyin_rules()
        pinyin_initial, pinyin_final, _ = pinyin_module.split_pinyin(selected_pinyin, pinyin_rules)
        
        actor = pinyin_module.get_pinyin_rules("initials", pinyin_initial)
        scene = pinyin_module.get_pinyin_rules("finals", pinyin_final)

        while not actor and pinyin_initial:
            actor = input(f"Enter actor for initial '{pinyin_initial}': ").strip()
        while not scene and pinyin_final:
            scene = input(f"Enter scene for final '{pinyin_final}': ").strip()

        # Save if either actor or scene was provided
        if actor or scene:
            # Ensure we have values for both (keep existing if one is empty)
            if not actor:
                actor = pinyin_module.get_pinyin_rules("initials", pinyin_initial)
            if not scene:
                scene = pinyin_module.get_pinyin_rules("finals", pinyin_final)
            
            if actor and scene:
                add_pinyin_rules(pinyin_rules, actor, scene, pinyin_initial, pinyin_final)
        
        return label, actor, scene, tone_override, pinyin_rules
    else:
        pinyin_rules = data.load_pinyin_rules() if selected_pinyin else None
        return label, actor, scene, tone_override, pinyin_rules
