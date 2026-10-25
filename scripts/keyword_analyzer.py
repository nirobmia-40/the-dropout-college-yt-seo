#!/usr/bin/env python3
"""
YouTube Keyword Analyzer
Analyzes a topic and generates keyword suggestions for YouTube SEO.

Usage:
    python3 keyword_analyzer.py "<topic>" "<language>"

Example:
    python3 keyword_analyzer.py "Python AI Agent Tutorial" "english"
    python3 keyword_analyzer.py "পাইথন দিয়ে AI Agent" "bangla"
"""

import sys
import re
import json
from collections import Counter


# ─── Keyword Templates ───────────────────────────────────────────────────────

HOW_TO_PREFIXES = [
    "how to", "how to make", "how to build", "how to create",
    "how to use", "how to learn", "how to start", "how to do",
]

MODIFIER_WORDS = [
    "best", "top", "ultimate", "complete", "beginner", "advanced",
    "free", "easy", "fast", "simple", "step by step", "full course",
    "tutorial", "guide", "tips", "tricks", "secrets", "2026", "2025",
    "for beginners", "from scratch", "in hindi", "in bangla",
    "masterclass", "crash course", "roadmap", "project",
]

QUESTION_WORDS = [
    "what is", "why", "when to use", "which is better",
    "can you", "should you", "is it worth",
]

BANGLA_MODIFIERS = [
    "টিউটোরিয়াল", "শেখা", "কিভাবে", "সহজে", "বাংলায়",
    "সম্পূর্ণ গাইড", "ফ্রি কোর্স", "প্রজেক্ট", "টিপস",
    "শিখুন", "বেসিক", "এডভান্সড", "সেরা উপায়",
]


def clean_topic(topic: str) -> str:
    """Clean and normalize the topic string."""
    topic = topic.strip().lower()
    topic = re.sub(r'[^\w\s\u0980-\u09FF]', '', topic)  # Keep Bangla chars
    topic = re.sub(r'\s+', ' ', topic)
    return topic


def extract_core_words(topic: str) -> list:
    """Extract meaningful words from the topic."""
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at',
        'to', 'for', 'of', 'with', 'and', 'or', 'but', 'not', 'this',
        'that', 'it', 'by', 'from', 'as', 'be', 'has', 'have', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
        'might', 'i', 'you', 'he', 'she', 'we', 'they', 'my', 'your',
        'দিয়ে', 'এবং', 'ও', 'তে', 'এর', 'কে', 'র', 'য়',
    }
    words = topic.split()
    return [w for w in words if w.lower() not in stop_words and len(w) > 1]


def generate_primary_keywords(topic: str, core_words: list) -> list:
    """Generate primary keyword variations."""
    keywords = [topic]

    # Add word-order variations
    if len(core_words) >= 2:
        keywords.append(' '.join(reversed(core_words)))
        for i in range(len(core_words)):
            for j in range(i + 1, len(core_words)):
                keywords.append(f"{core_words[i]} {core_words[j]}")

    return list(dict.fromkeys(keywords))  # Remove dupes, preserve order


def generate_long_tail_keywords(topic: str, core_words: list, language: str) -> list:
    """Generate long-tail keyword variations."""
    long_tails = []

    # How-to variations
    for prefix in HOW_TO_PREFIXES[:4]:
        long_tails.append(f"{prefix} {topic}")

    # Modifier variations
    modifiers = MODIFIER_WORDS if language != "bangla" else BANGLA_MODIFIERS
    for mod in modifiers[:10]:
        long_tails.append(f"{topic} {mod}")
        if language != "bangla":
            long_tails.append(f"{mod} {topic}")

    # Question variations
    for q in QUESTION_WORDS[:4]:
        long_tails.append(f"{q} {topic}")

    # Year variations
    long_tails.append(f"{topic} 2026")
    long_tails.append(f"{topic} 2025")

    return list(dict.fromkeys(long_tails))


def generate_related_keywords(core_words: list) -> list:
    """Generate related/LSI keyword suggestions."""
    related = []
    # Combine core words with common tech/content terms
    related_terms = [
        "tutorial", "example", "project", "course", "explained",
        "vs", "alternative", "review", "setup", "install",
        "beginner", "advanced", "tips", "best practices",
    ]
    for word in core_words[:3]:
        for term in related_terms[:8]:
            related.append(f"{word} {term}")

    return list(dict.fromkeys(related))


