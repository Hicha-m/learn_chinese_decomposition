"""
Main execution module.

This module contains the main workflow and entry point for the
Chinese character learning application.
"""

from . import config, data, tree, learning, ai, anki, pinyin as pinyin_module


def initialize_application():
    """
    Initialize the application.
    
    Loads configuration, creates necessary directories, and initializes data.
    """
    print("🚀 Initializing Chinese Character Learning Application...")
    
    # Initialize configuration
    config.initialize_config()
    
    # Create necessary directories
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.HANZI_DIR.mkdir(parents=True, exist_ok=True)
    config.ANKI_DIR.mkdir(parents=True, exist_ok=True)
    
    print("✅ Application initialized successfully")


def learn_new_character(target_char):
    """
    Main learning workflow for a new character.
    
    Args:
        target_char: Character to learn
    """
    print(f"\n📚 Learning character: {target_char}")
    print("=" * 50)
    
    # Initialize if needed
    if not config.PINYIN_RULES:
        initialize_application()
    
    # Load learned characters
    learned_chars = data.load_learned_chars()
    print(f"Already learned: {len(learned_chars)} characters")
    
    # Create tree builder
    builder = tree.HanziTreeBuilder(
        overrides=config.my_overrides,
        path_overrides=config.my_path_overrides,
        atomic_chars=config.my_stops,
        max_depth=8
    )
    
    # Step 1: Learn character breakdown
    print("\n1️⃣ Analyzing character structure...")
    char_to_learn, radicals = learning.learn_character(target_char, builder, learned_chars)
    
    if not char_to_learn:
        print("❌ Cannot determine next character to learn")
        return
    
    print(f"\n✅ Next character to learn: {char_to_learn}")
    print(f"   Components: {radicals}")
    
    # Step 2: Get dictionary information (simulated - would need dictionary API)
    print("\n2️⃣ Gathering character information...")
    # In real implementation, would call dictionary API
    option = {
        'pinyin': [],
        'definition': []
    }
    print("   (Dictionary lookup - placeholder)")
    
    # Step 3: Generate AI explanation
    print("\n3️⃣ Generating AI explanation...")
    prompt = ai.build_prompt(char_to_learn)
    try:
        explanation = ai.openrouterAIRes(
            modele="xiaomi/mimo-v2-flash:free",
            prompt=prompt,
            question="Are you sure? If not, rewrite without mistakes."
        )
        data.save_hanzi(char_to_learn, explanation, "explain")
        print("✅ Explanation generated and saved")
    except Exception as e:
        print(f"⚠️ AI generation failed: {e}")
        explanation = ""
    
    # Step 4: Extract example sentence
    print("\n4️⃣ Extracting example sentences...")
    sentence = ""
    # In full implementation, would extract from corpus
    print("   (Sentence extraction - placeholder)")
    
    # Step 5: Create Anki card
    print("\n5️⃣ Creating Anki flashcard...")
    try:
        label = "learning"  # Visual/semantic label
        tone = "4"  # Default tone
        
        characteristics = learning.characteristics_hanzi(
            char_to_learn,
            option,
            sentence,
            label,
            radicals,
            tone,
            config.PINYIN_RULES
        )
        
        model = anki.get_chinese_model()
        note = anki.note_anki_chinese(model, characteristics, easy_note=False)
        print("✅ Anki card created")
    except Exception as e:
        print(f"⚠️ Card creation failed: {e}")
        return
    
    # Step 6: Mark as learned
    print("\n6️⃣ Recording progress...")
    learning.mark_as_learned(char_to_learn, learned_chars)
    print(f"✅ {char_to_learn} marked as learned")
    
    print("\n" + "=" * 50)
    print("✅ Character learning session complete!")


def export_to_anki_deck():
    """Export learned characters to Anki deck file."""
    print("\n📤 Exporting to Anki...")
    try:
        anki.export_chars_learn_to_anki()
        print("✅ Export complete: mandarin_chinese.apkg")
    except Exception as e:
        print(f"❌ Export failed: {e}")


def show_learning_progress():
    """Display current learning progress."""
    learned_chars = data.load_learned_chars()
    chars_characteristic = data.load_learned_chars_characteristic()
    
    print("\n📊 Learning Progress")
    print("=" * 50)
    print(f"Characters learned: {len(learned_chars)}")
    print(f"Characters with details: {len(chars_characteristic)}")
    
    if chars_characteristic:
        print("\nRecent characters:")
        for i, (char, info) in enumerate(list(chars_characteristic.items())[-5:], 1):
            pinyin = info.get('pinyin', 'N/A')
            english = info.get('english', 'N/A')
            print(f"  {i}. {char} [{pinyin}] - {english}")


def main():
    """
    Main application entry point.
    
    Orchestrates the character learning process:
    1. Initialize application
    2. Load or create learned characters
    3. Load configuration and rules
    4. Accept user input or run demo
    5. Execute learning workflow
    """
    print("\n" + "=" * 50)
    print("🎯 Chinese Character Learning System")
    print("=" * 50)
    
    # Initialize
    initialize_application()
    
    # Show menu
    print("\nOptions:")
    print("  1. Learn new character")
    print("  2. Show progress")
    print("  3. Export to Anki")
    print("  4. Demo (learn '是')")
    print("  0. Exit")
    
    choice = input("\nSelect option (0-4): ").strip()
    
    if choice == "1":
        char = input("Enter character to learn: ").strip()
        if char:
            learn_new_character(char)
    elif choice == "2":
        show_learning_progress()
    elif choice == "3":
        export_to_anki_deck()
    elif choice == "4":
        # Demo with a common character
        learn_new_character("是")
    elif choice == "0":
        print("👋 Goodbye!")
    else:
        print("Invalid option")


if __name__ == '__main__':
    main()
