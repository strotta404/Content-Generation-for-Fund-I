import os
import csv
import smtplib
import openai
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import re

# Load API Key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌ Error: API Key not found. Make sure it's set in environment variables.")
    exit()

openai.api_key = OPENAI_API_KEY

# Email credentials (Using app password)
EMAIL_USER = "STrotta@delcamcapital.com"
EMAIL_PASS = "cqsgvsprtsotzqql"

# Define businesses
businesses = {
    "PlasTech Machining": [],
    "PlasTech Molding": [],
    "New England Fabricated Metals": [],
    "DelCam Manufacturing": [],
    "Shortening Shuttle": []
}

### 🔹 Function to Clean OpenAI Markdown Formatting
def clean_markdown(text):
    """Converts Markdown-style text to properly formatted HTML for email readability."""
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)  # Convert **bold** to <strong>
    text = re.sub(r"### (.*?)\n", r"<h3>\1</h3>\n", text)  # Convert ### Headers to <h3>
    text = re.sub(r"## (.*?)\n", r"<h2>\1</h2>\n", text)  # Convert ## Headers to <h2>
    text = re.sub(r"# (.*?)\n", r"<h1>\1</h1>\n", text)  # Convert # Headers to <h1>
    text = text.replace("\n", "<br><br>")  # Ensure proper spacing
    return text.strip()

### 🔹 Get New Topic from CSV or Generate More Topics
def get_new_topic(company):
    """Retrieve the first pending topic from the CSV file, and generate new topics if needed."""
    filename = f"{company.replace(' ', '_')}_topics.csv"

    if not os.path.exists(filename):
        print(f"⚠️ No topic list found for {company}. Generating new topics.")
        generate_new_topics(company)

    # Read topics from CSV
    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        topics = [row[0] for row in reader if row]

    if len(topics) < 5:
        print(f"🔄 Less than 5 topics left for {company}. Generating more...")
        generate_new_topics(company)

    return topics[0] if topics else "Placeholder Topic"

### 🔹 Generate AI-Written Blog Post
def generate_article(company, topic):
    """Generate a human-like, engaging blog post."""
    print(f"📝 Generating article on '{topic}' for {company}...")

    prompt = f"""
    Write a 500-word blog post for {company} on '{topic}' in a natural, engaging style.

    - Start with a strong hook or real-world example.
    - Use smooth transitions to connect ideas.
    - Write as if a professional human writer crafted it.
    - Use well-structured paragraphs and no excessive bullet points.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700
        )
        article = response.choices[0].message.content.strip()
        return clean_markdown(article)  # Clean Markdown formatting before returning

    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return None

### 🔹 Generate AI-Based Social Media Posts
def generate_social_posts(company, topic, article):
    """Generate social media posts for LinkedIn, Twitter, Facebook, and Instagram."""
    print(f"📢 Generating social media posts for {company}...")

    prompt = f"""
    Create engaging social media posts for {company} based on the blog topic '{topic}'.

    Provide separate posts for:
    - LinkedIn (Max 700 characters)
    - Twitter (Max 280 characters)
    - Facebook (Max 2,200 characters)
    - Instagram (Max 2,200 characters)

    Blog content for reference:
    {article}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        post_text = response.choices[0].message.content.split("\n\n")

        return {
            "LinkedIn": post_text[0][:700] if len(post_text) > 0 else f"Read our latest blog: {topic} [Link]",
            "Twitter": post_text[1][:280] if len(post_text) > 1 else f"{topic} - Discover more here! [Link]",
            "Facebook": post_text[2][:2200] if len(post_text) > 2 else f"We just published a new article: {topic}. Read more here! [Link]",
            "Instagram": post_text[3][:2200] if len(post_text) > 3 else f"Exciting updates from {company}! Read the latest here: [Link]"
        }

    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return None

### 🔹 Send Email for Approval
def send_to_approver(company, topic, article, social_posts):
    """Send an email for approval including blog & social media drafts."""
    print(f"📧 Sending approval email for {company}...")

    approver_email = "STrotta@delcamcapital.com"
    msg = MIMEMultipart()
    msg["Subject"] = f"Approval Required: {company} Blog & Social Media"
    msg["From"] = EMAIL_USER
    msg["To"] = approver_email

    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.5; color: #333;">
        <h2 style="color: #2C3E50;">{topic}</h2>
        <p>{article}</p>

        <h3 style="color: #2980B9;">📢 Social Media Drafts</h3>
        <strong>LinkedIn:</strong> <p>{social_posts['LinkedIn']}</p>
        <strong>Twitter:</strong> <p>{social_posts['Twitter']}</p>
        <strong>Facebook:</strong> <p>{social_posts['Facebook']}</p>
        <strong>Instagram:</strong> <p>{social_posts['Instagram']}</p>

        <p style="font-style: italic;">Reply 'yes' to approve or provide edits.</p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
    
    print(f"✅ Approval email sent for {company}.")

### 🔹 Main Workflow
for company in businesses.keys():
    topic = get_new_topic(company)
    article = generate_article(company, topic)
    social_posts = generate_social_posts(company, topic, article)
    send_to_approver(company, topic, article, social_posts)

print("\n✅ All tasks completed.")
