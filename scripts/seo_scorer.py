#!/usr/bin/env python3
"""
YouTube SEO Scorer
Calculates SEO scores for YouTube video titles, descriptions, and overall content.

Usage:
    python3 seo_scorer.py --type title "<title>" "<primary_keyword>"
    python3 seo_scorer.py --type description "<description>" "<primary_keyword>"
    python3 seo_scorer.py --type full "<title>" "<description>" "<tags>" "<primary_keyword>"
"""

import sys
import re
import json
import argparse


# ─── Constants ────────────────────────────────────────────────────────────────

POWER_WORDS = {
    "ultimate", "complete", "best", "top", "secret", "proven", "amazing",
    "incredible", "essential", "powerful", "effective", "guaranteed",
    "exclusive", "master", "expert", "professional", "advanced",
    "beginner", "easy", "simple", "fast", "quick", "free", "new",
    "how to", "step by step", "guide", "tutorial", "tips", "tricks",
    "hack", "hacks", "mistake", "mistakes", "avoid", "never", "always",
    "why", "what", "review", "vs", "comparison",
}

EMOTIONAL_TRIGGERS = {
    "mind-blowing", "shocking", "surprising", "unbelievable", "insane",
    "crazy", "awesome", "epic", "game-changer", "life-changing",
    "you need", "must watch", "don't miss", "stop doing", "warning",
    "finally", "nobody tells you", "truth about",
}

CTA_PHRASES = {
    "subscribe", "like", "comment", "share", "bell icon", "notification",
    "let me know", "tell me", "what do you think", "drop a comment",
    "hit the like", "smash the like", "turn on notifications",
}

YEAR_PATTERN = re.compile(r'\b20[2-3]\d\b')
NUMBER_PATTERN = re.compile(r'\b\d+\b')


# ─── Title Scorer ─────────────────────────────────────────────────────────────

def score_title(title: str, primary_keyword: str) -> dict:
    """Score a YouTube video title for SEO optimization."""
    scores = {}
    details = {}
    title_lower = title.lower()
    kw_lower = primary_keyword.lower()

    # 1. Keyword Presence (0-25)
    if kw_lower in title_lower:
        kw_pos = title_lower.index(kw_lower)
        if kw_pos < 40:
            scores["keyword_placement"] = 25
            details["keyword_placement"] = "✅ Primary keyword found in first 40 chars"
        else:
            scores["keyword_placement"] = 15
            details["keyword_placement"] = "⚠️ Keyword present but after 40th character"
    else:
        # Check partial match
        kw_words = kw_lower.split()
        matches = sum(1 for w in kw_words if w in title_lower)
        partial_score = int((matches / max(len(kw_words), 1)) * 15)
        scores["keyword_placement"] = partial_score
        details["keyword_placement"] = f"⚠️ Partial keyword match ({matches}/{len(kw_words)} words)"

    # 2. Title Length (0-20)
    title_len = len(title)
    if 50 <= title_len <= 70:
        scores["length"] = 20
        details["length"] = f"✅ Optimal length ({title_len} chars)"
    elif 40 <= title_len < 50 or 70 < title_len <= 80:
        scores["length"] = 15
        details["length"] = f"⚠️ Acceptable length ({title_len} chars), ideal is 50-70"
    elif title_len < 40:
        scores["length"] = 8
        details["length"] = f"❌ Too short ({title_len} chars), add more detail"
    else:
        scores["length"] = 5
        details["length"] = f"❌ Too long ({title_len} chars), may get truncated"

    # 3. Power Words (0-20)
    found_power = [w for w in POWER_WORDS if w in title_lower]
    if len(found_power) >= 2:
        scores["power_words"] = 20
        details["power_words"] = f"✅ Power words found: {', '.join(found_power[:3])}"
    elif len(found_power) == 1:
        scores["power_words"] = 12
        details["power_words"] = f"⚠️ Only 1 power word: {found_power[0]}"
    else:
        scores["power_words"] = 0
        details["power_words"] = "❌ No power words found — add words like 'Best', 'Ultimate', 'How to'"

    # 4. Emotional Trigger (0-15)
    found_emotion = [w for w in EMOTIONAL_TRIGGERS if w in title_lower]
    if found_emotion:
        scores["emotional_trigger"] = 15
        details["emotional_trigger"] = f"✅ Emotional triggers: {', '.join(found_emotion[:2])}"
    else:
        scores["emotional_trigger"] = 5
        details["emotional_trigger"] = "⚠️ No emotional triggers — consider adding curiosity gaps"

    # 5. Number/Year (0-10)
    has_year = bool(YEAR_PATTERN.search(title))
    has_number = bool(NUMBER_PATTERN.search(title))
    if has_year and has_number:
        scores["numbers"] = 10
        details["numbers"] = "✅ Contains both year and numbers"
    elif has_year or has_number:
        scores["numbers"] = 7
        details["numbers"] = "⚠️ Has year or number — adding both is better"
    else:
        scores["numbers"] = 0
        details["numbers"] = "❌ No numbers/year — titles with numbers get higher CTR"

    # 6. Special Characters & Formatting (0-10)
    has_separator = any(c in title for c in ['|', '—', '-', ':'])
    has_emoji = bool(re.search(r'[\U0001F600-\U0001F9FF\U00002702-\U000027B0]', title))
    format_score = 0
    if has_separator:
        format_score += 5
    if has_emoji:
        format_score += 3
    if title[0].isupper():
        format_score += 2
    scores["formatting"] = min(format_score, 10)
    details["formatting"] = f"{'✅' if format_score >= 7 else '⚠️'} Formatting score: {format_score}/10"

    total = sum(scores.values())

    return {
        "type": "title",
        "content": title,
        "primary_keyword": primary_keyword,
        "total_score": total,
        "max_score": 100,
        "breakdown": scores,
        "details": details,
    }


