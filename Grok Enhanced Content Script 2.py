import os
import csv
import smtplib
import openai
import requests
import gspread
import pandas as pd
from gspread_dataframe import set_with_dataframe
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import re
import random

# OpenAI API key
openai.api_key = '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'  # Replace with your new key

# OAuth 2.0 credentials
CLIENT_SECRET_FILE = r'C:\Users\Stephen\AppData\Local\Programs\Python\Python313\DelCam Content Workflow\client_secret_964739878276-3omdt4pej3mmp67g13s0d8nrj983kdb1.apps.googleusercontent.com.json'
TOKEN_FILE = 'token.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Authenticate
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
else:
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())

print("Active Scopes:", creds.scopes if creds else "None")
if not creds or not creds.valid:
    print("Credentials invalid!")
    exit()

client = gspread.authorize(creds)
GOOGLE_SHEET_ID = "1kBG0mlITGaB5ubgp84jtmayMuSLEAucsMuEfZZUynSw"
EMAIL_USER = "STrotta@delcamcapital.com"
EMAIL_PASS = "cqsgvsprtsotzqql"

businesses = {
    "PlasTech Machining": [],
    "PlasTech Molding": [],
    "New England Fabricated Metals": [],
    "DelCam Manufacturing": [],
    "Shortening Shuttle": []
}

def clean_markdown(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"### (.*?)\n", r"<h3>\1</h3>\n", text)
    text = re.sub(r"## (.*?)\n", r"<h2>\1</h2>\n", text)
    text = re.sub(r"# (.*?)\n", r"<h1>\1</h1>\n", text)
    text = text.replace("\n", "<br><br>")
    return text.strip()

def generate_new_topics(company):
    filename = f"{company.replace(' ', '_')}_topics.csv"
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([f"Sample Topic 1 for {company}"])
        writer.writerow([f"Sample Topic 2 for {company}"])
        writer.writerow([f"Sample Topic 3 for {company}"])
    print(f"📋 Generated placeholder topics for {company}.")

def get_new_topic(company):
    filename = f"{company.replace(' ', '_')}_topics.csv"
    if not os.path.exists(filename):
        print(f"⚠️ No topic list found for {company}. Generating new topics.")
        generate_new_topics(company)
    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        topics = [row[0] for row in reader if row]
    if len(topics) < 5:
        print(f"🔄 Less than 5 topics left for {company}. Generating more...")
        generate_new_topics(company)
        with open(filename, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            topics = [row[0] for row in reader if row]
    return topics[0] if topics else "Placeholder Topic"

def generate_article(company, topic):
    print(f"📝 Generating article on '{topic}' for {company}...")
    if company == "Shortening Shuttle":
        content_types = [
            {
                "type": "Blog Post",
                "prompt": f"Write a 500-word blog post for Shortening Shuttle on '{topic}' related to the used cooking oil industry. Focus on restaurant safety, safe transportation of used cooking oil, or oil filtration innovations like the BOSS (Battery Operated Shortening Shuttle), the first battery-powered oil filtration system. Start with a real-world kitchen scenario, use a professional tone, and emphasize safety or efficiency benefits.",
                "max_tokens": 700
            },
            {
                "type": "Quick Tips",
                "prompt": f"Write a 200-word article for Shortening Shuttle on '{topic}' with 3 quick, actionable tips for restaurant staff on safely handling used cooking oil or improving filtration with tools like the BOSS. Keep it concise, practical, and in a friendly tone.",
                "max_tokens": 300
            },
            {
                "type": "Listicle",
                "prompt": f"Write a 400-word listicle for Shortening Shuttle on '{topic}' titled '5 Ways to Enhance Restaurant Safety with Used Cooking Oil Management'. Include points about safe transport, filtration (mention the BOSS where relevant), and spill prevention. Start with a short intro, use a numbered list, and keep it engaging.",
                "max_tokens": 500
            }
        ]
    else:
        content_types = [
            {
                "type": "Blog Post",
                "prompt": f"Write a 500-word blog post for {company} on '{topic}' in a natural, engaging style. Start with a strong hook or real-world example. Use smooth transitions. Write as a professional human writer with well-structured paragraphs, no excessive bullet points.",
                "max_tokens": 700
            },
            {
                "type": "Quick Tips",
                "prompt": f"Write a 200-word article for {company} on '{topic}' with 3 quick, actionable tips. Keep it concise, engaging, and practical, written in a friendly tone.",
                "max_tokens": 300
            },
            {
                "type": "Listicle",
                "prompt": f"Write a 400-word listicle for {company} on '{topic}' titled '5 Ways {topic}'. Make it engaging, with a short intro and 5 numbered points, each with a brief explanation.",
                "max_tokens": 500
            }
        ]
    choice = random.choice(content_types)
    prompt = f"{choice['prompt']}\n- Suggest a simple image idea to pair with this content (e.g., 'A photo of a CNC machine in action' or 'A restaurant worker using the BOSS filtration system'). Return it after the article text, separated by 'Image Idea:'."
    print(f"📝 Content Type: {choice['type']}")
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=choice['max_tokens'] + 100  # Extra for image idea
        )
        full_text = response.choices[0].message.content.strip()
        if "Image Idea:" in full_text:
            article, image_idea = full_text.split("Image Idea:", 1)
            article = clean_markdown(article.strip())
            image_idea = image_idea.strip()
        else:
            article = clean_markdown(full_text)
            image_idea = "No image idea provided."
        return article, image_idea
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return f"Sample {choice['type']} content due to API error.", "Sample image idea"

