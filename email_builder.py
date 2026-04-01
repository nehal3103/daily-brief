import re
from datetime import datetime


def build_email_html(briefs):
    date_str = datetime.now().strftime("%A, %d %B %Y")

    source_colors = {
        "The Hindu Editorial": "#e63946",
        "The Wire": "#c1121f",
        "Project Syndicate": "#6a4c93",
        "Foreign Affairs": "#1d3557",
        "Al Jazeera": "#8338ec",
        "BBC World": "#e76f51",
        "Foreign Policy": "#2d6a4f",
        "The Diplomat": "#1b4332",
        "Economic Times Markets": "#2a9d8f",
        "Mint Markets": "#457b9d",
        "Moneycontrol": "#0077b6",
        "The Hindu National": "#e63946",
        "Indian Express": "#d62828",
        "TechCrunch": "#f4a261",
        "MIT Technology Review": "#264653",
        "Cricinfo": "#006400",
        "BBC Sport": "#e76f51",
    }

    cards_html = ""

    for b in briefs:
        color = source_colors.get(b["source"], "#888888")

        if b.get("headline_only") or not b.get("brief"):
            # Compact headline card
            cards_html += f"""
            <div style="
                background: #ffffff;
                border-radius: 8px;
                padding: 16px 20px;
                margin-bottom: 12px;
                border-left: 4px solid {color};
            ">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="
                        background: {color};
                        color: white;
                        font-size: 10px;
                        font-weight: 700;
                        padding: 2px 8px;
                        border-radius: 20px;
                        text-transform: uppercase;
                        white-space: nowrap;
                    ">{b['source']}</span>
                    <span style="font-size: 14px; color: #1a1a2e;">{b['title']}</span>
                    <a href="{b['link']}" style="
                        color: {color};
                        font-size: 12px;
                        font-weight: 600;
                        text-decoration: none;
                        white-space: nowrap;
                        margin-left: auto;
                    ">Read →</a>
                </div>
            </div>
            """
            continue

        # Full brief card
        brief_html = b["brief"]
        brief_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', brief_html)
        brief_html = brief_html.replace('\n', '<br>')

        cards_html += f"""
        <div style="
            background: #ffffff;
            border-radius: 10px;
            padding: 28px 32px;
            margin-bottom: 24px;
            border-left: 5px solid {color};
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        ">
            <div style="margin-bottom: 10px;">
                <span style="
                    background: {color};
                    color: white;
                    font-size: 11px;
                    font-weight: 700;
                    padding: 3px 10px;
                    border-radius: 20px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">{b['source']}</span>
            </div>

            <h2 style="
                font-size: 18px;
                font-weight: 700;
                color: #1a1a2e;
                margin: 10px 0 16px 0;
                line-height: 1.4;
            ">{b['title']}</h2>

            <div style="
                font-size: 15px;
                color: #333;
                line-height: 1.8;
            ">{brief_html}</div>

            <div style="margin-top: 16px;">
                <a href="{b['link']}" style="
                    color: {color};
                    font-size: 13px;
                    font-weight: 600;
                    text-decoration: none;
                ">Read full article →</a>
            </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="
        margin: 0;
        padding: 0;
        background: #f0f2f5;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    ">
        <div style="max-width: 680px; margin: 0 auto; padding: 32px 16px;">

            <!-- Header -->
            <div style="
                background: #1a1a2e;
                border-radius: 12px;
                padding: 32px;
                margin-bottom: 28px;
                text-align: center;
            ">
                <h1 style="
                    color: #ffffff;
                    font-size: 28px;
                    font-weight: 800;
                    margin: 0 0 6px 0;
                    letter-spacing: -0.5px;
                ">The Daily Brief</h1>
                <p style="
                    color: #a0aec0;
                    font-size: 14px;
                    margin: 0;
                ">{date_str}</p>
                <p style="
                    color: #718096;
                    font-size: 12px;
                    margin: 8px 0 0 0;
                ">Geopolitics · Markets · Tech · Analysis · Sports</p>
            </div>

            <!-- Section: Full Briefs -->
            <div style="
                font-size: 11px;
                font-weight: 700;
                color: #888;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 16px;
                padding-left: 4px;
            ">Today's Deep Reads</div>

            {cards_html}

            <!-- Footer -->
            <div style="
                text-align: center;
                padding: 32px 24px;
                color: #999;
                font-size: 12px;
                line-height: 1.8;
            ">
                <p style="margin: 0;">Sources: The Hindu · Economic Times · Mint · Al Jazeera · BBC · Foreign Policy · The Diplomat · Project Syndicate · TechCrunch · MIT Tech Review · Cricinfo</p>
                <p style="margin: 8px 0 0 0;">Powered by Groq · Built by you</p>
            </div>

        </div>
    </body>
    </html>
    """

    return html


# Test — saves preview.html
if __name__ == "__main__":
    from rss_fetcher import fetch_articles
    from brief_generator import generate_all_briefs

    print("Fetching articles...")
    articles = fetch_articles()

    print("Generating briefs...")
    briefs = generate_all_briefs(articles)

    print("Building email...")
    html = build_email_html(briefs)

    with open("preview.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Done. Open preview.html in your browser.")