
import snscrape.modules.twitter as sntwitter
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import os

# --- CONFIG ---
USERNAMES = ["Bundestag","KuehniKev","DietmarBartsch","Alice_Weidel","Markus_Soeder","elonmusk", "JDVance", "mattgaetz","TuckerCarlson","WashingtonPost","POLITICO","PeteHegseth","RobertKennedyJr","benshapiro","jordanbpeterson","Trevornoah","AOC","SWagenknecht","POTUS"]  # 👈 Add Twitter handles here
KEYWORDS = ["Europe", "Germany", "crypto", "Russia", "Ukraine", "war", "NATO", "Putin", "Trump","Merz","renewables","Erneuerbare","Russland"]  # 👈 Add keywords here
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_PROVIDER = os.environ["EMAIL_PROVIDER"]  # "gmail" or "outlook"

def collect_tweets():
    since = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    matches = []

    for username in USERNAMES:
        for tweet in sntwitter.TwitterUserScraper(username).get_items():
            if str(tweet.date.date()) < since:
                break
            if any(keyword.lower() in tweet.content.lower() for keyword in KEYWORDS):
                matches.append({
                    "user": username,
                    "text": tweet.content,
                    "date": tweet.date.strftime('%Y-%m-%d %H:%M'),
                    "url": f"https://twitter.com/{username}/status/{tweet.id}"
                })
    return matches

def send_email(matches):
    if not matches:
        return

    msg = EmailMessage()
    msg['Subject'] = "🕵️ Daily Twitter Keyword Alert"
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    text_content = "Here are today's matching tweets:\n\n"
    for m in matches:
        text_content += f"🔹 @{m['user']} — {m['date']}\n{m['text']}\n{m['url']}\n\n"
    msg.set_content(text_content)

    html_content = """\
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.5;">
        <h2>🕵️ Daily Twitter Keyword Alert</h2>
        <p>Here are the tweets matching your keywords in the last 24 hours:</p>
        <ul style="padding-left: 0;">
    """
    for m in matches:
        html_content += f"""\
          <li style="margin-bottom: 20px; list-style: none; border-bottom: 1px solid #ddd; padding-bottom: 10px;">
            <strong>@{m['user']}</strong> — <em>{m['date']}</em><br>
            <p style="margin: 8px 0;">{tweet_text}</p>
            <a href="{m['url']}">View Tweet</a>
          </li>
        """
    html_content += """\
        </ul>
        <p style="font-size: 0.9em; color: gray;">Bot by your friendly shadow agent 🤖</p>
      </body>
    </html>
    """

    msg.add_alternative(html_content, subtype='html')

    if EMAIL_PROVIDER.lower() == "gmail":
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
            smtp.send_message(msg)
    elif EMAIL_PROVIDER.lower() == "outlook":
        with smtplib.SMTP('smtp.office365.com', 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
            smtp.send_message(msg)
    else:
        raise ValueError("Unknown email provider. Use 'gmail' or 'outlook'.")

# --- RUN ---
tweets = collect_tweets()
send_email(tweets)