# ─── Description Scorer ──────────────────────────────────────────────────────

def score_description(description: str, primary_keyword: str) -> dict:
    """Score a YouTube video description for SEO optimization."""
    scores = {}
    details = {}
    desc_lower = description.lower()
    kw_lower = primary_keyword.lower()
    word_count = len(description.split())

    # 1. Keyword in first 150 chars (0-25)
    first_150 = desc_lower[:150]
    if kw_lower in first_150:
        scores["keyword_early"] = 25
        details["keyword_early"] = "✅ Primary keyword in first 150 characters"
    elif kw_lower in desc_lower[:300]:
        scores["keyword_early"] = 15
        details["keyword_early"] = "⚠️ Keyword found but not in first 150 chars"
    else:
        scores["keyword_early"] = 5
        details["keyword_early"] = "❌ Primary keyword missing from opening section"

    # 2. Keyword Density (0-20)
    kw_count = desc_lower.count(kw_lower)
    density = (kw_count * len(kw_lower.split())) / max(word_count, 1) * 100
    if 1.0 <= density <= 3.0:
        scores["keyword_density"] = 20
        details["keyword_density"] = f"✅ Keyword density: {density:.1f}% (ideal: 1-3%)"
    elif 0.5 <= density < 1.0 or 3.0 < density <= 5.0:
        scores["keyword_density"] = 12
        details["keyword_density"] = f"⚠️ Keyword density: {density:.1f}% (ideal: 1-3%)"
    else:
        scores["keyword_density"] = 5
        details["keyword_density"] = f"❌ Keyword density: {density:.1f}% — {'too low' if density < 0.5 else 'keyword stuffing!'}"

    # 3. Description Length (0-20)
    char_count = len(description)
    if 1000 <= char_count <= 5000:
        scores["length"] = 20
        details["length"] = f"✅ Good length ({char_count} chars, {word_count} words)"
    elif 500 <= char_count < 1000:
        scores["length"] = 12
        details["length"] = f"⚠️ Could be longer ({char_count} chars)"
    elif char_count < 500:
        scores["length"] = 5
        details["length"] = f"❌ Too short ({char_count} chars) — aim for 1000+"
    else:
        scores["length"] = 15
        details["length"] = f"⚠️ Very long ({char_count} chars) — good but ensure quality"

    # 4. Structure Elements (0-15)
    structure_score = 0
    has_timestamps = bool(re.search(r'\d+:\d+', description))
    has_links = bool(re.search(r'https?://', description))
    has_sections = description.count('\n\n') >= 3
    has_emoji = bool(re.search(r'[\U0001F600-\U0001F9FF\U00002702-\U000027B0🔹🔸📌✅❌⭐🎬📊]', description))

    if has_timestamps: structure_score += 4
    if has_links: structure_score += 3
    if has_sections: structure_score += 4
    if has_emoji: structure_score += 4
    scores["structure"] = min(structure_score, 15)
    struct_items = []
    if has_timestamps: struct_items.append("timestamps")
    if has_links: struct_items.append("links")
    if has_sections: struct_items.append("sections")
    if has_emoji: struct_items.append("emojis")
    details["structure"] = f"{'✅' if structure_score >= 10 else '⚠️'} Found: {', '.join(struct_items) if struct_items else 'none'}"

    # 5. CTA Presence (0-10)
    found_cta = [w for w in CTA_PHRASES if w in desc_lower]
    if len(found_cta) >= 2:
        scores["cta"] = 10
        details["cta"] = f"✅ CTAs found: {', '.join(found_cta[:3])}"
    elif len(found_cta) == 1:
        scores["cta"] = 5
        details["cta"] = f"⚠️ Only 1 CTA found — add more engagement prompts"
    else:
        scores["cta"] = 0
        details["cta"] = "❌ No CTA found — add subscribe/like/comment prompts"

    # 6. Hashtags (0-10)
    hashtags = re.findall(r'#\w+', description)
    if 3 <= len(hashtags) <= 5:
        scores["hashtags"] = 10
        details["hashtags"] = f"✅ {len(hashtags)} hashtags (ideal: 3-5)"
    elif 1 <= len(hashtags) <= 2 or 6 <= len(hashtags) <= 15:
        scores["hashtags"] = 5
        details["hashtags"] = f"⚠️ {len(hashtags)} hashtags — aim for 3-5"
    elif len(hashtags) > 15:
        scores["hashtags"] = 0
        details["hashtags"] = f"❌ {len(hashtags)} hashtags — YouTube ignores all if >15!"
    else:
        scores["hashtags"] = 0
        details["hashtags"] = "❌ No hashtags found"

    total = sum(scores.values())

    return {
        "type": "description",
        "primary_keyword": primary_keyword,
        "total_score": total,
        "max_score": 100,
        "word_count": word_count,
        "char_count": char_count,
        "keyword_count": kw_count,
        "keyword_density": round(density, 2),
        "breakdown": scores,
        "details": details,
    }


