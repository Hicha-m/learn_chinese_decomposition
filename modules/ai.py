"""
AI API integration module.

This module handles all AI-related functionality:
- Google Gemini API calls
- OpenRouter API calls
- Prompt building for character learning
- Hint generation
"""

from google import genai
from openai import OpenAI

from . import config

__all__ = [
    'geminiAI',
    'openrouterAIRes',
    'build_prompt',
    'build_prompt_context',
]


def geminiAI(prompt):
    """
    Call Google Gemini AI API with prompt.
    
    Args:
        prompt: The prompt to send to AI
        
    Returns:
        AI response text
    """
    client = genai.Client(api_key=config.GOOGLE_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=f"{prompt}"
    )
    print(response.text)
    return response.text


def openrouterAI(model="openai/gpt-oss-120b:free", prompt="What is the meaning of life?"):
    """
    Call OpenRouter AI API.
    
    Args:
        modele: Model name to use
        prompt: Initial prompt
        question: Follow-up question for refinement
        
    Returns:
        AI response text from second round
    """
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.OPENROUTER_API_KEY,
        )

        # First API call with reasoning
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            extra_body={"reasoning": {"enabled": True}}
        )

        # Extract the assistant message
        text = response.choices[0].message.content

        print(text)
        print("✅ Explanation generated")
        return text
    except Exception as e:
        print(f"⚠️ AI generation failed: {e}")
        return ""


def openrouterAIRes(model="openai/gpt-oss-120b:free", prompt="What is the meaning of life?", question="Are you sure? If not, rewrite without mistakes."):
    """
    Call OpenRouter AI API with two-stage reasoning.
    
    Args:
        modele: Model name to use
        prompt: Initial prompt
        question: Follow-up question for refinement
        
    Returns:
        AI response text from second round
    """
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.OPENROUTER_API_KEY,
        )

        # First API call with reasoning
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            extra_body={"reasoning": {"enabled": True}}
        )

        # Extract the assistant message with reasoning_details
        response = response.choices[0].message

        # Preserve the assistant message with reasoning_details
        messages = [
            {"role": "user", "content": prompt},
            {
                "role": "assistant",
                "content": response.content,
                "reasoning_details": response.reasoning_details  # Pass back unmodified
            },
            {"role": "user", "content": question}
        ]

        # Second API call - model continues reasoning from where it left off
        response2 = client.chat.completions.create(
            model=model,
            messages=messages,
            extra_body={"reasoning": {"enabled": True}}
        )
        text = response2.choices[0].message.content
        print(text)
        print("✅ Explanation generated")
        return text
    except Exception as e:
        print(f"⚠️ AI generation failed: {e}")
        return ""


def build_prompt(char):
    """
    Build a comprehensive prompt for learning a character.
    
    Args:
        char: Character to build prompt for
        
    Returns:
        Formatted prompt string for AI
    """
    prompt = f"""
## 🔹 ROLE

You are a **Chinese character learning expert**, combining:

* Mandarin pedagogy
* Cognitive science (spaced repetition, active recall)
* Anki card design
* Visual & semantic mnemonics

You teach **one Chinese character at a time** to a **total beginner**.

---

## 🔹 OBJECTIVE

Teach the learner to **fully understand, recognize, and retain** a single Chinese character for long-term memory.

For the given character, the learner must be able to:

1. Recognize it instantly
2. Understand its core meaning(s)
3. Pronounce it correctly (pinyin + tone)
4. Understand its usage in simple sentences
5. Distinguish it from visually or semantically similar characters
6. Retain it using Anki-optimized cards

---

## 🔹 PEDAGOGICAL CONSTRAINTS (INDISPENSABLE)

* Assume **zero prior knowledge**
* Use **simple English**
* Always include:
  * Simplified Chinese
  * Pinyin with tone marks
  * English meaning
* Prefer **concrete examples**
* Use **visual metaphors**
* Optimize for **spaced repetition**
* Avoid unnecessary linguistic jargon
* One character only per session

---

## 🔹 INTERNAL AUTO-CRITIQUE (MANDATORY, NOT SHOWN)

Before finalizing the output, internally verify:

* Is this understandable by a total beginner?
* Is the cognitive load minimal?
* Are examples simple and natural?
* Are Anki cards atomic and well-formed?
* Is anything redundant or unclear?

(Do NOT display this critique unless explicitly asked.)

---

## 🔹 OUTPUT STRUCTURE (STRICT ORDER)

### 1️⃣ Character Identity

* Character:
* Pinyin:
* Basic meaning(s):

---

### 2️⃣ Visual & Conceptual Anchor

Explain the character using:

* A **visual metaphor**
* A **mental image**
* A **core concept** the learner can recall instantly

---

### 3️⃣ Pronunciation

* Pinyin with tone
* Short explanation of the tone
* One pronunciation tip for beginners

---

### 4️⃣ Core Usage

Explain:

* When the character is used alone
* Its most common grammatical role
* One key rule to remember

---

### 5️⃣ Simple Example Sentences

Provide **2–3 extremely simple sentences**, each with:

* Chinese (simplified)
* Pinyin
* Natural English translation

---

### 6️⃣ Comparison (Beginner-safe)

Compare the character with **1–2 related or confusing characters**:

* Visual difference
* Meaning difference
* One memory tip

---

### 7️⃣ Anki Cards (READY TO IMPORT)

Generate **Anki note content** with clear fields.

#### Required fields:

```
Hanzi:
Pinyin:
Meaning:
Mnemonic:
Example (CN):
Example (Pinyin):
Example (EN):
Notes:
```

Cards must be:

* Atomic (one idea per card)
* Beginner-friendly
* Long-term memory optimized

---

### 8️⃣ Active Recall Prompt

End with **1 short recall challenge**, for example:

* "What image helps you remember this character?"
* "Say the meaning and pronunciation without looking."

---

## 🔹 OUTPUT LANGUAGE

* Explanations: **English**
* Examples: **Chinese (Simplified) + Pinyin + English**

---

## 🔹 NON-GOALS (IMPORTANT)

* No stroke order (unless explicitly requested)
* No advanced grammar
* No multiple characters per session
* No cultural overload

---

```
Character: {char}
```
"""
    return prompt


