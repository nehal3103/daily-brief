import feedparser
import re

FEEDS = {
    # --- EDITORIALS & DEEP ANALYSIS ---
    "The Hindu Editorial": [
        "https://www.thehindu.com/opinion/editorial/feeder/default.rss",
        "https://www.thehindu.com/opinion/lead/feeder/default.rss",
        "https://www.thehindu.com/opinion/columns/feeder/default.rss",
    ],
    "The Wire": [
        "https://thewire.in/rss",
    ],
    "Project Syndicate": [
        "https://www.project-syndicate.org/rss",
    ],
    "Foreign Affairs": [
        "https://www.foreignaffairs.com/rss.xml",
    ],

    # --- GEOPOLITICS ---
    "Al Jazeera": [
        "https://www.aljazeera.com/xml/rss/all.xml",
    ],
    "BBC World": [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
    ],
    "Foreign Policy": [
        "https://foreignpolicy.com/feed/",
    ],
    "The Diplomat": [
        "https://thediplomat.com/feed/",
    ],

    # --- INDIA MARKETS & STOCKS ---
    "Economic Times Markets": [
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
    ],
    "Mint Markets": [
        "https://www.livemint.com/rss/markets",
        "https://www.livemint.com/rss/opinion",
    ],
    "Moneycontrol": [
        "https://www.moneycontrol.com/rss/marketreports.xml",
        "https://www.moneycontrol.com/rss/economy.xml",
    ],

    # --- MAJOR NATIONAL NEWS ---
    "The Hindu National": [
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://www.thehindu.com/business/feeder/default.rss",
    ],
    "Indian Express": [
        "https://indianexpress.com/section/india/feed/",
        "https://indianexpress.com/section/business/feed/",
    ],

    # --- TECH ---
    "TechCrunch": [
        "https://techcrunch.com/feed/",
    ],
    "MIT Technology Review": [
        "https://www.technologyreview.com/feed/",
    ],

    # --- SPORTS (headlines only) ---
    "Cricinfo": [
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    ],
    "BBC Sport": [
        "http://feeds.bbci.co.uk/sport/rss.xml",
    ],
}

# Which sources get AI briefs vs headlines only
HEADLINE_ONLY_SOURCES = {"Cricinfo", "BBC Sport"}

# Per-source article limits
SOURCE_LIMITS = {
    "The Hindu Editorial": 4,
    "The Wire": 2,
    "Project Syndicate": 2,
    "Foreign Affairs": 1,
    "Al Jazeera": 3,
    "BBC World": 2,
    "Foreign Policy": 2,
    "The Diplomat": 2,
    "Economic Times Markets": 3,
    "Mint Markets": 2,
    "Moneycontrol": 2,
    "The Hindu National": 2,
    "Indian Express": 2,
    "TechCrunch": 2,
    "MIT Technology Review": 1,
    "Cricinfo": 2,
    "BBC Sport": 1,
}

