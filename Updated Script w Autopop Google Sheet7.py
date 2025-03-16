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

# OpenAI API key
openai.api_key = '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'

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
        return clean_markdown(article)
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return "Sample article content due to API error."

def generate_social_posts(company, topic, article):
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
            "Twitter": post_text[1][:280] if len(post_text) > 1 else f"{topic} - Discover more! [Link]",
            "Facebook": post_text[2][:2200] if len(post_text) > 2 else f"We just published: {topic}. Read more! [Link]",
            "Instagram": post_text[3][:2200] if len(post_text) > 3 else f"Exciting updates from {company}! [Link]"
        }
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return {"LinkedIn": "Sample", "Twitter": "Sample", "Facebook": "Sample", "Instagram": "Sample"}

def save_to_google_sheets(company, topic, article, social_posts):
    print(f"📊 Saving content for {company} to Google Sheets...")
    sheet = client.open_by_key(GOOGLE_SHEET_ID)
    try:
        worksheet = sheet.worksheet("Content Output")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title="Content Output", rows=100, cols=10)
        worksheet.append_row(["Company", "Topic", "Article", "LinkedIn Post", "Twitter Post", "Facebook Post", "Instagram Post", "Timestamp"])
    df = pd.DataFrame([{
        "Company": company,
        "Topic": topic,
        "Article": article,
        "LinkedIn Post": social_posts["LinkedIn"],
        "Twitter Post": social_posts["Twitter"],
        "Facebook Post": social_posts["Facebook"],
        "Instagram Post": social_posts["Instagram"],
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    set_with_dataframe(worksheet, df, include_column_header=False, resize=True, row=len(worksheet.get_all_values()) + 1)
    print(f"✅ Google Sheet updated for {company}.")

def send_to_approver(company, topic, article, social_posts):
    print(f"📧 Sending approval email for {company}...")
    approver_email = "STrotta@delcamcapital.com"
    msg = MIMEMultipart()
    msg["Subject"] = f"Approval Required: {company} Blog & Social Media"
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
    article = generate_article(company, topic)
    social_posts = generate_social_posts(company, topic, article)
    save_to_google_sheets(company, topic, article, social_posts)
    send_to_approver(company, topic, article, social_posts)

print("\n✅ All tasks completed.")