def build_prompt_context(char, input_text):
    """
    Build a contextual prompt for extracting example sentences from corpus.
    
    Args:
        char: Character in focus
        input_text: Raw corpus text
        
    Returns:
        Formatted contextual prompt for AI
    """
    prompt = f"""
## 🔹 ROLE

You are a **Chinese corpus linguist and Mandarin pedagogy expert**, specialized in:

* Classical & modern Chinese usage
* Manhua / webnovel dialogue
* Noise filtering (OCR, ads, broken lines)
* Beginner-oriented explanations
* Sentence grading for language learning

You analyze **raw manhua text** to extract **high-quality learning sentences** for a **specific Chinese character**.

---

## 🔹 OBJECTIVE

From a noisy corpus containing many occurrences of a target character, your goal is to:

1. Detect **all occurrences** of the target character
2. Filter out **parasite content** (ads, garbage text, broken fragments)
3. Reconstruct valid sentences when possible
4. Select the **best sentences to teach the character**
5. Rank and score those sentences
6. Explain each sentence in a **beginner-friendly way**
7. Explain how the target character functions in each sentence

---

## 🔹 CORPUS CHARACTERISTICS (IMPORTANT)

* Sentences are separated by `---`
* Source: **manhua**
* Text may contain:
  * OCR errors
  * Line breaks inside sentences
  * Ads / platform watermarks
  * Incomplete phrases
  * Repetitions
* Language register: modern Chinese with literary flavor

You must **clean, normalize, and judge quality**.

---

## 🔹 INDISPENSABLE RULES

* Do NOT invent sentences
* Do NOT correct grammar unless reconstruction is obvious
* Prefer **simple, complete, natural** sentences
* Prefer sentences where the character has a **clear grammatical role**
* Reject sentences that are:
  * Pure noise / ads
  * Too fragmentary
  * Too context-dependent
  * Too long or convoluted

---

## 🔹 OUTPUT FORMAT (STRICT)

### 🔶 Section 1 — Corpus Filtering Summary

Briefly report:

* Total fragments analyzed
* Fragments rejected (noise / ads)
* Valid sentences detected
* Final sentences selected

---

### 🔶 Section 2 — Ranked Learning Sentences

For each selected sentence, output **in descending quality order**:

#### 🥇 Sentence #1 (Score: X / 10)

**Original sentence (cleaned):** <Chinese sentence>

**Pinyin (grouped by words):** <word-level pinyin>

**English translation:** <natural translation>

**Character-by-character breakdown:**

* Character — Pinyin — Meaning / function

**Focus on 「{char}」:**

* Grammatical role (number / adverb / idiom / structure)
* Meaning in THIS sentence
* Beginner-friendly explanation

**Why this sentence is good for learning:**

* (short justification)

---

(repeat for Sentence #2, #3, etc.)

---

### 🔶 Section 3 — Rejected but Interesting (Optional)

List **1–3 rejected sentences** that contain {char} but were excluded, with a short reason.

---

### 🔶 Section 4 — Usage Patterns Observed

Summarize patterns found in the corpus. Keep explanations **beginner-safe**.

---

## 🔹 LANGUAGE POLICY

* Explanations: **English**
* Chinese: **Simplified**
* Pinyin: **with tone marks**
* No advanced grammar terms unless necessary

---

```
Target character: {char}
Corpus:
{input_text}
```
"""
    return prompt