def generate_social_posts(company, topic, article):
    print(f"📢 Generating social media posts for {company}...")
    if company == "Shortening Shuttle":
        prompt = f"""
        Create engaging social media posts for Shortening Shuttle based on the topic '{topic}' in the used cooking oil industry.
        Focus on restaurant safety, safe oil transport, or filtration (e.g., BOSS system).
        Provide separate posts for:
        - LinkedIn (Max 700 characters)
        - Twitter (Max 280 characters)
        - Facebook (Max 2,200 characters)
        - Instagram (Max 2,200 characters)
        - X (Max 280 characters)
        - YouTube (Max 5,000 characters, as a video description)
        Content for reference:
        {article}
        """
    else:
        prompt = f"""
        Create engaging social media posts for {company} based on the topic '{topic}'.
        Provide separate posts for:
        - LinkedIn (Max 700 characters)
        - Twitter (Max 280 characters)
        - Facebook (Max 2,200 characters)
        - Instagram (Max 2,200 characters)
        - X (Max 280 characters)
        - YouTube (Max 5,000 characters, as a video description)
        Content for reference:
        {article}
        """
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700
        )
        post_text = response.choices[0].message.content.split("\n\n")
        return {
            "LinkedIn": post_text[0][:700] if len(post_text) > 0 else f"Read our latest: {topic} [Link]",
            "Twitter": post_text[1][:280] if len(post_text) > 1 else f"{topic} - More here! [Link]",
            "Facebook": post_text[2][:2200] if len(post_text) > 2 else f"New post: {topic}. [Link]",
            "Instagram": post_text[3][:2200] if len(post_text) > 3 else f"Updates from {company}! [Link]",
            "X": post_text[4][:280] if len(post_text) > 4 else f"{topic} on X - Check it out! [Link]",
            "YouTube": post_text[5][:5000] if len(post_text) > 5 else f"New video on {topic} by {company}. Subscribe! [Link]"
        }
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return {
            "LinkedIn": "Sample", "Twitter": "Sample", "Facebook": "Sample",
            "Instagram": "Sample", "X": "Sample", "YouTube": "Sample"
        }

def save_to_google_sheets(company, topic, article, social_posts, image_idea):
    print(f"📊 Saving content for {company} to Google Sheets...")
    sheet = client.open_by_key(GOOGLE_SHEET_ID)
    try:
        worksheet = sheet.worksheet("Varied Content")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title="Varied Content", rows=100, cols=12)
        worksheet.append_row(["Company", "Topic", "Article", "LinkedIn Post", "Twitter Post",
                              "Facebook Post", "Instagram Post", "X Post", "YouTube Post",
                              "Image Idea", "Timestamp"])
    df = pd.DataFrame([{
        "Company": company,
        "Topic": topic,
        "Article": article,
        "LinkedIn Post": social_posts["LinkedIn"],
        "Twitter Post": social_posts["Twitter"],
        "Facebook Post": social_posts["Facebook"],
        "Instagram Post": social_posts["Instagram"],
        "X Post": social_posts["X"],
        "YouTube Post": social_posts["YouTube"],
        "Image Idea": image_idea,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    set_with_dataframe(worksheet, df, include_column_header=False, resize=True, row=len(worksheet.get_all_values()) + 1)
    print(f"✅ Google Sheet updated for {company}.")

def send_to_approver(company, topic, article, social_posts, image_idea):
    print(f"📧 Sending approval email for {company}...")
    approver_email = "STrotta@delcamcapital.com"
    msg = MIMEMultipart()
    msg["Subject"] = f"Approval Required: {company} Content & Social Media"
    msg["From"] = EMAIL_USER
    msg["To"] = approver_email
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.5; color: #333;">
        <h2>{topic}</h2>
        <p>{article}</p>
        <h3>📢 Social Media Drafts</h3>
        <strong>LinkedIn:</strong> <p>{social_posts['LinkedIn']}</p>
        <strong>Twitter:</strong> <p>{social_posts['Twitter']}</p>
        <strong>Facebook:</strong> <p>{social_posts['Facebook']}</p>
        <strong>Instagram:</strong> <p>{social_posts['Instagram']}</p>
        <strong>X:</strong> <p>{social_posts['X']}</p>
        <strong>YouTube:</strong> <p>{social_posts['YouTube']}</p>
        <h3>🖼️ Image Idea</h3>
        <p>{image_idea}</p>
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

for company in businesses.keys():
    topic = get_new_topic(company)
    article, image_idea = generate_article(company, topic)
    social_posts = generate_social_posts(company, topic, article)
    save_to_google_sheets(company, topic, article, social_posts, image_idea)
    send_to_approver(company, topic, article, social_posts, image_idea)

print("\n✅ All tasks completed.")
