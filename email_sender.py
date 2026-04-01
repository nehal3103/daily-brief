import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.environ.get("RESEND_API_KEY")

def send_email(html_content):
    from_email = os.environ.get("FROM_EMAIL", "onboarding@resend.dev")
    to_email = os.environ.get("TO_EMAIL")

    if not to_email:
        print("ERROR: TO_EMAIL not set in .env")
        return False

    from datetime import datetime
    date_str = datetime.now().strftime("%d %B %Y")
    subject = f"The Daily Brief — {date_str}"

    try:
        response = resend.Emails.send({
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "html": html_content,
        })
        print(f"Email sent successfully. ID: {response['id']}")
        return True

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


# Test it
if __name__ == "__main__":
    from rss_fetcher import fetch_articles
    from brief_generator import generate_all_briefs
    from email_builder import build_email_html

    print("Fetching articles...")
    articles = fetch_articles()

    print("Generating briefs...")
    briefs = generate_all_briefs(articles)

    print("Building email...")
    html = build_email_html(briefs)

    print("Sending email...")
    send_email(html)