# ─── Tag Scorer ───────────────────────────────────────────────────────────────

def score_tags(tags_str: str, primary_keyword: str) -> dict:
    """Score YouTube tags for SEO."""
    scores = {}
    details = {}
    tags = [t.strip() for t in tags_str.split(',') if t.strip()]
    kw_lower = primary_keyword.lower()
    total_chars = len(tags_str)

    # 1. Tag count (0-25)
    tag_count = len(tags)
    if 20 <= tag_count <= 40:
        scores["count"] = 25
        details["count"] = f"✅ {tag_count} tags (ideal: 20-40)"
    elif 10 <= tag_count < 20 or 40 < tag_count <= 50:
        scores["count"] = 15
        details["count"] = f"⚠️ {tag_count} tags — aim for 20-40"
    else:
        scores["count"] = 5
        details["count"] = f"❌ {tag_count} tags — {'too few' if tag_count < 10 else 'too many'}"

    # 2. Character limit (0-20)
    if total_chars <= 500:
        scores["char_limit"] = 20
        details["char_limit"] = f"✅ {total_chars}/500 characters used"
    else:
        scores["char_limit"] = 5
        details["char_limit"] = f"❌ {total_chars}/500 — exceeds YouTube limit!"

    # 3. Primary keyword in tags (0-25)
    tags_lower = [t.lower() for t in tags]
    if kw_lower in tags_lower:
        scores["keyword_present"] = 25
        details["keyword_present"] = "✅ Exact primary keyword found in tags"
    elif any(kw_lower in t for t in tags_lower):
        scores["keyword_present"] = 18
        details["keyword_present"] = "⚠️ Primary keyword partially present"
    else:
        scores["keyword_present"] = 5
        details["keyword_present"] = "❌ Primary keyword missing from tags"

    # 4. Tag variety (0-15)
    avg_words = sum(len(t.split()) for t in tags) / max(len(tags), 1)
    short_tags = sum(1 for t in tags if len(t.split()) <= 2)
    long_tags = sum(1 for t in tags if len(t.split()) >= 3)
    if short_tags > 0 and long_tags > 0:
        scores["variety"] = 15
        details["variety"] = f"✅ Good mix: {short_tags} short + {long_tags} long-tail tags"
    else:
        scores["variety"] = 8
        details["variety"] = f"⚠️ Needs more variety (avg {avg_words:.1f} words/tag)"

    # 5. First tag is primary keyword (0-15)
    if tags_lower and kw_lower == tags_lower[0]:
        scores["first_tag"] = 15
        details["first_tag"] = "✅ First tag is the primary keyword"
    elif tags_lower and kw_lower in tags_lower[0]:
        scores["first_tag"] = 10
        details["first_tag"] = "⚠️ First tag contains primary keyword"
    else:
        scores["first_tag"] = 0
        details["first_tag"] = "❌ First tag should be your primary keyword"

    total = sum(scores.values())

    return {
        "type": "tags",
        "tag_count": tag_count,
        "total_chars": total_chars,
        "total_score": total,
        "max_score": 100,
        "breakdown": scores,
        "details": details,
    }


