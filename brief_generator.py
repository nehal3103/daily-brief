import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_brief(article):
    title = article["title"]
    summary = article.get("summary", "").strip()
    source = article["source"]
    summary_length = article.get("summary_length", 0)

    # If summary is too thin, don't risk hallucination
    # Just return a clean "read more" card
    if summary_length < 30:
        return None

    content_input = f"Title: {title}\nSummary: {summary}"

    prompt = f"""
You are a senior analyst at a world affairs think tank. You write a daily brief for a smart, curious Indian reader who wants to genuinely understand the world — not just headlines.

RULES:
- Use the article as your anchor for what happened and when
- Freely use your own knowledge to explain background, history, and context — this is expected and required
- Never invent specific quotes, casualty numbers, or data points not present in the article
- If a number or claim is from your knowledge (not the article), do not present it as if it came from the article
- Write like you are explaining to a smart friend over coffee — not like a textbook

STRUCTURE — follow exactly:

**What happened:**
2-3 sentences. Specific. What is the news, who is involved, what changed.

**The background — why this matters now:**
4-5 sentences. This is the most important section. Use your knowledge freely here. What is the history behind this? What has been building up to this moment? What are the key tensions, relationships, or dynamics at play? Give the reader real context they won't get from just reading the headline.

**Why it matters:**
2-3 sentences. Concrete impact — on India, global trade, energy, geopolitics, or markets. Only connect to India when the connection is genuine. Do not force it.

**Key terms:**
Only include this section if there are genuinely technical terms (treaties, financial instruments, geopolitical concepts) a layman would not know. If none, skip this section entirely — do not write "None needed."

Article:
{content_input}
Source: {source}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Groq error for '{title}': {e}")
        return None


def generate_all_briefs(articles, delay=2):
    briefs = []

    for i, article in enumerate(articles):
        print(f"[{i+1}/{len(articles)}] Processing: {article['title'][:60]}...")

        # Sports or headline-only sources
        if article.get("headline_only"):
            briefs.append({
                "source": article["source"],
                "title": article["title"],
                "link": article["link"],
                "brief": None,
                "headline_only": True,
            })
            continue

        brief = generate_brief(article)

        briefs.append({
            "source": article["source"],
            "title": article["title"],
            "link": article["link"],
            "brief": brief,
            "headline_only": brief is None,  # thin summary = show as headline
        })

        time.sleep(delay)

    print(f"\nDone. Full briefs: {sum(1 for b in briefs if not b['headline_only'])} | Headlines: {sum(1 for b in briefs if b['headline_only'])}")
    return briefs

# Test it
if __name__ == "__main__":
    from rss_fetcher import fetch_articles

    articles = fetch_articles(max_per_source=2)  # Small test — 2 per source
    briefs = generate_all_briefs(articles)

    for b in briefs:
        print(f"\n{'='*60}")
        print(f"[{b['source']}] {b['title']}")
        print(f"{'='*60}")
        print(b["brief"])