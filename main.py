from rss_fetcher import fetch_articles
from brief_generator import generate_all_briefs
from email_builder import build_email_html
from email_sender import send_email

def run():
    print("=== Daily Brief Pipeline Starting ===")

    print("\n[1/4] Fetching articles...")
    articles = fetch_articles()

    if not articles:
        print("No articles found. Exiting.")
        return

    print(f"\n[2/4] Generating briefs for {len(articles)} articles...")
    briefs = generate_all_briefs(articles)

    print("\n[3/4] Building email...")
    html = build_email_html(briefs)

    print("\n[4/4] Sending email...")
    send_email(html)

    print("\n=== Done ===")

if __name__ == "__main__":
    run()