# ─── Full SEO Scorer ─────────────────────────────────────────────────────────

def score_full(title: str, description: str, tags: str, primary_keyword: str) -> dict:
    """Calculate full SEO score combining all elements."""
    title_result = score_title(title, primary_keyword)
    desc_result = score_description(description, primary_keyword)
    tags_result = score_tags(tags, primary_keyword)

    # Weighted scoring
    weights = {
        "title": 0.30,
        "description": 0.35,
        "tags": 0.20,
        "consistency": 0.15,
    }

    # Consistency check — are keywords aligned across all elements?
    kw_lower = primary_keyword.lower()
    consistency_score = 0
    if kw_lower in title.lower():
        consistency_score += 35
    if kw_lower in description.lower()[:200]:
        consistency_score += 35
    if any(kw_lower in t.lower() for t in tags.split(',')):
        consistency_score += 30

    weighted_total = (
        title_result["total_score"] * weights["title"] +
        desc_result["total_score"] * weights["description"] +
        tags_result["total_score"] * weights["tags"] +
        consistency_score * weights["consistency"]
    )

    return {
        "type": "full",
        "overall_score": round(weighted_total),
        "title_score": title_result["total_score"],
        "description_score": desc_result["total_score"],
        "tags_score": tags_result["total_score"],
        "consistency_score": consistency_score,
        "weights": weights,
        "title_details": title_result["details"],
        "description_details": desc_result["details"],
        "tags_details": tags_result["details"],
    }


# ─── Output Formatting ───────────────────────────────────────────────────────

def print_score_report(result: dict):
    """Print a formatted score report."""
    print("=" * 60)
    print(f"  📈 SEO SCORE REPORT — {result['type'].upper()}")
    print("=" * 60)

    if result["type"] == "full":
        grade = "🏆 Excellent" if result["overall_score"] >= 85 else \
                "✅ Good" if result["overall_score"] >= 70 else \
                "⚠️ Needs Work" if result["overall_score"] >= 50 else \
                "❌ Poor"

        print(f"\n  🎯 OVERALL SCORE: {result['overall_score']}/100 — {grade}")
        print()
        print(f"  ├── Title:       {result['title_score']}/100 (weight: 30%)")
        print(f"  ├── Description: {result['description_score']}/100 (weight: 35%)")
        print(f"  ├── Tags:        {result['tags_score']}/100 (weight: 20%)")
        print(f"  └── Consistency: {result['consistency_score']}/100 (weight: 15%)")
        print()

        for section, details in [
            ("TITLE", result["title_details"]),
            ("DESCRIPTION", result["description_details"]),
            ("TAGS", result["tags_details"]),
        ]:
            print(f"─── {section} DETAILS ─────────────────────────────")
            for key, value in details.items():
                print(f"  {value}")
            print()
    else:
        grade = "🏆 Excellent" if result["total_score"] >= 85 else \
                "✅ Good" if result["total_score"] >= 70 else \
                "⚠️ Needs Work" if result["total_score"] >= 50 else \
                "❌ Poor"

        print(f"\n  🎯 SCORE: {result['total_score']}/100 — {grade}")
        print()
        print("─── BREAKDOWN ────────────────────────────────────────")
        for key, value in result["details"].items():
            print(f"  {value}")
        print()

    print("─── JSON OUTPUT ──────────────────────────────────────")
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube SEO Scorer")
    parser.add_argument("--type", choices=["title", "description", "full"],
                        required=True, help="What to score")
    parser.add_argument("args", nargs="+", help="Content to score")

    args = parser.parse_args()

    if args.type == "title":
        if len(args.args) < 2:
            print("Usage: --type title \"<title>\" \"<primary_keyword>\"")
            sys.exit(1)
        result = score_title(args.args[0], args.args[1])

    elif args.type == "description":
        if len(args.args) < 2:
            print("Usage: --type description \"<description>\" \"<primary_keyword>\"")
            sys.exit(1)
        result = score_description(args.args[0], args.args[1])

    elif args.type == "full":
        if len(args.args) < 4:
            print("Usage: --type full \"<title>\" \"<description>\" \"<tags>\" \"<primary_keyword>\"")
            sys.exit(1)
        result = score_full(args.args[0], args.args[1], args.args[2], args.args[3])

    print_score_report(result)
