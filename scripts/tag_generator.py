#!/usr/bin/env python3
"""
YouTube Smart Tag Generator
Generates categorized, SEO-optimized tags for YouTube videos.

Usage:
    python3 tag_generator.py "<topic>" "<primary_keyword>" "<language>"

Example:
    python3 tag_generator.py "Python AI Agent" "python ai agent tutorial" "english"
"""

import sys
import re
import json


# ─── Tag Templates ────────────────────────────────────────────────────────────

TUTORIAL_SUFFIXES = [
    "tutorial", "guide", "course", "explained", "for beginners",
    "step by step", "from scratch", "full course", "crash course",
    "walkthrough", "masterclass", "bootcamp", "lesson", "lecture",
]

MODIFIER_TAGS = [
    "best", "top", "how to", "learn", "easy", "simple",
    "free", "2026", "2025", "latest", "new", "updated",
    "complete", "ultimate", "beginner", "advanced", "pro",
]

TECH_CATEGORIES = {
    "python": ["python programming", "python tutorial", "python project", "python code", "python for beginners"],
    "javascript": ["javascript tutorial", "js tutorial", "javascript project", "web development", "frontend"],
    "ai": ["artificial intelligence", "ai tutorial", "machine learning", "deep learning", "ai project"],
    "ml": ["machine learning", "ml tutorial", "data science", "sklearn", "ml project"],
    "web": ["web development", "website", "html css", "frontend", "backend", "full stack"],
    "react": ["react tutorial", "reactjs", "react project", "frontend framework", "react hooks"],
    "node": ["nodejs", "node tutorial", "backend development", "express js", "server side"],
    "data": ["data science", "data analysis", "data visualization", "pandas", "numpy"],
    "nlp": ["natural language processing", "nlp tutorial", "text analysis", "chatbot", "language model"],
    "agent": ["ai agent", "autonomous agent", "agent tutorial", "langchain", "ai automation"],
}

BANGLA_TAG_TEMPLATES = [
    "{topic} বাংলা",
    "{topic} টিউটোরিয়াল",
    "{topic} শেখা",
    "{topic} বাংলায় শেখো",
    "{topic} কোর্স বাংলা",
    "বাংলা {topic}",
    "{topic} প্রজেক্ট",
    "{topic} গাইড বাংলা",
]

ENGAGEMENT_TAGS = [
    "tips and tricks", "mistakes to avoid", "things you should know",
    "secrets", "hidden features", "pro tips", "common mistakes",
]


def clean_text(text: str) -> str:
    """Normalize input text."""
    return re.sub(r'\s+', ' ', text.strip().lower())


def extract_words(text: str) -> list:
    """Extract meaningful words from text."""
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'and', 'or', 'but', 'not', 'this', 'that', 'it',
        'by', 'from', 'as', 'be', 'দিয়ে', 'এবং', 'ও', 'কে', 'তে',
    }
    words = clean_text(text).split()
    return [w for w in words if w not in stop_words and len(w) > 1]


