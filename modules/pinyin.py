"""
Pinyin processing utilities.

This module provides a clean, dependency-free implementation of
`split_pinyin()` to parse a pinyin syllable into:
- initial
- final
- tone
"""

from __future__ import annotations

import re

__all__ = [
	"split_pinyin",
]


_TONE_MARKS = {
	"ā": ("a", "1"), "á": ("a", "2"), "ǎ": ("a", "3"), "à": ("a", "4"),
	"ē": ("e", "1"), "é": ("e", "2"), "ě": ("e", "3"), "è": ("e", "4"),
	"ī": ("i", "1"), "í": ("i", "2"), "ǐ": ("i", "3"), "ì": ("i", "4"),
	"ō": ("o", "1"), "ó": ("o", "2"), "ǒ": ("o", "3"), "ò": ("o", "4"),
	"ū": ("u", "1"), "ú": ("u", "2"), "ǔ": ("u", "3"), "ù": ("u", "4"),
	"ǖ": ("ü", "1"), "ǘ": ("ü", "2"), "ǚ": ("ü", "3"), "ǜ": ("ü", "4"),
}


def _strip_tone_marks(syllable: str) -> tuple[str, str]:
	"""
	Replace tone-marked vowels with base vowels and return tone.

	Returns:
		(clean_syllable, tone)
	"""
	tone = "5"
	out_chars = []
	for ch in syllable:
		if ch in _TONE_MARKS:
			base, t = _TONE_MARKS[ch]
			out_chars.append(base)
			tone = t
		else:
			out_chars.append(ch)
	return "".join(out_chars), tone


def _extract_tone_number(syllable: str) -> tuple[str, str]:
	"""
	Extract numeric tone if present at the end (1-5).
	"""
	match = re.match(r"^(.+?)([1-5])$", syllable)
	if match:
		return match.group(1), match.group(2)
	return syllable, ""


def _get_initial_candidates(pinyin_rules: dict | None) -> list[str]:
	"""
	Build list of possible initials, longest-first.
	"""
	if pinyin_rules and isinstance(pinyin_rules, dict) and "initials" in pinyin_rules:
		initials = list(pinyin_rules["initials"].keys())
	else:
		initials = [
			"zh", "ch", "sh",
			"b", "p", "m", "f", "d", "t", "n", "l",
			"g", "k", "h", "r", "z", "c", "s", "y", "w",
		]
	initials = sorted(set(initials), key=len, reverse=True)
	return initials


def split_pinyin(pinyin: str, pinyin_rules: dict | None = None) -> tuple[str, str, str]:
	"""
	Split a pinyin syllable into (initial, final, tone).

	Args:
		pinyin: Pinyin syllable, with tone number or tone marks.
		pinyin_rules: Optional rules dict (used to derive initials list).

	Returns:
		(initial, final, tone)
	"""
	if not pinyin:
		return "", "", ""

	syllable = pinyin.strip().lower()

	# 1) Numeric tone (e.g., "shi4")
	syllable, tone = _extract_tone_number(syllable)

	# 2) Tone marks (e.g., "shì")
	if not tone:
		syllable, tone = _strip_tone_marks(syllable)
	if not tone:
		tone = "5"

	# 3) Initial/final split
	initials = _get_initial_candidates(pinyin_rules)
	initial = ""
	final = syllable
	for cand in initials:
		if cand and syllable.startswith(cand):
			initial = cand
			final = syllable[len(cand):]
			break

	return initial, final, tone