ALLOWED_KEYWORDS = {
    "The Hindu Editorial": [],       # Take everything from editorial feed — it's already filtered
    "The Wire": [],                  # Take everything
    "Project Syndicate": [],
    "Foreign Affairs": [],
    "Foreign Policy": [],
    "The Diplomat": [],

    "Al Jazeera": [
        "war", "conflict", "iran", "israel", "russia", "ukraine", "china",
        "nato", "nuclear", "sanctions", "diplomacy", "ceasefire", "airstrike",
        "middle east", "asia", "india", "pakistan", "trade", "economy",
    ],
    "BBC World": [
        "war", "conflict", "iran", "israel", "russia", "ukraine", "china",
        "election", "economy", "trade", "diplomacy", "nuclear", "climate",
    ],
    "Economic Times Markets": [
        "nifty", "sensex", "bse", "nse", "stock", "market", "rally", "selloff",
        "earnings", "results", "profit", "ipo", "fii", "rbi", "repo rate",
        "inflation", "gdp", "rupee", "dollar", "crude", "gold", "budget",
    ],
    "Mint Markets": [
        "nifty", "sensex", "market", "stock", "rbi", "inflation", "rupee",
        "earnings", "ipo", "rate", "economy", "budget", "fiscal",
    ],
    "Moneycontrol": [
        "nifty", "sensex", "market", "stock", "rbi", "rate", "rupee",
        "earnings", "economy", "inflation", "crude",
    ],
    "The Hindu National": [
        "government", "policy", "rbi", "budget", "economy", "parliament",
        "supreme court", "foreign policy", "india-china", "india-us",
        "infrastructure", "census", "defence", "trade", "bilateral",
    ],
    "Indian Express": [
        "government", "policy", "economy", "parliament", "supreme court",
        "rbi", "budget", "defence", "foreign", "bilateral", "infrastructure",
    ],
    "TechCrunch": [
        "ai", "artificial intelligence", "startup", "funding", "openai",
        "google", "apple", "meta", "microsoft", "antitrust", "regulation",
        "india", "acquisition", "ipo", "llm", "model",
    ],
    "MIT Technology Review": [
        "ai", "artificial intelligence", "machine learning", "regulation",
        "climate", "energy", "biotech", "policy", "research",
    ],
    "Cricinfo": [],   # Take all — it's already cricket only
    "BBC Sport": [
        "cricket", "football", "formula 1", "f1", "premier league",
        "world cup", "champions league",
    ],
}

BLOCKED_KEYWORDS = [
    # Crime & courts
    "murder", "rape", "theft", "robbery", "kidnap",
    "fir", "custody", "arrested", "convicted", "sentenced",

    # Entertainment
    "bollywood", "celebrity", "actor", "actress", "film", "movie",
    "reality show", "ott", "web series",

    # Local political noise
    "election rally", "bypoll", "ward election",
    "bjp vs", "congress vs",

    # Fluff
    "horoscope", "viral", "april fool", "trending",
    "blinkit", "zomato", "swiggy",
    "weather update", "price in your city",
    "quote of the day",
]


def is_relevant(source, title, summary=""):
    text = (title + " " + summary).lower()

    # Always block these regardless of source
    for word in BLOCKED_KEYWORDS:
        if word in text:
            return False

    # Sources with empty allowed list = take everything (already curated feeds)
    allowed = ALLOWED_KEYWORDS.get(source, [])
    if not allowed:
        return True

    # Otherwise match against allowed keywords
    for word in allowed:
        if word in text:
            return True

    return False


def fetch_articles():
    all_articles = []
    seen_titles = set()

    for source, urls in FEEDS.items():
        limit = SOURCE_LIMITS.get(source, 3)
        headline_only = source in HEADLINE_ONLY_SOURCES
        count = 0

        print(f"Fetching from {source}...")

        for url in urls:
            if count >= limit:
                break

            feed = feedparser.parse(url)

            if len(feed.entries) == 0:
                print(f"  WARNING: No entries at {url}")
                continue

            for entry in feed.entries:
                if count >= limit:
                    break

                title = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()
                link = entry.get("link", "")

                # Clean HTML tags
                summary = re.sub(r"<[^>]+>", "", summary)
                # Clean whitespace
                summary = re.sub(r'\s+', ' ', summary).strip()

                if not title:
                    continue

                if title in seen_titles:
                    continue

                if is_relevant(source, title, summary):
                    seen_titles.add(title)
                    all_articles.append({
                        "source": source,
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "headline_only": headline_only,
                        "summary_length": len(summary),
                    })
                    count += 1

    print(f"\nTotal relevant articles found: {len(all_articles)}")
    return all_articles


if __name__ == "__main__":
    articles = fetch_articles()
    for a in articles:
        tag = "[HEADLINE]" if a["headline_only"] else "[BRIEF]"
        print(f"\n{tag} [{a['source']}] {a['title']}")
        if a['summary']:
            print(f"  {a['summary'][:120]}...")
        else:
            print(f"  [No summary — {a['summary_length']} chars]")