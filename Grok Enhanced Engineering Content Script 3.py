import os
import csv
import smtplib
import random
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
import gspread
import pandas as pd
from gspread_dataframe import set_with_dataframe
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import re

# OpenAI client
client = OpenAI(api_key="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")

# Google Sheets OAuth
CLIENT_SECRET_FILE = r'C:\Users\Stephen\AppData\Local\Programs\Python\Python313\DelCam Content Workflow\client_secret_964739878276-3omdt4pej3mmp67g13s0d8nrj983kdb1.apps.googleusercontent.com.json'
TOKEN_FILE = 'token.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
GOOGLE_SHEET_ID = "1kBG0mlITGaB5ubgp84jtmayMuSLEAucsMuEfZZUynSw"
EMAIL_USER = "STrotta@delcamcapital.com"
EMAIL_PASS = "cqsgvsprtsotzqql"

if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
else:
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())

gspread_client = gspread.authorize(creds)

# Businesses
businesses = {
    "PlasTech Machining": [],
    "PlasTech Molding": [],
    "New England Fabricated Metals": [],
    "DelCam Manufacturing": [],
    "Shortening Shuttle": []
}

# Clean Markdown for HTML
def clean_markdown(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"### (.*?)\n", r"<h3>\1</h3>\n", text)
    text = re.sub(r"## (.*?)\n", r"<h2>\1</h2>\n", text)
    text = re.sub(r"# (.*?)\n", r"<h1>\1</h1>\n", text)
    text = text.replace("\n", "<br><br>")
    return text.strip()

# Generate engineering-focused topics
def generate_new_topics(company):
    filename = f"{company.replace(' ', '_')}_eng_topics.csv"
    if os.path.exists(filename):
        return  # Skip if topics exist
    if company == "Shortening Shuttle":
        prompt = f"Generate 10 specific, practical topics for Shortening Shuttle aimed at restaurant engineers and managers. Focus on operational capabilities like safe oil transport, filtration systems (e.g., BOSS), and compliance needs. Example: 'Optimizing Oil Filtration with BOSS for High-Volume Kitchens'."
    else:
        prompt = f"Generate 10 detailed, engineering-focused topics for {company} targeting an engineering audience. Focus on fabrication capabilities, customer needs (e.g., tolerances, materials), and services. Include specifics like dimensional requirements (e.g., ±0.005” tolerances) and material options (e.g., ABS, stainless steel). Example: 'Achieving ±0.005” Tolerances in CNC Machining with PlasTech Machining'."
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    topics = response.choices[0].message.content.split("\n")[:10]
    topics = [t.strip() for t in topics if t.strip()]
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for topic in topics:
            writer.writerow([topic, "pending"])
    print(f"📋 Generated engineering topics for {company}.")

# Get next topic
def get_new_topic(company):
    filename = f"{company.replace(' ', '_')}_eng_topics.csv"
    if not os.path.exists(filename):
        generate_new_topics(company)
    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        topics = [row for row in reader if row and len(row) > 1]
    for topic in topics:
        if topic[1] == "pending":
            return topic[0]
    generate_new_topics(company)  # Regenerate if no pending topics
    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        topics = [row for row in reader if row and len(row) > 1]
    return topics[0][0] if topics else "Placeholder Engineering Topic"

# Generate engineering article
def generate_article(company, topic):
    print(f"📝 Generating engineering article on '{topic}' for {company}...")
    if company == "Shortening Shuttle":
        prompt = f"Write a 750-word article for Shortening Shuttle on '{topic}' for restaurant engineers. Focus on operational capabilities (e.g., BOSS filtration, oil transport safety), specific needs (e.g., 50-gallon capacity, spill prevention), and benefits (e.g., uptime, compliance). Start with a real-world scenario, use a technical yet engaging tone, and include practical details."
    else:
        prompt = f"Write a 750-word article for {company} on '{topic}' for an engineering audience. Detail fabrication capabilities (e.g., CNC machining, molding, laser cutting), customer needs (e.g., tolerances like ±0.005”, material specs like ABS or 304 stainless steel), and services (e.g., prototyping, high-volume production). Include technical details, a real-world example, and actionable insights. Use a professional, engineering-focused tone."
    prompt += "\nSuggest a technical image idea (e.g., 'Cross-section of a CNC-machined part showing tolerances'). Return it after the article, separated by 'Image Idea:'."
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000  # ~750 words + image idea
        )
        full_text = response.choices[0].message.content.strip()
        article, image_idea = full_text.split("Image Idea:", 1) if "Image Idea:" in full_text else (full_text, "No image idea provided.")
        return clean_markdown(article.strip()), image_idea.strip()
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return "Sample engineering content due to API error.", "Sample image"

# Generate social posts (unchanged)
def generate_social_posts(company, topic, article):
    prompt = f"Create engineering-focused social media posts for {company} on '{topic}'. Use the article for reference:\n{article}\nProvide posts for LinkedIn (700 char), Twitter (280 char), Facebook (2200 char), Instagram (2200 char), X (280 char), YouTube (5000 char, video description)."
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700
        )
        post_text = response.choices[0].message.content.split("\n\n")
        return {
            "LinkedIn": post_text[0][:700] if len(post_text) > 0 else f"Explore {topic} [Link]",
            "Twitter": post_text[1][:280] if len(post_text) > 1 else f"{topic} insights [Link]",
            "Facebook": post_text[2][:2200] if len(post_text) > 2 else f"New: {topic} [Link]",
            "Instagram": post_text[3][:2200] if len(post_text) > 3 else f"{company} tech [Link]",
            "X": post_text[4][:280] if len(post_text) > 4 else f"{topic} on X [Link]",
            "YouTube": post_text[5][:5000] if len(post_text) > 5 else f"Video: {topic} [Link]"
        }
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return {k: "Sample" for k in ["LinkedIn", "Twitter", "Facebook", "Instagram", "X", "YouTube"]}

# Save to Google Sheets with new tab
def save_to_google_sheets(company, topic, article, social_posts, image_idea):
    print(f"📊 Saving to Google Sheets for {company}...")
    sheet = gspread_client.open_by_key(GOOGLE_SHEET_ID)
    try:
        worksheet = sheet.worksheet("Engineering Content")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title="Engineering Content", rows=100, cols=12)
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
    print(f"✅ Saved to 'Engineering Content' tab for {company}.")

# Send email (unchanged)
def send_to_approver(company, topic, article, social_posts, image_idea):
    print(f"📧 Sending approval email for {company}...")
    approver_email = "STrotta@delcamcapital.com"
    msg = MIMEMultipart()
    msg["Subject"] = f"Approval: {company} Engineering Content"
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

# Main workflow
for company in businesses.keys():
    topic = get_new_topic(company)
    article, image_idea = generate_article(company, topic)
    social_posts = generate_social_posts(company, topic, article)
    save_to_google_sheets(company, topic, article, social_posts, image_idea)
    send_to_approver(company, topic, article, social_posts, image_idea)

print("\n✅ Engineering content workflow completed.")