def calculate_keyword_score(keyword: str, topic: str, core_words: list) -> int:
    """Calculate a relevance score for a keyword (0-100)."""
    score = 50  # Base score

    # Exact match bonus
    if topic in keyword.lower():
        score += 20

    # Core word presence
    kw_lower = keyword.lower()
    matches = sum(1 for w in core_words if w in kw_lower)
    score += min(matches * 10, 20)

    # Length penalty (too long is bad)
    word_count = len(keyword.split())
    if word_count <= 5:
        score += 10
    elif word_count > 8:
        score -= 10

    # Modifier bonus
    for mod in MODIFIER_WORDS:
        if mod in kw_lower:
            score += 5
            break

    return min(max(score, 0), 100)


def analyze_keywords(topic: str, language: str = "english") -> dict:
    """Main keyword analysis function."""
    cleaned = clean_topic(topic)
    core_words = extract_core_words(cleaned)
    lang = language.lower().strip()

    # Generate keyword categories
    primary = generate_primary_keywords(cleaned, core_words)
    long_tail = generate_long_tail_keywords(cleaned, core_words, lang)
    related = generate_related_keywords(core_words)

    # Score all keywords
    scored_primary = [
        {"keyword": kw, "score": calculate_keyword_score(kw, cleaned, core_words), "type": "primary"}
        for kw in primary[:10]
    ]
    scored_long_tail = [
        {"keyword": kw, "score": calculate_keyword_score(kw, cleaned, core_words), "type": "long-tail"}
        for kw in long_tail[:20]
    ]
    scored_related = [
        {"keyword": kw, "score": calculate_keyword_score(kw, cleaned, core_words), "type": "related"}
        for kw in related[:15]
    ]

    # Sort each by score
    scored_primary.sort(key=lambda x: x["score"], reverse=True)
    scored_long_tail.sort(key=lambda x: x["score"], reverse=True)
    scored_related.sort(key=lambda x: x["score"], reverse=True)

    result = {
        "topic": topic,
        "language": lang,
        "core_words": core_words,
        "primary_keywords": scored_primary,
        "long_tail_keywords": scored_long_tail,
        "related_keywords": scored_related,
        "recommended_primary": scored_primary[0]["keyword"] if scored_primary else topic,
        "total_keywords_generated": len(scored_primary) + len(scored_long_tail) + len(scored_related),
    }

    return result


def print_report(result: dict):
    """Print a formatted keyword analysis report."""
    print("=" * 65)
    print(f"  🔍 KEYWORD ANALYSIS REPORT")
    print(f"  Topic: {result['topic']}")
    print(f"  Language: {result['language']}")
    print("=" * 65)
    print()

    print(f"📌 Core Words: {', '.join(result['core_words'])}")
    print(f"📌 Recommended Primary Keyword: {result['recommended_primary']}")
    print(f"📌 Total Keywords Generated: {result['total_keywords_generated']}")
    print()

    print("─── PRIMARY KEYWORDS ──────────────────────────────────────")
    for kw in result["primary_keywords"]:
        bar = "█" * (kw["score"] // 10) + "░" * (10 - kw["score"] // 10)
        print(f"  [{kw['score']:3d}] {bar} {kw['keyword']}")
    print()

    print("─── LONG-TAIL KEYWORDS ────────────────────────────────────")
    for kw in result["long_tail_keywords"][:15]:
        bar = "█" * (kw["score"] // 10) + "░" * (10 - kw["score"] // 10)
        print(f"  [{kw['score']:3d}] {bar} {kw['keyword']}")
    print()

    print("─── RELATED/LSI KEYWORDS ──────────────────────────────────")
    for kw in result["related_keywords"][:10]:
        bar = "█" * (kw["score"] // 10) + "░" * (10 - kw["score"] // 10)
        print(f"  [{kw['score']:3d}] {bar} {kw['keyword']}")
    print()

    # Also output JSON for programmatic use
    print("─── JSON OUTPUT ───────────────────────────────────────────")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 keyword_analyzer.py \"<topic>\" [language]")
        print("  language: english (default), bangla, mixed")
        sys.exit(1)

    topic_input = sys.argv[1]
    lang_input = sys.argv[2] if len(sys.argv) > 2 else "english"

    result = analyze_keywords(topic_input, lang_input)
    print_report(result)
