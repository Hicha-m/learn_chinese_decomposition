# Product Requirements Document (PRD)

## 1. Document Information
- Product name: Learn Chinese Decomposition
- Repository: learn_chinese_decomposition
- Version: 1.0 (initial PRD draft)
- Date: 2026-03-31
- Owner: Project maintainer

## 2. Product Summary
Learn Chinese Decomposition is a Python CLI learning tool that helps beginner learners study Chinese characters by decomposing Hanzi into components, guiding pronunciation with pinyin mnemonics, and generating review material in Anki.

The product combines:
- Character decomposition and dependency-aware learning order
- AI-assisted character explanation and context sentence generation
- Local progress persistence for iterative daily learning
- Anki flashcard creation and export

## 3. Problem Statement
Beginners often struggle to memorize Hanzi because characters appear visually dense and disconnected from pronunciation and usage. Existing workflows are frequently fragmented across dictionary apps, notes, and flashcards.

The product solves this by offering one integrated workflow that:
- Breaks each target character into learnable sub-components
- Helps users select and remember pronunciation with mnemonics
- Produces reusable Anki cards automatically
- Preserves progress across sessions

## 4. Goals and Non-Goals

### 4.1 Goals
- Enable a complete end-to-end learning session from a target character to Anki note creation.
- Improve retention by combining decomposition, pinyin cues, and contextual examples.
- Keep all user data local and transparent through file-based persistence.
- Maintain reliability through a clear modular architecture and automated tests.

### 4.2 Non-Goals (Current Scope)
- Full graphical user interface (desktop/mobile/web).
- Multi-user authentication or cloud accounts.
- Audio recording, speech scoring, or pronunciation grading.
- Curriculum management for formal classroom use.

## 5. Target Users
- Primary user: Independent beginner/intermediate Mandarin learner who wants structured Hanzi memorization.
- Secondary user: Power learner already using Anki who wants faster card generation.
- Maintainer user: Developer who wants to extend decomposition rules, prompts, or export behavior.

## 6. User Needs
- As a learner, I want to input a character and get the next learnable item based on dependencies.
- As a learner, I want an understandable explanation with beginner-safe examples.
- As a learner, I want to choose pronunciation when multiple pinyin values exist.
- As a learner, I want generated notes to be exportable to Anki with minimal manual editing.
- As a learner, I want progress to persist between sessions.
- As a maintainer, I want robust tests and modular code so refactors are safe.

## 7. Product Scope and Features

### 7.1 CLI Application Shell
- Startup and setup scripts (`setup.sh`, `run.sh`) for environment and execution.
- Main menu flow with options to:
  - Learn a new character
  - Show progress
  - Export learned content to Anki
  - Export current session to Anki

### 7.2 Character Decomposition and Learning Order
- Build decomposition tree from configured rules.
- Compute dependencies and determine the next learnable character.
- Handle statuses:
  - Learnable now
  - Complete tree already learned
  - Blocked (missing prerequisites)

### 7.3 AI-Assisted Content Generation
- Generate pedagogical explanation for a target character.
- Generate context-driven example sentence extraction from corpus bubble data.
- Support providers currently used by implementation:
  - OpenRouter
  - Google Gemini

### 7.4 Pinyin and Mnemonic Workflow
- Present pinyin options when multiple pronunciations exist.
- Support pinyin initials/finals/tone mnemonic mapping.
- Allow user updates to mnemonic rules and persist them.

### 7.5 Anki Note and Deck Export
- Build structured Anki notes with fields for Hanzi, pinyin, meaning, components, mnemonic fields, and examples.
- Support easy-note mode for lighter cards when context is missing or user chooses simplified review.
- Export deck package for import into Anki.

### 7.6 Data Persistence
- Store user progress and generated artifacts locally in data directories.
- Persist:
  - Learned character list
  - Character characteristics
  - Pinyin rules
  - Temporary session notes
  - Generated Hanzi markdown outputs