def generate_tags(topic: str, primary_keyword: str, language: str = "english") -> dict:
    """Generate comprehensive tags for a YouTube video."""
    topic_clean = clean_text(topic)
    kw_clean = clean_text(primary_keyword)
    words = extract_words(topic)
    lang = language.lower().strip()

    tags = {
        "exact_match": [],
        "long_tail": [],
        "related_topic": [],
        "broad_category": [],
        "language_specific": [],
    }

    # ─── Exact Match Tags ───
    tags["exact_match"].append(kw_clean)
    tags["exact_match"].append(topic_clean)
    # Word combinations
    if len(words) >= 2:
        for i in range(len(words)):
            for j in range(i + 1, min(i + 3, len(words) + 1)):
                combo = ' '.join(words[i:j])
                if combo not in tags["exact_match"]:
                    tags["exact_match"].append(combo)

    # ─── Long-tail Tags ───
    for suffix in TUTORIAL_SUFFIXES[:8]:
        tag = f"{topic_clean} {suffix}"
        if len(tag) <= 50:
            tags["long_tail"].append(tag)

    for mod in MODIFIER_TAGS[:8]:
        tag = f"{mod} {topic_clean}"
        if len(tag) <= 50:
            tags["long_tail"].append(tag)

    tags["long_tail"].append(f"how to {topic_clean}")
    tags["long_tail"].append(f"{topic_clean} 2026")
    tags["long_tail"].append(f"learn {topic_clean}")

    # ─── Related Topic Tags ───
    for word in words:
        if word in TECH_CATEGORIES:
            tags["related_topic"].extend(TECH_CATEGORIES[word][:5])

    # Add engagement tags
    for eng_tag in ENGAGEMENT_TAGS[:4]:
        tags["related_topic"].append(f"{words[0]} {eng_tag}" if words else eng_tag)

    # ─── Broad Category Tags ───
    broad_categories = [
        "technology", "programming", "coding", "software",
        "education", "tutorial", "learning", "tech",
    ]
    for cat in broad_categories:
        if cat not in topic_clean:
            tags["broad_category"].append(cat)

    # ─── Language-Specific Tags ───
    if lang in ("bangla", "mixed"):
        for template in BANGLA_TAG_TEMPLATES:
            tag = template.format(topic=topic_clean)
            tags["language_specific"].append(tag)
        tags["language_specific"].append(f"{topic_clean} bangla tutorial")
        tags["language_specific"].append(f"{topic_clean} in bangla")

    if lang in ("english", "mixed"):
        tags["language_specific"].append(f"{topic_clean} in english")
        tags["language_specific"].append(f"{topic_clean} english tutorial")

    # ─── Deduplicate and Clean ───
    for category in tags:
        seen = set()
        unique = []
        for tag in tags[category]:
            tag_clean = tag.strip().lower()
            if tag_clean and tag_clean not in seen:
                seen.add(tag_clean)
                unique.append(tag_clean)
        tags[category] = unique

    # ─── Enforce 500 Character Limit ───
    all_tags = []
    total_chars = 0
    for category in ["exact_match", "long_tail", "related_topic", "language_specific", "broad_category"]:
        for tag in tags[category]:
            # Account for comma separator
            tag_len = len(tag) + (2 if all_tags else 0)  # ", " separator
            if total_chars + tag_len <= 500:
                all_tags.append(tag)
                total_chars += tag_len

    result = {
        "topic": topic,
        "primary_keyword": primary_keyword,
        "language": lang,
        "categorized_tags": tags,
        "all_tags": all_tags,
        "total_tags": len(all_tags),
        "total_characters": total_chars,
        "character_limit": 500,
        "tags_string": ", ".join(all_tags),
    }

    return result


def print_tag_report(result: dict):
    """Print formatted tag report."""
    print("=" * 60)
    print(f"  🏷️  TAG GENERATION REPORT")
    print(f"  Topic: {result['topic']}")
    print("=" * 60)
    print()

    print(f"📊 Total Tags: {result['total_tags']}")
    print(f"📊 Characters Used: {result['total_characters']}/{result['character_limit']}")
    print()

    for category, category_tags in result["categorized_tags"].items():
        if category_tags:
            label = category.replace('_', ' ').upper()
            print(f"─── {label} ({len(category_tags)}) ──────────────────────")
            for i, tag in enumerate(category_tags, 1):
                print(f"  {i:2d}. {tag}")
            print()

    print("─── COPY-PASTE READY ─────────────────────────────────")
    print(result["tags_string"])
    print()

    print("─── JSON OUTPUT ──────────────────────────────────────")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python3 tag_generator.py "<topic>" "<primary_keyword>" [language]')
        print("  language: english (default), bangla, mixed")
        sys.exit(1)

    topic_input = sys.argv[1]
    keyword_input = sys.argv[2]
    lang_input = sys.argv[3] if len(sys.argv) > 3 else "english"

    result = generate_tags(topic_input, keyword_input, lang_input)
    print_tag_report(result)