### 7.7 Progress Tracking
- Display learned counts and recent character details.
- Ensure progress updates occur after successful card creation.

## 8. Functional Requirements

### FR-1 Initialization
- The system must initialize configuration and required directories before any learning action.
- The system must load decomposition tree rules at runtime from file-backed configuration.

### FR-2 Learning Session
- The system must accept a target character and compute the next learnable character.
- The system must return a learnable candidate with its component radicals when available.

### FR-3 Pronunciation Selection
- The system must allow user selection when multiple pinyin readings exist.
- The system must default to a safe fallback selection when user input is invalid.

### FR-4 AI Content Generation
- The system must generate an explanation prompt and request AI output.
- The system must attempt context sentence extraction when corpus links exist.
- The system must continue gracefully when AI calls fail.

### FR-5 Card Construction
- The system must assemble note fields required by the Chinese Anki model.
- The system must support both full and simplified easy-note creation paths.

### FR-6 Learning State Update
- The system must mark a character as learned only after successful card pipeline completion.
- The system must persist learned state immediately after update.

### FR-7 Export
- The system must export either full learned content or current session content to Anki package format.
- The system must show success/failure feedback in CLI.

## 9. Non-Functional Requirements

### NFR-1 Reliability
- Core workflows must be covered by automated tests (unit + integration/e2e style where applicable).
- File I/O operations must fail safely with warnings and defaults where possible.

### NFR-2 Performance
- Repeatedly used pinyin rules should be cached to minimize repeated disk I/O.
- Typical single-character workflow should complete without noticeable CLI lag excluding external API latency.

### NFR-3 Security and Privacy
- API keys must be loaded from environment/config and never hardcoded in source.
- User learning data should remain local by default.

### NFR-4 Maintainability
- Architecture should remain modular by concern (AI, data, learning, Anki, tree, config).
- Public module boundaries should remain explicit and testable.

### NFR-5 Portability
- Setup and run scripts should support Linux/macOS shell environments and virtual environment workflows.

## 10. Success Metrics
- User can complete a full character session from input to saved Anki note without manual file edits.
- At least 95% test pass rate on default branch test suite.
- Zero data loss in learned character progression across restarts.
- Exported Anki package imports successfully in standard Anki desktop client.

## 11. Milestones

### Milestone A: Stable CLI Core
- Finalize initialization, menu flows, and progress display.
- Ensure decomposition and dependency resolution remain correct.

### Milestone B: AI and Context Quality
- Improve prompt quality and extraction robustness.
- Add fallback behavior for low-quality or empty AI responses.

### Milestone C: Anki Experience Quality
- Improve note templates and tagging strategy.
- Validate export consistency and note deduplication strategy.

### Milestone D: Hardening and Refactoring
- Expand tests around edge cases and regressions.
- Complete planned phase refactors with backward compatibility.

## 12. Risks and Mitigations
- External API instability or quota limits:
  - Mitigation: Graceful fallback paths and clear retry messaging.
- Data schema drift in local JSON/pickle files:
  - Mitigation: Versioned schema checks and migration helpers.
- Character decomposition edge cases:
  - Mitigation: Rule override mechanisms and targeted regression tests.
- User confusion in text-only UX:
  - Mitigation: Improve prompts, validation feedback, and progress summaries.

## 13. Open Questions
- Should the product support offline-only mode without AI dependencies?
- Should pinyin rule editing be formalized into a dedicated CLI menu?
- Should duplicate note detection be enforced before Anki export?
- Which model/provider should be default for cost vs quality optimization?

## 14. Acceptance Criteria (Release Readiness)
- A new user can run setup and launch the CLI successfully.
- User can learn one new character end-to-end and see progress updated.
- User can export notes and import generated deck into Anki.
- Test suite passes in CI/local baseline environment.
- Documentation clearly describes setup, workflow, and required environment variables.
